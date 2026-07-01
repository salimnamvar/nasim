# NASIM Architecture Audit: C4 Design vs Current Implementation

## Executive Summary

This audit compares the C4 architectural design of NASIM with the current implementation in the free-claude-code codebase. The analysis follows the CAR (Challenge-Action-Result) framework to identify gaps, opportunities for enhancement, and recommendations for aligning the implementation with the target architecture.

## C4 Architecture Overview

The C4 design specifies a clean 3-layer CSR (Controller-Service-Repository) architecture:

1. **Controller Layer**: CLIAdapter, HTTPAdapter, MCPAdapter → AgentController
2. **Service Layer**: TaskService, ToolService, SessionService, ConfigService, SafetyService, ContextService, EvaluationService
3. **Repository Layer**: 13 different repositories for data access
4. **Data Stores**: Session, Memory, WireLog, Config stores

## Current Implementation Analysis

### 1. Controller Layer Analysis

**Challenge**: The current implementation has a fragmented controller layer with multiple entry points and inconsistent routing.

**Current State**:
- CLI entry via `cli/entrypoints.py` with `serve()` and `init()` functions
- HTTP entry via `api/app.py` with FastAPI routes
- No clear AgentController convergence point
- Multiple adapters exist but are not properly separated:
  - CLI adapter functionality in `cli/managed/manager.py`
  - HTTP adapter functionality in `api/routes.py`
  - No dedicated MCP adapter found

**Action Required**:
- Create a unified AgentController class that serves as the single entry point
- Refactor CLI, HTTP, and MCP adapters to delegate to AgentController
- Implement proper adapter pattern with clear separation of concerns

**Result**: Unified request handling with consistent validation and routing

### 2. Service Layer Analysis

**Challenge**: Service layer is fragmented and mixed with other concerns.

**Current State**:
- Task orchestration logic scattered across `messaging/node_runner.py`, `messaging/workflow.py`
- Tool service functionality in `api/web_server_tools.py` and provider tool implementations
- Session management in `messaging/session.py` (more repository-like)
- Config service functionality in `config/settings.py` and `api/admin_config.py`
- No dedicated SafetyService, ContextService, or EvaluationService classes
- Business logic mixed with API routes and messaging infrastructure

**Action Required**:
- Create dedicated service classes for each domain:
  - TaskService: Agentic loop, subagent orchestration
  - ToolService: Tool registry, validation, execution
  - SessionService: Session lifecycle management
  - ConfigService: Configuration loading and validation
  - SafetyService: Permission gating, injection scanning
  - ContextService: Context pipeline and management
  - EvaluationService: Task evaluation and quality checks
- Extract business logic from API routes and messaging infrastructure

**Result**: Clear separation of concerns with well-defined service boundaries

### 3. Repository Layer Analysis

**Challenge**: Repository layer is partially implemented but inconsistent.

**Current State**:
- SessionRepository functionality in `messaging/session.py` (SessionStore class)
- ConfigRepository functionality in `config/` module
- FilesystemRepository functionality scattered across file I/O operations
- No dedicated LLMRepository, SandboxRepository, EditStrategyRepository, etc.
- Direct data access from services and API routes
- Some repository patterns exist but not consistently applied

**Action Required**:
- Create dedicated repository classes for each data access concern:
  - SessionRepository: Message persistence
  - HistoryRepository: Snapshots and revert index
  - ConfigRepository: Configuration management
  - MemoryRepository: Cross-session knowledge
  - LLMRepository: LLM API calls and model routing
  - FilesystemRepository: Host filesystem I/O
  - SandboxRepository: Sandboxed command execution
  - EditStrategyRepository: Diff staging and application
  - GitRepository: Git operations
  - MCPRepository: MCP extension tools
  - RepoIntelligenceRepository: Codebase intelligence
  - WebRepository: Web fetch operations
  - WireLogRepository: Interaction logging
- Ensure all data access goes through repositories

**Result**: Consistent data access patterns with proper abstraction

### 4. Data Store Analysis

**Challenge**: Data stores are implemented but not properly abstracted.

