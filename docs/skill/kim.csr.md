# CSR Layer Interaction Patterns

Detailed patterns for how operations flow through Controller-Service-Repository layers.

## Table of Contents

1. [Layer Responsibilities](#layer-responsibilities)
2. [DTO Patterns](#dto-patterns)
3. [Validation Patterns](#validation-patterns)
4. [Error Propagation](#error-propagation)
5. [Interaction Patterns by Concern](#interaction-patterns-by-concern)
6. [Nested Resource Patterns](#nested-resource-patterns)

---

## Layer Responsibilities

### Controller Layer

- **Receives** HTTP requests (GET, POST, PATCH, PUT, DELETE)
- **Validates** request format, required fields, field types
- **Transforms** HTTP request → Request DTO
- **Calls** appropriate Service method
- **Transforms** Response DTO → HTTP response
- **Handles** HTTP-level concerns (status codes, headers, CORS)
- **Does NOT** contain business logic

### Service Layer

- **Receives** Request DTOs from Controller
- **Implements** business logic and rules
- **Orchestrates** calls to one or more Repositories
- **Applies** state transition rules (for stateful resources)
- **Applies** access control rules (when not handled by middleware)
- **Transforms** Entity → Response DTO
- **Validates** business-level constraints (not format-level)
- **Does NOT** directly access the database

### Repository Layer

- **Abstracts** data access (can be JPA, JDBC, Mongo, etc.)
- **Provides** CRUD operations on entities
- **Handles** query construction and execution
- **Returns** entities or entity collections
- **Does NOT** contain business logic
- **Does NOT** return DTOs directly

---

## DTO Patterns

### Request DTO Flow

```
Client → Controller: HTTP Request (JSON)
Controller → Controller: JSON → RequestDTO (deserialization)
Controller → Service: RequestDTO
Service → Service: RequestDTO → Entity (mapping)
Service → Repository: Entity
Repository → Database: SQL/persistence operation
```

### Response DTO Flow

```
Database → Repository: Entity/Result
Repository → Service: Entity
Service → Service: Entity → ResponseDTO (mapping)
Service → Controller: ResponseDTO
Controller → Client: ResponseDTO → JSON (serialization) + HTTP Status
```

### PlantUML DTO Pattern

```plantuml
Client -> Controller: POST /v1/publishers/123/books\n{ "title": "Example", "author": "John" }
activate Controller

Controller -> Controller: deserialize → CreateBookRequestDTO
Controller -> Controller: validate(CreateBookRequestDTO)

Controller -> Service: createBook(parent, CreateBookRequestDTO)
activate Service

Service -> Service: CreateBookRequestDTO → BookEntity
Service -> Service: applyDefaults(bookEntity)
Service -> Service: validateBusinessRules(bookEntity)

Service -> Repository: save(bookEntity)
activate Repository
Repository -> DB: INSERT INTO books ...
activate DB
DB --> Repository: persisted entity
Repository --> Service: BookEntity (with generated ID)
deactivate Repository

Service -> Service: BookEntity → BookResponseDTO
Service --> Controller: BookResponseDTO
deactivate Service

Controller --> Client: 201 Created + BookResponseDTO
deactivate Controller
```

---

## Validation Patterns

### Two-Phase Validation

**Phase 1: Controller (Format/Structural)**
- Field presence (required fields)
- Data types (string, number, boolean)
- Format validation (email, URL, date format)
- Range validation (min, max values)

**Phase 2: Service (Business/Domain)**
- Uniqueness constraints
- State transition validity
- Cross-field business rules
- Authorization checks
- Referential integrity

```plantuml
Client -> Controller: request
activate Controller

Controller -> Controller: Phase 1: validateFormat()
alt Format invalid
    Controller --> Client: 400 Bad Request
else Format valid
    Controller -> Service: requestDTO
    activate Service
    
    Service -> Service: Phase 2: validateBusiness()
    alt Business invalid
        Service --> Controller: INVALID_ARGUMENT error
        Controller --> Client: 400 Bad Request + details
    else Business valid
        Service -> Repository: ...
    end
    deactivate Service
end
deactivate Controller
```

---

## Error Propagation

### Error Types by Layer

| Error Source | Layer | HTTP Status | gRPC Code |
|-------------|-------|-------------|-----------|
| Invalid JSON format | Controller | 400 Bad Request | INVALID_ARGUMENT |
| Missing required field | Controller | 400 Bad Request | INVALID_ARGUMENT |
| Type mismatch | Controller | 400 Bad Request | INVALID_ARGUMENT |
| Resource not found | Service | 404 Not Found | NOT_FOUND |
| Duplicate resource | Service | 409 Conflict | ALREADY_EXISTS |
| Business rule violation | Service | 400/422 | FAILED_PRECONDITION |
| Invalid state transition | Service | 400/409 | FAILED_PRECONDITION |
| Unauthorized | Controller/Service | 401 Unauthorized | UNAUTHENTICATED |
| Permission denied | Service | 403 Forbidden | PERMISSION_DENIED |
| Database error | Repository | 500 Internal Server | INTERNAL |
| Timeout | Service/Repository | 504 Gateway Timeout | DEADLINE_EXCEEDED |

### Error Propagation Pattern

```plantuml
alt Error: Resource Not Found
    Repository --> Service: throw NotFoundException
    Service --> Controller: propagate DomainException
    Controller --> Client: 404 Not Found\n{ "error": { "code": 404, "message": "Book 'books/456' not found" } }
else Error: Validation Failed
    Service --> Controller: throw ValidationException
    Controller --> Client: 400 Bad Request\n{ "error": { "code": 400, "message": "Invalid field 'price'", "details": [...] } }
else Error: Database Failure
    Repository --> Service: throw DataAccessException
    Service --> Controller: propagate InternalException
    Controller --> Client: 500 Internal Server Error
end
```

---

## Interaction Patterns by Concern

### 1. Simple CRUD (Single Resource)

Standard RoD methods on a single resource. See SKILL.md quick-reference.

### 2. Transactional Operation (Multiple Resources)

When a business operation must update multiple resources atomically:

```plantuml
Client -> Controller: POST /v1/orders (create order + update inventory)
activate Controller
Controller -> Service: createOrder(CreateOrderRequest)
activate Service

Service -> Service: validateOrder(request)

Service -> Repository: findProduct(productId)
activate Repository
Repository -> DB: SELECT * FROM products WHERE id=...
DB --> Repository: ProductEntity
Repository --> Service: ProductEntity
deactivate Repository

alt Insufficient inventory
    Service --> Controller: FAILED_PRECONDITION (insufficient stock)
else Sufficient inventory
    Service -> Repository: save(OrderEntity)
    activate Repository
    Repository -> DB: INSERT INTO orders ...
    DB --> Repository: OrderEntity
    Repository --> Service: OrderEntity
    deactivate Repository
    
    Service -> Repository: updateInventory(productId, -quantity)
    activate Repository
    Repository -> DB: UPDATE products SET stock=... WHERE id=...
    DB --> Repository: updated ProductEntity
    Repository --> Service: ProductEntity
    deactivate Repository
    
    Service -> Service: OrderEntity → OrderResponseDTO
    Service --> Controller: OrderResponseDTO
end
deactivate Service

Controller --> Client: 201 Created + OrderResponseDTO
deactivate Controller
```

### 3. Read with Filtering/Sorting (List Enhancement)

```plantuml
Client -> Controller: GET /v1/publishers/123/books?filter=price<50&order_by=title
activate Controller

Controller -> Controller: parse filter expression
Controller -> Controller: parse order_by fields

Controller -> Service: listBooks(parent, filter, orderBy, pageSize, pageToken)
activate Service

Service -> Repository: findByParentWithFilter(parent, filterSpec, pageable)
activate Repository
Repository -> DB: SELECT * FROM books WHERE publisher_id=... AND price<50 ORDER BY title LIMIT ...
DB --> Repository: result set
Repository --> Service: List<BookEntity> + nextPageToken
deactivate Repository

Service -> Service: entities → responseDTOs
Service --> Controller: ListBooksResponse
deactivate Service

Controller --> Client: 200 OK + response
deactivate Controller
```

### 4. Cascading Operation (Parent-Child Resources)

```plantuml
Client -> Controller: DELETE /v1/publishers/123
activate Controller
Controller -> Service: deletePublisher(name)
activate Service

Service -> Repository: findPublisher(name)
activate Repository
Repository -> DB: SELECT ...
DB --> Repository: PublisherEntity
Repository --> Service

alt Publisher has books
    Service --> Controller: FAILED_PRECONDITION
    Controller --> Client: 409 Conflict + reason
else Publisher empty
    Service -> Repository: deletePublisher(name)
    Repository -> DB: DELETE FROM publishers WHERE id=...
    DB --> Repository: success
    Repository --> Service
    
    Service --> Controller: success
    Controller --> Client: 204 No Content
end
deactivate Service
deactivate Controller
```

### 5. Batch Operation

```plantuml
Client -> Controller: POST /v1/batchDeleteBooks
Controller -> Service: batchDelete(resourceNames[])

Service -> Service: initialize results[]
loop for each resourceName
    Service -> Repository: findByName(name)
    alt Resource found
        Service -> Repository: delete(name)
        Service -> Service: results.add(success)
    else Resource not found
        Service -> Service: results.add(notFound)
    end
end

Service --> Controller: BatchDeleteResponse
Controller --> Client: 200 OK + partial results
```

---

## Nested Resource Patterns

For resources with parent-child relationships (AIP-122, AIP-124):

### Resource Naming in Sequence Diagrams

Always use the full resource name in method signatures:

```plantuml
Controller -> Service: getBook(name="publishers/123/books/456")
Service -> Repository: findByName("publishers/123/books/456")
Repository -> DB: SELECT * FROM books WHERE publisher_id=123 AND book_id=456
```

### Parent Validation Pattern

```plantuml
Controller -> Service: createBook(parent="publishers/123", bookData)
Service -> Repository: validatePublisherExists("publishers/123")
alt Parent not found
    Service --> Controller: NOT_FOUND (parent)
else Parent exists
    Service -> Repository: save(book)
end
```
