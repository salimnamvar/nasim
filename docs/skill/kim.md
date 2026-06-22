---
name: csr-rod-sequence-diagram
description: >
  Design UML Sequence Diagrams for backend systems that follow the Controller-Service-Repository (CSR) 
  architectural pattern and Resource-Oriented Design (RoD) based on Google AIP (API Improvement Proposals). 
  Use when creating, generating, or modeling sequence diagrams for RESTful API interactions, especially 
  when the system architecture uses CSR layers and resource-oriented endpoints. Supports PlantUML output 
  format. Covers standard methods (Get, List, Create, Update, Delete), custom methods, error handling, 
  pagination, state transitions, and field-level interactions across Controller, Service, and Repository 
  layers.
---

# CSR-RoD Sequence Diagram Skill

Design UML Sequence Diagrams that map Resource-Oriented Design (RoD) API operations to Controller-Service-Repository (CSR) architecture layers, outputting PlantUML syntax.

## Core Principles

- **Vertical axis = time** (top to bottom)
- **Horizontal axis = participants** (left to right: external actor → Controller → Service → Repository)
- **Solid arrowhead (→)** = synchronous call (sender waits)
- **Open arrowhead (→>)** = asynchronous call (sender continues)
- **Dashed arrow (-->)** = return/response message
- **Activation bar (rectangle on lifeline)** = object is active/processing
- Each lifeline represents a participant in the CSR + RoD interaction

## Standard CSR Layer Responsibilities

| Layer | Role | RoD Mapping |
|-------|------|-------------|
| **Client/Actor** | Initiates HTTP requests | API consumer (browser, mobile, service) |
| **Controller** | Receives HTTP requests, validates input, routes to Service, returns HTTP responses | HTTP verb + resource URI handler |
| **Service** | Contains business logic, orchestrates operations, applies rules, transforms data | Standard method logic (Get/List/Create/Update/Delete/Custom) |
| **Repository** | Data access abstraction, persists/retrieves entities from database | Resource storage/retrieval operations |
| **Database** | Actual data store | Resource persistence |

## Workflow: Creating a CSR-RoD Sequence Diagram

Follow these steps:

1. **Identify the RoD operation** — Determine which standard method (Get/List/Create/Update/Delete) or custom method applies. See `references/rod-patterns.md` for RoD patterns.
2. **Map to CSR layers** — Determine how the operation flows through Controller → Service → Repository. See `references/csr-patterns.md` for layer interaction patterns.
3. **Add error handling** — Include alt/else fragments for error paths (validation, not found, conflict). See AIP-193 error patterns in `references/rod-patterns.md`.
4. **Add state checks** — For stateful resources, include state validation gates. See AIP-216 patterns.
5. **Write PlantUML** — Use the syntax reference in `references/plantuml-syntax.md`.
6. **Validate completeness** — Check against the checklist below.

## Completion Checklist

Every CSR-RoD sequence diagram MUST include:

- [ ] All CSR layers participating in the flow (Client, Controller, Service, Repository, Database)
- [ ] Correct HTTP verb and resource URI mapping (per AIP-131 through AIP-135)
- [ ] Activation bars on all layers during processing
- [ ] Input validation in Controller
- [ ] Business logic execution in Service
- [ ] Data access in Repository
- [ ] Response path back to Client
- [ ] Error handling (at minimum: validation error, not found, server error)

Every CSR-RoD sequence diagram SHOULD include:

- [ ] Authentication/authorization check (opt block)
- [ ] Pagination handling (for List operations, per AIP-158)
- [ ] State transition check (for stateful resources, per AIP-216)
- [ ] Field behavior annotations (per AIP-203: REQUIRED, OPTIONAL, OUTPUT_ONLY, INPUT_ONLY)

## Quick-Reference: RoD Standard Methods → CSR Flow

### Get (AIP-131)
```
Client → Controller: GET /v1/{resource.name}
Controller → Service: getResource(name)
Service → Repository: findByName(name)
Repository --> Service: Resource (or null)
alt Resource not found
    Service --> Controller: NOT_FOUND error (AIP-193)
    Controller --> Client: 404 Not Found
else Resource found
    Service --> Controller: Resource
    Controller --> Client: 200 OK + Resource
end
```

### List (AIP-132)
```
Client → Controller: GET /v1/{parent}/resources?page_size=N
Controller → Service: listResources(parent, pageSize, pageToken)
Service → Repository: findByParent(parent, pageable)
Repository --> Service: List<Resource> + nextPageToken
Service --> Controller: ListResourcesResponse
Controller --> Client: 200 OK + {resources, nextPageToken}
```

### Create (AIP-133)
```
Client → Controller: POST /v1/{parent}/resources
Controller → Controller: validate request body
Controller → Service: createResource(parent, Resource)
Service → Service: apply business rules/defaults
Service → Repository: save(Resource)
Repository --> Service: persisted Resource (with generated name/ID)
Service --> Controller: Resource
Controller --> Client: 200 OK + Resource (or 201 Created)
```

### Update (AIP-134)
```
Client → Controller: PATCH /v1/{resource.name}
Controller → Controller: validate request body + update_mask
Controller → Service: updateResource(Resource, updateMask)
Service → Repository: findByName(name)
alt Resource not found
    Service --> Controller: NOT_FOUND error
else Resource exists
    Service → Service: apply update mask, validate state transition
    Service → Repository: save(updated Resource)
    Repository --> Service: persisted Resource
    Service --> Controller: Resource
    Controller --> Client: 200 OK + Resource
end
```

### Delete (AIP-135)
```
Client → Controller: DELETE /v1/{resource.name}
Controller → Service: deleteResource(name)
Service → Repository: findByName(name)
alt Resource not found
    Service --> Controller: NOT_FOUND (idempotent: may return success)
else Resource exists
    alt soft delete supported (AIP-164)
        Service → Repository: markDeleted(name)
    else hard delete
        Service → Repository: delete(name)
    end
    Repository --> Service: success
    Service --> Controller: success
    Controller --> Client: 204 No Content (or 200 OK)
end
```

## PlantUML Participant Declaration Convention

Always declare participants in this order:

```plantuml
actor Client
participant "ResourceController" as Controller
participant "ResourceService" as Service
participant "ResourceRepository" as Repository
database "Database" as DB
```

## Detailed References

- **CSR layer patterns**: See `references/csr-patterns.md` for detailed interaction patterns across layers, including DTO transformation, validation sequencing, and error propagation.
- **RoD patterns**: See `references/rod-patterns.md` for standard/custom methods, resource naming, pagination, errors, state management, and field behavior.
- **PlantUML syntax**: See `references/plantuml-syntax.md` for complete PlantUML sequence diagram syntax reference.
- **Worked examples**: See `references/examples.md` for complete, ready-to-use PlantUML diagram examples covering all standard methods.
