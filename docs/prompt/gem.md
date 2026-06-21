This is an incredibly robust and well-structured prompt system. You have essentially codified a strict Software Architecture governance model. Treating diagrams as code and enforcing single-source-of-truth traceability are hallmarks of elite engineering teams.

Before we dive into improving the design principles, I need to ground our interaction in reality: **I am Gemini, a cloud-based AI.** I do not have a persistent local file system, I cannot write directly to a `~/.claude/` directory, I cannot install local git pre-commit hooks on your machine, and I cannot autonomously scan a local project directory like "NASIM" unless you paste or upload the code here.

However, I can act as your virtual Chief Architect. We can refine these rules to make them bulletproof, and I can generate the exact scripts, PlantUML diagrams, and C4 scaffolding you need so you can implement them in your NASIM repository.

Here is how we can elevate these skills and layers to truly reflect cutting-edge 2026 software design standards.

---

### **1. Enhancing the Design Layers**

Your current rules are textbook perfect. To make them pragmatic for modern, distributed, cloud-native systems, we need to inject **Domain-Driven Design (DDD)** and **Event-Driven Architecture (EDA)** principles.

#### **C4 Model Enhancements**

* **Map to DDD:** Explicitly map C4 elements to Domain-Driven Design concepts. A *Container* often maps to a Bounded Context. A *Component* often maps to an Aggregate Root or Domain Service. This bridges the gap between architecture and business logic.
* **The Deployment View:** C4’s often-ignored "Deployment Diagram" is critical today. Add a rule for **C4-Deployment**: Mapping Containers to infrastructure (e.g., Kubernetes Pods, AWS Lambdas) to capture security and networking zones.
* **Deprecate Level 4 (Code):** Instead of making it optional, actively discourage manual Level 4 diagrams. Mandate that code-level architecture (Level 4) must be dynamically generated from code using tools like ArchUnit or code-to-UML generators. Manual updates at this level cause synchronization drift.

#### **Use Case (UC) Enhancements**

* **Bind to BDD (Behavior-Driven Development):** Pure UML Use Cases can become disconnected from testing. Add a rule that every Use Case must map 1:1 with a `Given-When-Then` Gherkin feature file.
* **API-First Contracts:** For headless systems, an "Actor" is often another system. Rule: If the Actor is a system, the Use Case must link directly to an OpenAPI/AsyncAPI endpoint or schema.

#### **State Machine (SM) Enhancements**

* **Event Sourcing & Immutability:** Update the rule to state that State Machines should govern *Aggregate Roots*. State transitions should ideally be modeled by emitting **Domain Events** rather than just changing a mutable database column.
* **Distributed Sagas:** Add a rule for complex distributed states. If a State Machine spans multiple C4 Containers (e.g., microservices), it must be modeled as a Saga (Choreography or Orchestration) with explicit *Compensating Actions* for failure states.

#### **Sequence Diagram (SQ) Enhancements**

* **Telemetry Traceability:** A modern Sequence Diagram is essentially a blueprint for Distributed Tracing. Rule: Sequence interactions across C4 Containers must include a correlation ID/Trace ID concept.
* **Message Broker Representation:** Explicitly define how event buses/message brokers (e.g., Kafka, RabbitMQ) are represented. They should be their own lifelines to clearly show asynchronous decoupling.

---

### **2. Modernizing the Automation & Tooling (Part 2)**

Writing custom Python scripts to parse codebase structures and Mermaid files from scratch is heavily prone to edge-case failures. I highly recommend updating your tooling rules to leverage industry standards:

* **Instead of `validate_architecture.py`:** Mandate the use of **ArchUnit** (Java/C#) or **Dependency Cruiser** (Node/JS). These tools let you write unit tests for your architecture (e.g., `layers("Controllers").shouldNotDependOn("Repositories")`).
* **Instead of purely text-based diagrams:** Mandate **Structurizr (Docs as Code)**. Structurizr allows you to define your C4 model in code once, and it automatically generates Context, Container, and Component diagrams that are mathematically guaranteed to stay in sync.
* **For `scaffold_states.py`:** Use established state machine libraries (like XState for TS/JS, or Spring State Machine for Java) instead of raw Enums, as they natively support hierarchical states and guards.

---

### **3. Executing on the "NASIM" Project (Part 3)**

Because I cannot see your local filesystem, I cannot scan the NASIM codebase directly. **To execute this immediately, I need you to provide the foundational data.** Please share a brief overview of NASIM by providing:

1. **The Core Goal:** What does NASIM do? (e.g., "It is an e-commerce order processing system").
2. **Tech Stack:** What language/framework are we using? (This dictates how I write the State Machine code and the architecture validation scripts).
3. **Core Entities:** What are the 2-3 most important nouns in your system? (e.g., Order, User, Payment).

Once you provide those details, I will immediately generate the C4 PlantUML architecture, the State Machine code implementation, the Sequence Diagram for your primary flow, and the `validate_architecture` script tailored exactly to your stack.

**What are the primary domain entities and the tech stack for NASIM so we can generate these artifacts right now?**