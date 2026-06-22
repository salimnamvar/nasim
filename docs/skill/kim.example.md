# Worked Examples

Complete, ready-to-use PlantUML sequence diagrams for common CSR-RoD operations.

## Table of Contents

- [Worked Examples](#worked-examples)
  - [Table of Contents](#table-of-contents)
  - [Get Resource](#get-resource)
  - [List Resources](#list-resources)
  - [Create Resource](#create-resource)
  - [Update Resource](#update-resource)
  - [Delete Resource](#delete-resource)
  - [Custom Method: Cancel](#custom-method-cancel)
  - [Custom Method: Approve](#custom-method-approve)
  - [Stateful Resource Lifecycle](#stateful-resource-lifecycle)
  - [Batch Create](#batch-create)
  - [Error Propagation](#error-propagation)

---

## Get Resource

Standard single-resource retrieval with full error handling.

```plantuml
@startuml
!theme plain

actor "API Client" as Client
participant "BookController" as BC
participant "BookService" as BS
participant "BookRepository" as BR
database "PostgreSQL" as DB

title Get Book (AIP-131)

== Request ==
Client -> BC+: GET /v1/publishers/123/books/456

== Authentication ==
opt Validate Bearer Token
    BC -> BC: verifyToken(authHeader)
    alt Token expired
        BC --> Client-: 401 Unauthorized
            \n{ "error": { "code": 16, "message": "Token expired" } }
    end
end

== Retrieve ==
BC -> BS+: getBook(name="publishers/123/books/456")
BS -> BR+: findByName(name)
BR -> DB+: SELECT * FROM books WHERE publisher_id=123 AND book_id=456
DB --> BR-: BookEntity (or null)
BR --> BS-: Optional<BookEntity>

== Response Handling ==
alt Book Not Found
    BS -> BS: buildError(
        NOT_FOUND, "Book '.../books/456' not found",
        ErrorInfo { reason="RESOURCE_NOT_FOUND",
                    metadata={ "resource": ".../books/456" } })
    BS --> BC-: throw NotFoundException
    BC --> Client-: 404 Not Found
        \n{ "code": 5, "message": "Book not found",
          "details": [{ "reason": "RESOURCE_NOT_FOUND" }] }

else Book Found
    BS -> BS: entity → BookResponseDTO
    BS --> BC-: BookResponseDTO
    BC --> Client-: 200 OK
        \n{ "name": "publishers/123/books/456",
          "title": "Design Patterns",
          "author": "GoF",
          "state": "ACTIVE",
          "createTime": "2024-01-15T10:30:00Z" }
end

@enduml
```

---

## List Resources

Paginated list with filter and ordering.

```plantuml
@startuml
!theme plain

actor "API Client" as Client
participant "BookController" as BC
participant "BookService" as BS
participant "BookRepository" as BR
database "PostgreSQL" as DB

title List Books (AIP-132) with Pagination

== First Page Request ==
Client -> BC+: GET /v1/publishers/123/books?page_size=3&filter=price<50&order_by=title

BC -> BC: parseFilter("price<50")
BC -> BC: parseOrderBy("title")
BC -> BS+: listBooks(
    parent="publishers/123",
    pageSize=3,
    pageToken="",
    filter="price<50",
    orderBy="title")

BS -> BR+: findByParent(parent, Pageable(size=3+1))
note right: Query page_size+1 to detect hasMore
BR -> DB+: SELECT * FROM books\nWHERE publisher_id=123 AND price<50\nORDER BY title\nLIMIT 4
DB --> BR-: [Book-A, Book-B, Book-C, Book-D]
BR --> BS-: entities (4 items)

BS -> BS: hasMore = (results.size > pageSize)
BS -> BS: if hasMore: trim last item, encode page token
BS -> BS: entities → BookResponseDTO[]

BS --> BC-: ListBooksResponse {
    books: [Book-A, Book-B, Book-C],
    nextPageToken: "eyJvZmZzZXQiOjN9" }
BC --> Client-: 200 OK + response

== Second Page Request ==
Client -> BC+: GET .../books?page_size=3&page_token=eyJvZmZzZXQiOjN9
BC -> BS+: listBooks(parent, 3, "eyJvZmZzZXQiOjN9", filter, orderBy)
BS -> BS: decodeToken → offset=3
BS -> BR+: findByParent(parent, Pageable(3, 4))
BR -> DB+: SELECT ... LIMIT 4 OFFSET 3
DB --> BR-: [Book-D, Book-E]
BR --> BS-: entities (2 items)
BS -> BS: hasMore = false
BS --> BC-: { books: [Book-D, Book-E], nextPageToken: "" }
BC --> Client-: 200 OK + response (last page)

@enduml
```

---

## Create Resource

Server-generated ID with validation and business rules.

```plantuml
@startuml
!theme plain

actor "API Client" as Client
participant "BookController" as BC
participant "BookService" as BS
participant "PublisherRepository" as PR
database "PostgreSQL" as DB

title Create Book (AIP-133) with Parent Validation

== Request ==
Client -> BC+: POST /v1/publishers/123/books
        \n{ "title": "Clean Code", "author": "Bob Martin", "price": 42.99 }

== Phase 1: Structural Validation ==
BC -> BC: validateFormat(requestBody)
alt Missing required field
    BC --> Client-: 400 Bad Request
        \n{ "error": { "code": 3, "message": "Field 'title' is required" } }
end
alt Invalid field type
    BC --> Client-: 400 Bad Request
        \n{ "error": { "code": 3, "message": "Field 'price' must be numeric" } }
end

== Phase 2: Parent Validation ==
BC -> BS+: createBook(parent="publishers/123", bookData)
BS -> PR+: existsByName("publishers/123")
PR -> DB+: SELECT 1 FROM publishers WHERE id=123
DB --> PR-: 1 row
PR --> BS-: true

alt Parent not found
    BS -> BS: buildError(NOT_FOUND, "Publisher not found")
    BS --> BC-: throw NotFoundException
    BC --> Client-: 404 Not Found
end

== Phase 3: Business Logic ==
BS -> BS: validateBusinessRules(bookData)
alt Price negative
    BS --> BC-: throw ValidationException("Price must be >= 0")
    BC --> Client-: 400 Bad Request
end

BS -> BS: generateResourceId()
BS -> BS: setDefaults(bookData)
note right: Set createTime, state=PENDING_REVIEW,
name="publishers/123/books/{generatedId}"

== Phase 4: Persistence ==
BS -> PR+: save(bookEntity)
PR -> DB+: INSERT INTO books (id, publisher_id, title, ...) VALUES (...)
DB --> PR-: persisted row
PR --> BS-: BookEntity

== Phase 5: Response ==
BS -> BS: entity → BookResponseDTO
BS --> BC-: BookResponseDTO
BC --> Client-: 201 Created
        \n{ "name": "publishers/123/books/abc-789",
          "title": "Clean Code",
          "author": "Bob Martin",
          "price": 42.99,
          "state": "PENDING_REVIEW",
          "createTime": "2024-06-15T14:22:00Z" }

@enduml
```

---

## Update Resource

Partial update with update mask and field behavior handling.

```plantuml
@startuml
!theme plain

actor "API Client" as Client
participant "BookController" as BC
participant "BookService" as BS
participant "BookRepository" as BR
database "PostgreSQL" as DB

title Update Book (AIP-134) with Update Mask

== Request ==
Client -> BC+: PATCH /v1/publishers/123/books/456
        \n{ "book": {
            "name": "publishers/123/books/456",
            "title": "Clean Code: Revised",
            "price": 49.99 },
          "update_mask": "title,price" }

BC -> BC: validate update_mask syntax

== Retrieve Existing ==
BC -> BS+: updateBook(book, updateMask={"title","price"})
BS -> BR+: findByName("publishers/123/books/456")
BR -> DB+: SELECT * FROM books WHERE ...
DB --> BR-: existing BookEntity
BR --> BS-: BookEntity

alt Resource Not Found
    BS --> BC-: NOT_FOUND
    BC --> Client-: 404 Not Found
end

== Validate Immutable Fields ==
BS -> BS: checkMaskAgainstImmutableFields(mask, Book.class)
alt Mask contains immutable field (e.g., "name", "createTime")
    BS --> BC-: throw ValidationException("Cannot update immutable field 'name'")
    BC --> Client-: 400 Bad Request
        \n{ "error": { "code": 3, "message": "Field 'name' is immutable" } }
end

== State Validation ==
BS -> BS: checkStateAllowsUpdate(entity.state)
alt Resource in non-updatable state
    BS --> BC-: FAILED_PRECONDITION
    BC --> Client-: 409 Conflict
        \n{ "error": { "code": 9,
          "message": "Cannot update resource in ARCHIVED state" } }
end

== Apply Update ==
BS -> BS: applyFieldMask(existing, newData, mask)
note right: Only title and price updated.
author remains unchanged.
createTime remains unchanged.
BS -> BS: validateUpdatedFields(entity)

== Persist ==
BS -> BR+: save(updatedEntity)
BR -> DB+: UPDATE books SET title='Clean Code: Revised', price=49.99 WHERE ...
DB --> BR-: updated row
BR --> BS-: BookEntity

BS -> BS: entity → BookResponseDTO
BS --> BC-: BookResponseDTO
BC --> Client-: 200 OK
        \n{ "name": "publishers/123/books/456",
          "title": "Clean Code: Revised",
          "author": "Bob Martin",     ' unchanged
          "price": 49.99,            ' updated
          "updateTime": "2024-06-15T15:00:00Z" }

@enduml
```

---

## Delete Resource

Soft delete with state transition and force option.

```plantuml
@startuml
!theme plain

actor "API Client" as Client
participant "BookController" as BC
participant "BookService" as BS
participant "BookRepository" as BR
database "PostgreSQL" as DB

title Delete Book (AIP-135) with Soft Delete

== Request ==
Client -> BC+: DELETE /v1/publishers/123/books/456

BC -> BS+: deleteBook(name="publishers/123/books/456")

== Check Existence ==
BS -> BR+: findByName(name)
BR -> DB+: SELECT ... FROM books WHERE ... AND deleted=false
DB --> BR-: BookEntity
BR --> BS-: BookEntity

alt Already Deleted (Idempotent)
    BS --> BC-: success (no-op)
    BC --> Client-: 204 No Content
end

== Check Dependencies ==
BS -> BR+: countActiveOrdersForBook(name)
BR -> DB+: SELECT COUNT(*) FROM order_items WHERE book_id=456 AND status='ACTIVE'
DB --> BR-: 3
BR --> BS-: 3

alt Has Active Dependencies
    BS -> BS: buildError(FAILED_PRECONDITION,
        "Cannot delete book with 3 active orders",
        ErrorInfo { reason="RESOURCE_HAS_DEPENDENTS",
                    metadata={ "activeOrders": "3" } })
    BS --> BC-: throw FailedPreconditionException
    BC --> Client-: 409 Conflict
        \n{ "error": { "code": 9,
          "message": "Book has 3 active orders",
          "details": [{ "reason": "RESOURCE_HAS_DEPENDENTS" }] } }
end

== Soft Delete Execution ==
BS -> BS: validateStateTransition(ACTIVE → DELETED)
BS -> BS: entity.state = DELETED
BS -> BS: entity.deleteTime = now()
BS -> BR+: save(entity)
BR -> DB+: UPDATE books SET state='DELETED', deleted=true, delete_time=NOW() WHERE ...
DB --> BR-: updated
BR --> BS-: success

BS --> BC-: success
BC --> Client-: 204 No Content

note right: Book remains in DB with
state=DELETED. Can be restored
via :restore custom method.

@enduml
```

---

## Custom Method: Cancel

Cancel a long-running operation.

```plantuml
@startuml
!theme plain

actor "API Client" as Client
participant "OperationController" as OC
participant "OperationService" as OS
participant "OperationRepository" as OR
database "PostgreSQL" as DB

title Custom Method: Cancel Operation (AIP-136)

== Request ==
Client -> OC+: POST /v1/operations/abc-123:cancel
        \n{}

== Validate ==
OC -> OS+: cancelOperation(name="operations/abc-123")
OS -> OR+: findByName("operations/abc-123")
OR -> DB+: SELECT * FROM operations WHERE id='abc-123'
DB --> OR-: OperationEntity (state=RUNNING)
OR --> OS-: OperationEntity

alt Operation Not Found
    OS --> OC-: NOT_FOUND
    OC --> Client-: 404 Not Found
end

== State Transition ==
OS -> OS: validateTransition(RUNNING → CANCELLING)
alt Already Completed
    OS --> OC-: FAILED_PRECONDITION
    OC --> Client-: 409 Conflict
        \n{ "error": { "message": "Cannot cancel completed operation" } }
else Already Cancelled
    OS --> OC-: FAILED_PRECONDITION
    OC --> Client-: 409 Conflict
        \n{ "error": { "message": "Operation already cancelled" } }
end

== Execute Cancellation ==
OS -> OS: operation.state = CANCELLING
OS -> OR+: save(operation)
OR -> DB+: UPDATE operations SET state='CANCELLING' WHERE id='abc-123'
DB --> OR-: updated
OR --> OS-: OperationEntity

OS -> OS: triggerCancellationTask(operation.name)
note right: Async task will transition
CANCELLING → CANCELLED

OS -> OS: entity → OperationResponseDTO
OS --> OC-: OperationResponseDTO
OC --> Client-: 200 OK
        \n{ "name": "operations/abc-123",
          "state": "CANCELLING",
          "cancelTime": "2024-06-15T16:00:00Z" }

@enduml
```

---

## Custom Method: Approve

State-driven approval workflow.

```plantuml
@startuml
!theme plain

actor "Approver" as Approver
participant "ApprovalController" as AC
participant "ApprovalService" as AS
participant "ApprovalRepository" as AR
database "PostgreSQL" as DB

title Custom Method: Approve Request (AIP-136)

== Request ==
Approver -> AC+: POST /v1/requests/req-456:approve
        \n{ "comment": "Approved per policy" }

AC -> AS+: approveRequest(name="requests/req-456", comment)

== Validate Request ==
AS -> AR+: findByName("requests/req-456")
AR -> DB+: SELECT * FROM requests WHERE id='req-456'
DB --> AR-: RequestEntity (state=PENDING_APPROVAL)
AR --> AS-: RequestEntity

alt Request Not Found
    AS --> AC-: NOT_FOUND
    AC --> Approver-: 404 Not Found
end

== Authorization Check ==
AS -> AS: checkApproverAuthorization(request, approver)
alt Not Authorized
    AS --> AC-: PERMISSION_DENIED
    AC --> Approver-: 403 Forbidden
        \n{ "error": { "message": "Not authorized to approve this request" } }
end

== State Validation ==
AS -> AS: validateStateTransition(PENDING_APPROVAL → APPROVED)
alt Invalid State for Approval
    AS --> AC-: FAILED_PRECONDITION
    AC --> Approver-: 409 Conflict
        \n{ "error": { "message": "Request must be in PENDING_APPROVAL state" } }
end

== Execute Approval ==
AS -> AS: request.state = APPROVED
AS -> AS: request.approverComment = comment
AS -> AS: request.approveTime = now()

AS -> AR+: save(request)
AR -> DB+: UPDATE requests SET state='APPROVED', ... WHERE id='req-456'
DB --> AR-: updated
AR --> AS-: RequestEntity

AS -> AS: postApprovalActions(request)
note right: Notify submitter, trigger
 downstream workflows, etc.

AS -> AS: entity → RequestResponseDTO
AS --> AC-: RequestResponseDTO
AC --> Approver-: 200 OK
        \n{ "name": "requests/req-456",
          "state": "APPROVED",
          "approverComment": "Approved per policy",
          "approveTime": "2024-06-15T16:30:00Z" }

@enduml
```

---

## Stateful Resource Lifecycle

Complete state machine for an Order resource.

```plantuml
@startuml
!theme plain

actor "Customer" as Customer
actor "Admin" as Admin
participant "OrderController" as OC
participant "OrderService" as OS
participant "OrderRepository" as OR
database "PostgreSQL" as DB

title Stateful Resource: Order Lifecycle (AIP-216)

== Create Order (PENDING_PAYMENT) ==
Customer -> OC+: POST /v1/orders
OC -> OS+: createOrder(CreateOrderRequest)
OS -> OS: initializeOrder()
OS -> OS: order.state = PENDING_PAYMENT

OS -> OR+: save(order)
OR -> DB+: INSERT INTO orders ...
DB --> OR-: OrderEntity
OR --> OS-: OrderEntity

OS --> OC-: OrderResponseDTO
OC --> Customer-: 201 Created
        \n{ "name": "orders/ord-789", "state": "PENDING_PAYMENT" }

== Pay (:pay) PENDING_PAYMENT → PROCESSING ==
Customer -> OC+: POST /v1/orders/ord-456:pay
        \n{ "paymentMethod": "card_123" }

OC -> OS+: payOrder(name="orders/ord-456", paymentDetails)
OS -> OR+: findByName("orders/ord-456")
OR -> DB+: SELECT ...
DB --> OR-: OrderEntity (state=PENDING_PAYMENT)
OR --> OS-: OrderEntity

OS -> OS: validateStateTransition(PENDING_PAYMENT → PROCESSING)
alt Invalid state
    OS --> OC-: FAILED_PRECONDITION
    OC --> Customer-: 409 Conflict
end

OS -> OS: processPayment(paymentDetails)
alt Payment failed
    OS -> OS: order.state = PAYMENT_FAILED
    OS -> OR+: save(order)
    OR -> DB+: UPDATE ...
    DB --> OR-: updated
    OR --> OS-: OrderEntity
    OS --> OC-: OrderResponseDTO
    OC --> Customer-: 200 OK
        \n{ "name": "orders/ord-456", "state": "PAYMENT_FAILED" }
else Payment succeeded
    OS -> OS: order.state = PROCESSING
    OS -> OR+: save(order)
    OR -> DB+: UPDATE ...
    DB --> OR-: updated
    OR --> OS-: OrderEntity
    OS --> OC-: OrderResponseDTO
    OC --> Customer-: 200 OK
        \n{ "name": "orders/ord-456", "state": "PROCESSING" }
end

== Fulfillment (PROCESSING → SHIPPED) [Backend] ==
Admin -> OC+: POST /v1/orders/ord-456:ship
        \n{ "trackingNumber": "TRK-789" }

OC -> OS+: shipOrder(name, trackingDetails)
OS -> OR+: findByName(name)
OR -> DB+: SELECT ...
DB --> OR-: OrderEntity (state=PROCESSING)
OR --> OS-: OrderEntity

OS -> OS: validateStateTransition(PROCESSING → SHIPPED)
alt Not PROCESSING
    OS --> OC-: FAILED_PRECONDITION
    OC --> Admin-: 409 Conflict
end

OS -> OS: order.state = SHIPPED
OS -> OS: order.trackingNumber = trackingNumber
OS -> OR+: save(order)
OR -> DB+: UPDATE ...
DB --> OR-: updated
OR --> OS-: OrderEntity
OS --> OC-: OrderResponseDTO
OC --> Admin-: 200 OK
        \n{ "name": "orders/ord-456", "state": "SHIPPED",
          "trackingNumber": "TRK-789" }

== Delivered (SHIPPED → DELIVERED) [Webhook/Backend] ==
OS -> OS: onDeliveryConfirmed(order)
OS -> OR+: findByName("orders/ord-456")
OR -> DB+: SELECT ...
DB --> OR-: OrderEntity (state=SHIPPED)
OR --> OS-: OrderEntity

OS -> OS: validateStateTransition(SHIPPED → DELIVERED)
OS -> OS: order.state = DELIVERED
OS -> OS: order.deliverTime = now()
OS -> OR+: save(order)
OR -> DB+: UPDATE ...
DB --> OR-: updated
OR --> OS-: OrderEntity

OS -> OS: sendDeliveryNotification(order)

== Cancel (:cancel) [PENDING_PAYMENT only] ==
Customer -> OC+: POST /v1/orders/ord-456:cancel
OC -> OS+: cancelOrder(name="orders/ord-456")
OS -> OR+: findByName(name)
OR -> DB+: SELECT ...
DB --> OR-: OrderEntity (state=SHIPPED)
OR --> OS-: OrderEntity

OS -> OS: validateStateTransition(SHIPPED → CANCELLED)
alt State does not allow cancellation
    OS --> OC-: FAILED_PRECONDITION
    OC --> Customer-: 409 Conflict
        \n{ "error": { "message": "Cannot cancel shipped order" } }
else Transition allowed
    OS -> OS: order.state = CANCELLED
    OS -> OR+: save(order)
    OR -> DB+: UPDATE ...
    DB --> OR-: updated
    OR --> OS-: OrderEntity
    OS --> OC-: OrderResponseDTO
    OC --> Customer-: 200 OK
        \n{ "name": "orders/ord-456", "state": "CANCELLED" }
end

@enduml
```

---

## Batch Create

Atomic batch operation with partial success handling.

```plantuml
@startuml
!theme plain

actor "API Client" as Client
participant "BookController" as BC
participant "BookService" as BS
participant "BookRepository" as BR
database "PostgreSQL" as DB

title Batch Create Books

== Request ==
Client -> BC+: POST /v1/publishers/123/books:batchCreate
        \n{ "requests": [
            { "book": { "title": "Book A", "price": 10 } },
            { "book": { "title": "Book B", "price": -5 } },
            { "book": { "title": "Book C", "price": 20 } }
        ] }

BC -> BS+: batchCreateBooks(parent="publishers/123", requests[])

== Process Each Item ==
BS -> BS: initialize results[]

loop for each request in requests
    BS -> BS: validateBookData(request.book)
    alt Validation failed
        BS -> BS: results.add({
            index: i,
            status: "INVALID_ARGUMENT",
            error: "Price must be non-negative" })
    else Validation passed
        BS -> BS: generateId()
        BS -> BS: setDefaults(book)
        BS -> BR+: save(bookEntity)
        BR -> DB+: INSERT ...
        DB --> BR-: persisted
        BR --> BS-: BookEntity
        BS -> BS: results.add({
            index: i,
            status: "OK",
            book: BookResponseDTO })
    end
end

BS --> BC-: BatchCreateResponse { results[] }

alt All succeeded
    BC --> Client-: 200 OK
        \n{ "results": [
            { "index": 0, "status": "OK", "book": { "name": ".../bk-1" } },
            { "index": 1, "status": "OK", "book": { "name": ".../bk-2" } },
            { "index": 2, "status": "OK", "book": { "name": ".../bk-3" } } ] }
else Partial success
    BC --> Client-: 200 OK (partial success)
        \n{ "results": [
            { "index": 0, "status": "OK", "book": { "name": ".../bk-1" } },
            { "index": 1, "status": "INVALID_ARGUMENT",
              "error": { "message": "Price must be non-negative" } },
            { "index": 2, "status": "OK", "book": { "name": ".../bk-3" } } ] }
end

@enduml
```

---

## Error Propagation

Comprehensive error handling across all CSR layers.

```plantuml
@startuml
!theme plain

actor "Client" as Client
participant "Controller" as C
participant "Service" as S
participant "Repository" as R
database "DB" as DB

title Error Propagation Across CSR Layers

== Validation Error (Controller Layer) ==
Client -> C+: POST /v1/books { "price": "not-a-number" }
C -> C: parseAndValidateBody()
C --> Client-: 400 Bad Request
    \n{ "code": 3, "message": "Invalid argument: 'price' must be numeric" }

== Not Found (Service Layer) ==
Client -> C+: GET /v1/books/999
C -> S+: getBook("books/999")
S -> R+: findByName("books/999")
R -> DB+: SELECT ...
DB --> R-: null
R --> S-: Optional.empty()
S -> S: throw new NotFoundException(
    "Book 'books/999' not found",
    ErrorInfo { reason="RESOURCE_NOT_FOUND",
                domain="library.googleapis.com",
                metadata={"resource":"books/999"} })
S --> C-: NotFoundException
C --> Client-: 404 Not Found
    \n{ "code": 5, "message": "Book 'books/999' not found",
      "details": [{
        "@type": "google.rpc.ErrorInfo",
        "reason": "RESOURCE_NOT_FOUND",
        "domain": "library.googleapis.com",
        "metadata": { "resource": "books/999" }
      }] }

== Conflict (Service Layer) ==
Client -> C+: POST /v1/books { "name": "books/existing" }
C -> S+: createBook(...)
S -> R+: existsByName("books/existing")
R -> DB+: SELECT 1 ...
DB --> R-: 1
R --> S-: true
S -> S: throw new AlreadyExistsException(
    "Book 'books/existing' already exists")
S --> C-: AlreadyExistsException
C --> Client-: 409 Conflict
    \n{ "code": 6, "message": "Book already exists" }

== Permission Denied (Service Layer) ==
Client -> C+: DELETE /v1/books/456
C -> S+: deleteBook("books/456")
S -> S: checkPermission(user, "books/456", DELETE)
S -> S: throw new PermissionDeniedException(
    "User 'alice' cannot delete book 'books/456'")
S --> C-: PermissionDeniedException
C --> Client-: 403 Forbidden
    \n{ "code": 7, "message": "Permission denied" }

== State Conflict (Service Layer) ==
Client -> C+: PATCH /v1/books/456 { ... }
C -> S+: updateBook(...)
S -> R+: findByName(...)
R --> S-: BookEntity(state=DELETED)
S -> S: throw new FailedPreconditionException(
    "Cannot modify deleted resource",
    ErrorInfo { reason="INVALID_STATE_TRANSITION",
                metadata={"currentState":"DELETED"} })
S --> C-: FailedPreconditionException
C --> Client-: 409 Conflict
    \n{ "code": 9, "message": "Resource is deleted" }

== Database Error (Repository Layer) ==
Client -> C+: POST /v1/books { "title": "New" }
C -> S+: createBook(...)
S -> R+: save(entity)
R -> DB+: INSERT ...
DB --> R-: SQLException: connection timeout
R -> R: throw new DataAccessException("Database connection failed")
R --> S-: DataAccessException
S -> S: logError()
S --> C-: InternalException
C --> Client-: 500 Internal Server Error
    \n{ "code": 13, "message": "Internal server error" }

@enduml
```