**Current State**:
- Session Store: JSONL files in `~/.nasim/sessions/`
- Memory Store: JSON + embeddings in `~/.nasim/memory/`
- Wire Log Store: JSONL append-only logs
- Config Store: YAML and environment variables
- Direct file system access throughout codebase
- No consistent abstraction layer

**Action Required**:
- Create proper data store abstractions
- Ensure all file access goes through repository layer
- Implement consistent error handling for data operations

**Result**: Reliable data persistence with proper error handling

### 5. External System Integration Analysis

**Challenge**: External system integrations are implemented but not properly abstracted.

**Current State**:
- LLM Backend: Implemented via `providers/` module with litellm integration
- Host Filesystem: Direct pathlib usage throughout
- Sandbox Runtime: Some subprocess usage but no dedicated sandbox
- Web: Implemented via `api/web_tools/`
- MCP Server: No dedicated MCP server implementation found
- Git Repository: Some git operations but no dedicated repository
- Repo Intelligence: No dedicated intelligence backend

**Action Required**:
- Create proper abstractions for all external systems
- Implement dedicated sandbox runtime with proper isolation
- Develop repo intelligence backend (tree-sitter, LSP, embeddings)
- Implement MCP server for extension tools

**Result**: Reliable external system integration with proper error handling

## Architectural Gaps and Enhancement Opportunities

### 1. Missing AgentController
**Challenge**: No central convergence point for all adapters
**Action**: Implement AgentController class as single entry point
**Result**: Consistent request handling and validation

### 2. Fragmented Service Layer
**Challenge**: Business logic scattered across multiple modules
**Action**: Create dedicated service classes with clear responsibilities
**Result**: Better separation of concerns and testability

### 3. Incomplete Repository Pattern
**Challenge**: Inconsistent data access patterns
**Action**: Implement complete repository layer with all required repositories
**Result**: Consistent data access with proper abstraction

### 4. Missing Safety Service
**Challenge**: No dedicated safety and validation layer
**Action**: Implement SafetyService with permission gating, injection scanning
**Result**: Improved security and reliability

### 5. Missing Context Service
**Challenge**: Context management scattered across messaging infrastructure
**Action**: Implement ContextService for context pipeline management
**Result**: Better context handling and memory management

### 6. Missing Evaluation Service
**Challenge**: No dedicated task evaluation and quality checking
**Action**: Implement EvaluationService for success checks, retries, quality management
**Result**: Improved task completion reliability

### 7. Missing External System Abstractions
**Challenge**: Direct integration with external systems without proper abstraction
**Action**: Implement proper abstractions for all external systems
**Result**: Better error handling and maintainability

## Recommendations for NASIM Enhancement

### Phase 1: Core Architecture Refactoring
1. **Implement AgentController** as central convergence point
2. **Create dedicated service classes** for each domain
3. **Implement complete repository layer** with all required repositories
4. **Refactor adapters** to use AgentController consistently

### Phase 2: Service Layer Enhancement
1. **Implement SafetyService** with comprehensive validation
2. **Implement ContextService** for advanced context management
3. **Implement EvaluationService** for task quality assurance
4. **Enhance ToolService** with better tool registry and validation

### Phase 3: External System Integration
1. **Implement dedicated SandboxRepository** with proper isolation
2. **Develop RepoIntelligenceRepository** with tree-sitter, LSP, embeddings
3. **Implement MCPRepository** for extension tools
4. **Enhance external system error handling** and retry logic

### Phase 4: Advanced Features
1. **Implement subagent orchestration** in TaskService
2. **Enhance persona management** capabilities
3. **Add advanced error recovery** mechanisms
4. **Implement comprehensive logging** and monitoring

## Conclusion

The current implementation shows good progress toward the C4 architecture but has significant gaps in the service and repository layers. By systematically implementing the missing components and refactoring existing code to follow the CSR pattern, NASIM can achieve better separation of concerns, improved maintainability, and enhanced functionality.

The recommended phased approach allows for incremental improvement while maintaining system stability. Each phase builds upon the previous one, ultimately resulting in a robust, well-architected system that fully realizes the C4 design vision.