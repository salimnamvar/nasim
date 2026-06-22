# Resource-Oriented Design (RoD) Patterns

Patterns derived from Google AIPs for designing resource-oriented APIs mapped to sequence diagrams.

## Table of Contents

1. [Resource Naming (AIP-122)](#resource-naming)
2. [Resource Types (AIP-123)](#resource-types)
3. [Standard Methods](#standard-methods)
   - [Get (AIP-131)](#get-aip-131)
   - [List (AIP-132)](#list-aip-132)
   - [Create (AIP-133)](#create-aip-133)
   - [Update (AIP-134)](#update-aip-134)
   - [Delete (AIP-135)](#delete-aip-135)
4. [Custom Methods (AIP-136)](#custom-methods-aip-136)
5. [Pagination (AIP-158)](#pagination-aip-158)
6. [Errors (AIP-193)](#errors-aip-193)
7. [Field Behavior (AIP-203)](#field-behavior-aip-203)
8. [State Management (AIP-216)](#state-management-aip-216)

---

## Resource Naming (AIP-122)

### Resource Name Format

Resource names follow URI path schema without leading slash:

```
collectionId/resourceId/collectionId/resourceId/...
```

Rules:
- Collection identifiers = plural noun, camelCase (e.g., `publishers`, `books`, `orderItems`)
- Resource IDs = string, no uppercase (e.g., `123`, `les-miserables`)
- Separator = `/`
- Resources expose a `name` field containing the full resource name
- Resources may expose `uid` (system-generated unique ID) as OUTPUT_ONLY

### Examples

| Resource | Name |
|----------|------|
| Publisher | `publishers/123` |
| Book | `publishers/123/books/les-miserables` |
| User | `users/vhugo1802` |

### Full Resource Name (cross-API)

```
//library.googleapis.com/publishers/123/books/les-miserables
```

### Sequence Diagram Note

Use resource names in full form in messages:

```plantuml
Client -> Controller: GET /v1/publishers/123/books/les-miserables
Controller -> Service: getBook(name="publishers/123/books/les-miserables")
Service -> Repository: findByName("publishers/123/books/les-miserables")
```

---

## Resource Types (AIP-123)

Each resource has a type string in format:

```
{serviceName}.googleapis.com/{resourceMessageName}
```

Example: `library.googleapis.com/Book`

---

## Standard Methods

### Get (AIP-131)

**HTTP**: `GET /v1/{name=resourcePattern}`

**Rules**:
- URI has single variable field `name`
- No request body
- Returns full resource or partial response (AIP-157)
- Errors: NOT_FOUND if resource doesn't exist, PERMISSION_DENIED if no access

**Sequence Diagram Pattern**:

```plantuml
actor Client
participant "BookController" as C
participant "BookService" as S
participant "BookRepository" as R
database "Database" as DB

Client -> C: GET /v1/publishers/123/books/456
activate C

C -> S: getBook(name="publishers/123/books/456")
activate S

S -> R: findByName("publishers/123/books/456")
activate R
R -> DB: SELECT * FROM books WHERE ...
activate DB
DB --> R: BookEntity (or null)
deactivate DB
R --> S: Optional<BookEntity>
deactivate R

alt Book not found
    S --> C: throw NOT_FOUND
    C --> Client: 404 Not Found
        { "error": { "code": 5, "message": "Book not found" } }
else Book found
    S -> S: entity → BookResponseDTO
    S --> C: BookResponseDTO
    C --> Client: 200 OK + BookResponseDTO
end
deactivate S
deactivate C
```

---

### List (AIP-132)

**HTTP**: `GET /v1/{parent=parentPattern}/collectionId`

**Rules**:
- Supports pagination (page_size, page_token)
- Supports filtering (AIP-160)
- Supports ordering (AIP-160)
- Returns list + next_page_token
- parent field is REQUIRED for nested resources

**Request Fields**:
- `parent`: REQUIRED, format documented in comment
- `page_size`: int32, optional (default ~50, max 1000)
- `page_token`: string, from previous response
- `filter`: string, optional filtering expression
- `order_by`: string, optional ordering expression

**Response Fields**:
- Repeated resource field (e.g., `repeated Book books`)
- `next_page_token`: empty if no more pages

**Sequence Diagram Pattern**:

```plantuml
Client -> C: GET /v1/publishers/123/books?page_size=50
activate C

C -> S: listBooks(parent="publishers/123", pageSize=50, pageToken=null)
activate S

S -> R: findByParent("publishers/123", Pageable(size=50))
activate R
R -> DB: SELECT * FROM books WHERE publisher_id=123 LIMIT 51
activate DB
DB --> R: List<BookEntity> (51 items = hasMore)
deactivate DB
R --> S: List<BookEntity> + hasMore=true
deactivate R

S -> S: entities → BookResponseDTO[]
S -> S: generateNextPageToken()
S --> C: ListBooksResponse { books[], nextPageToken: "xyz" }
deactivate S

C --> Client: 200 OK + ListBooksResponse
        { "books": [...], "nextPageToken": "xyz" }
deactivate C
```

**Empty List Response**:

```plantuml
alt No books found
    R --> S: Empty list
    S --> C: ListBooksResponse { books: [], nextPageToken: "" }
    C --> Client: 200 OK + { "books": [], "nextPageToken": "" }
end
```

---

### Create (AIP-133)

**HTTP**: `POST /v1/{parent=parentPattern}/collectionId`

**Rules**:
- Request body contains resource to create (without `name` field)
- Response returns created resource (with server-generated `name`)
- Supports client-specified ID via `resourceId` field
- HTTP 200 OK or 201 Created
- Errors: ALREADY_EXISTS if client ID conflicts, INVALID_ARGUMENT if bad data

**Idempotency Consideration**:

```plantuml
alt Client provides resourceId (idempotent create)
    Client -> C: POST /v1/publishers/123/books\n{ "resourceId": "my-book", ... }
    C -> S: createBook(parent, resourceId="my-book", BookData)
    S -> R: findByName("publishers/123/books/my-book")
    alt Already exists
        S --> C: ALREADY_EXISTS (or return existing if atomic)
    else Not exists
        S -> R: save(BookEntity with id="my-book")
    end
else Server generates ID
    S -> S: generateId()
    S -> R: save(BookEntity with generated id)
end
```

**Sequence Diagram Pattern (server-generated ID)**:

```plantuml
Client -> C: POST /v1/publishers/123/books
        { "title": "New Book", "author": "Jane" }
activate C

C -> C: validate request body
C -> S: createBook(parent="publishers/123", BookData)
activate S

S -> S: applyDefaults(bookData)
S -> S: validateBusinessRules(bookData)
S -> S: generateUniqueId()

S -> R: save(BookEntity)
activate R
R -> DB: INSERT INTO books (id, title, ...) VALUES (...)
activate DB
DB --> R: persisted BookEntity
deactivate DB
R --> S: BookEntity (with name="publishers/123/books/abc-uuid")
deactivate R

S -> S: entity → BookResponseDTO
S --> C: BookResponseDTO
C --> Client: 201 Created + BookResponseDTO
        { "name": "publishers/123/books/abc-uuid", ... }
deactivate S
deactivate C
```

---

### Update (AIP-134)

**HTTP**: `PATCH /v1/{resource.name=resourcePattern}`

**Rules**:
- Uses PATCH (partial update), not PUT
- Request body contains resource with `name` field
- Includes `update_mask` (FieldMask) specifying which fields to update
- Returns updated resource
- Errors: NOT_FOUND, INVALID_ARGUMENT, FAILED_PRECONDITION

**Update Mask Processing**:

```plantuml
Client -> C: PATCH /v1/publishers/123/books/456
        { "book": { "name": "...", "title": "New Title" },
          "update_mask": "title" }
activate C

C -> C: validate update_mask
C -> S: updateBook(BookEntity, updateMask={"title"})
activate S

S -> R: findByName("publishers/123/books/456")
activate R
R -> DB: SELECT ...
DB --> R: existing BookEntity
deactivate R
R --> S: BookEntity
deactivate R

alt Book not found
    S --> C: NOT_FOUND
else Book exists
    S -> S: applyUpdateMask(existing, newData, mask)
    note right: Only "title" is updated,
    other fields remain unchanged
    
    S -> S: validateUpdatedFields(book)
    S -> R: save(updated BookEntity)
    R -> DB: UPDATE books SET title='New Title' WHERE ...
    DB --> R: updated BookEntity
    R --> S
    
    S -> S: entity → BookResponseDTO
    S --> C: BookResponseDTO
end
deactivate S

C --> Client: 200 OK + BookResponseDTO
deactivate C
```

**Full Replacement (PUT - Discouraged)**:

If PUT is used, the entire resource is replaced. Document as backwards-incompatible risk.

---

### Delete (AIP-135)

**HTTP**: `DELETE /v1/{name=resourcePattern}`

**Rules**:
- Idempotent (deleting non-existent returns success or 404)
- Returns: 204 No Content or 200 OK (with metadata)
- Supports force parameter for cascading delete
- Supports soft delete (AIP-164)

**Sequence Diagram Pattern (hard delete)**:

```plantuml
Client -> C: DELETE /v1/publishers/123/books/456
activate C

C -> S: deleteBook(name="publishers/123/books/456")
activate S

S -> R: findByName("publishers/123/books/456")
activate R
R -> DB: SELECT ...
DB --> R: BookEntity (or null)
deactivate R
R --> S: Optional<BookEntity>
deactivate R

alt Book not found (idempotent)
    S --> C: success (already deleted)
    C --> Client: 204 No Content
    note right: Some APIs return 404;
    document the behavior
else Book found
    alt Has dependent resources
        S --> C: FAILED_PRECONDITION
        C --> Client: 409 Conflict + reason
    else No dependents
        S -> R: delete("publishers/123/books/456")
        activate R
        R -> DB: DELETE FROM books WHERE ...
        DB --> R: success
        deactivate R
        R --> S
        S --> C: success
        C --> Client: 204 No Content
    end
end
deactivate S
deactivate C
```

**Soft Delete Pattern (AIP-164)**:

```plantuml
Client -> C: DELETE /v1/publishers/123/books/456
C -> S: deleteBook(name, force=false)
S -> R: findByName(name)

S -> S: check state machine
alt Resource in non-deletable state
    S --> C: FAILED_PRECONDITION
else Deletable
    S -> R: markDeleted(name)
    R -> DB: UPDATE books SET deleted=true, deleted_at=NOW() WHERE ...
    DB --> R: updated
    R --> S
    S --> C: success
end

C --> Client: 204 No Content
note right: Resource remains in DB
with deleted flag. Can be
restored via custom method.
```

---

## Custom Methods (AIP-136)

Custom methods use `:` separator in URI and often map to RPC-style operations.

### URI Patterns

```
POST /v1/{resource}:customVerb        # Resource-scoped
POST /v1/{parent}/collection:customVerb # Collection-scoped
POST /v1/customVerb                   # Global
```

### Common Custom Method Examples

| Operation | URI Pattern | Description |
|-----------|-------------|-------------|
| Cancel | `POST /v1/{name}:cancel` | Cancel a long-running operation |
| Restore | `POST /v1/{name}:restore` | Restore a soft-deleted resource |
| Publish | `POST /v1/{name}:publish` | Publish a draft resource |
| Archive | `POST /v1/{name}:archive` | Archive a resource |
| Approve | `POST /v1/{name}:approve` | Approve a pending resource |
| Search | `POST /v1/{parent}/collection:search` | Complex search |

### Custom Method Pattern (Cancel Example)

```plantuml
Client -> C: POST /v1/operations/abc-123:cancel
activate C

C -> S: cancelOperation(name="operations/abc-123")
activate S

S -> R: findByName("operations/abc-123")
activate R
R -> DB: SELECT ...
DB --> R: OperationEntity (state=RUNNING)
R --> S
deactivate R

alt Operation not found
    S --> C: NOT_FOUND
else Operation already completed
    S --> C: FAILED_PRECONDITION
else Operation running
    S -> S: validateStateTransition(RUNNING → CANCELLING)
    S -> R: updateState(name, CANCELLING)
    activate R
    R -> DB: UPDATE operations SET state='CANCELLING' WHERE ...
    DB --> R: updated
    deactivate R
    R --> S
    
    S -> S: triggerCancellation(name)
    S --> C: Operation (state=CANCELLING)
end
deactivate S

C --> Client: 200 OK + Operation
        { "name": "operations/abc-123", "state": "CANCELLING" }
deactivate C
```

---

## Pagination (AIP-158)

### Request/Response Fields

**Request**:
- `page_size`: int32, max results per page (default ~50, max 1000)
- `page_token`: string, opaque token from previous `next_page_token`

**Response**:
- Resource list field (e.g., `books[]`)
- `next_page_token`: empty string if no more results

### Sequence Diagram Pattern

```plantuml
== First Page Request ==
Client -> C: GET /v1/publishers/123/books?page_size=10
C -> S: listBooks(parent, pageSize=10, pageToken="")
S -> R: findByParent(parent, Pageable(0, 10))
R -> DB: SELECT * FROM books WHERE ... ORDER BY id LIMIT 11
DB --> R: rows (11 items)
R --> S: entities + hasMore=true
S -> S: generateToken(offset=10)
S --> C: { "books": [10 items], "nextPageToken": "CgYwLTEw" }
C --> Client: 200 OK + response

== Second Page Request ==
Client -> C: GET /v1/publishers/123/books?page_size=10&page_token=CgYwLTEw
C -> S: listBooks(parent, pageSize=10, pageToken="CgYwLTEw")
S -> S: decodeToken("CgYwLTEw") → offset=10
S -> R: findByParent(parent, Pageable(10, 10))
R -> DB: SELECT * FROM books WHERE ... ORDER BY id LIMIT 11 OFFSET 10
DB --> R: rows (5 items)
R --> S: entities + hasMore=false
S --> C: { "books": [5 items], "nextPageToken": "" }
C --> Client: 200 OK + response
```

---

## Errors (AIP-193)

### Error Response Format

All errors return `google.rpc.Status`:

```json
{
  "code": 5,
  "message": "Book 'books/456' not found.",
  "details": [
    {
      "@type": "type.googleapis.com/google.rpc.ErrorInfo",
      "reason": "RESOURCE_NOT_FOUND",
      "domain": "library.googleapis.com",
      "metadata": { "resource": "books/456" }
    }
  ]
}
```

### Standard Error Codes for RoD

| Scenario | HTTP | gRPC Code | Reason |
|----------|------|-----------|--------|
| Resource not found | 404 | NOT_FOUND (5) | RESOURCE_NOT_FOUND |
| Invalid argument | 400 | INVALID_ARGUMENT (3) | INVALID_FIELD_VALUE |
| Already exists | 409 | ALREADY_EXISTS (6) | RESOURCE_ALREADY_EXISTS |
| Permission denied | 403 | PERMISSION_DENIED (7) | ACCESS_DENIED |
| Not authenticated | 401 | UNAUTHENTICATED (16) | AUTHENTICATION_REQUIRED |
| State conflict | 409 | FAILED_PRECONDITION (9) | INVALID_STATE_TRANSITION |
| Rate limited | 429 | RESOURCE_EXHAUSTED (8) | RATE_LIMIT_EXCEEDED |
| Internal error | 500 | INTERNAL (13) | INTERNAL_ERROR |

### Sequence Diagram Error Fragment Template

```plantuml
alt ERROR: Resource Not Found
    Service -> Service: composeError(
        code=NOT_FOUND,
        message="Book 'books/456' not found.",
        reason="RESOURCE_NOT_FOUND",
        metadata={"resource": "books/456"})
    Service --> Controller: DomainException(NOT_FOUND)
    Controller --> Client: 404 Not Found + ErrorInfo
    note right
        {
          "code": 5,
          "message": "Book 'books/456' not found.",
          "details": [{
            "reason": "RESOURCE_NOT_FOUND",
            "metadata": { "resource": "books/456" }
          }]
        }
    end note
```

---

## Field Behavior (AIP-203)

Field behavior annotations determine which fields are involved in each operation.

### Field Behavior Types

| Annotation | Meaning | Create | Get | Update | List |
|-----------|---------|--------|-----|--------|------|
| `REQUIRED` | Must be provided | Client provides | Returned | N/A (already exists) | Returned |
| `OPTIONAL` | May be provided | Client may provide | Returned if set | Client may update | Returned if set |
| `OUTPUT_ONLY` | Server-generated | Ignored if provided | Returned | Ignored if provided | Returned |
| `INPUT_ONLY` | Never returned | Client provides | Not returned | Client may update | Not returned |
| `IMMUTABLE` | Set once on create | Client provides | Returned | Error if changed | Returned |
| `IDENTIFIER` | Identifies the resource | N/A (generated) | Returned as `name` | N/A | Returned as `name` |
| `UNORDERED_LIST` | Collection, order insignificant | N/A | Returned | May update | Returned |

### Field Behavior in Sequence Diagrams

Show field behavior through message content and validation:

```plantuml
== Create: name is OUTPUT_ONLY (server-generated) ==
Client -> C: POST /v1/publishers/123/books
        { "title": "X", "author": "Y", "name": "ignored" }
C -> S: createBook(...)
S -> S: stripOutputOnlyFields(input)
note right: name field stripped
(OUTPUT_ONLY)

== Get: all non-INPUT_ONLY fields returned ==
S --> C: Book { name, title, author, createTime }
note right: No internalId (INPUT_ONLY)

== Update: only update_mask fields processed ==
Client -> C: PATCH /v1/.../books/456
        { "book": { "name": "...", "title": "New" },
          "update_mask": "title" }
C -> S: updateBook(book, "title")
S -> S: validateMaskAgainstImmutableFields(mask)
note right: Error if mask includes
immutable fields
```

---

## State Management (AIP-216)

### State Enum Pattern

Resources with lifecycle states use a `state` enum field marked OUTPUT_ONLY:

```protobuf
enum State {
  STATE_UNSPECIFIED = 0;
  CREATING = 1;
  ACTIVE = 2;
  UPDATING = 3;
  DELETING = 4;
  DELETED = 5;
  ARCHIVED = 6;
}
```

### State Transition Diagram in Sequence Form

```plantuml
== State: CREATING → ACTIVE ==
S -> S: validateTransition(CREATING, ACTIVE)
alt Transition not allowed
    S --> C: FAILED_PRECONDITION
        { "error": {
            "message": "Cannot transition from CREATING to ACTIVE.",
            "details": [{
              "reason": "INVALID_STATE_TRANSITION",
              "metadata": {
                "from": "CREATING",
                "to": "ACTIVE"
              }
            }]
        }}
else Transition allowed
    S -> R: updateState(name, ACTIVE)
end

== Typical State Machine (Order Lifecycle) ==
Client -> C: POST /v1/orders (Create)
S -> S: initialState = PENDING_PAYMENT

Client -> C: POST /v1/orders/123:pay
S -> S: transition PENDING_PAYMENT → PROCESSING

alt Payment processing complete
    S -> S: transition PROCESSING → COMPLETED
else Payment failed
    S -> S: transition PROCESSING → CANCELLED
end

Client -> C: POST /v1/orders/123:cancel (only if PENDING_PAYMENT)
S -> S: validate current state allows cancel
alt State not CANCELLABLE
    S --> C: FAILED_PRECONDITION
else
    S -> S: transition → CANCELLED
end
```

### Read-Only During State Transitions

```plantuml
alt Resource in transitional state
    Client -> C: PATCH /v1/.../books/456
    C -> S: updateBook(...)
    S -> S: checkState(bookId)
    alt State in (CREATING, DELETING, UPDATING)
        S --> C: FAILED_PRECONDITION
        C --> Client: 409 Conflict
            "Cannot modify resource while in CREATING state"
    end
end
```
