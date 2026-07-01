# NASIM Technical Architecture Audit

## Detailed Analysis of C4 Design vs Current Implementation

## 1. Controller Layer Analysis

### Current Implementation Issues

**Problem 1: Multiple Entry Points Without Central Coordination**
- `cli/entrypoints.py`: `serve()` function starts FastAPI server
- `api/app.py`: FastAPI application with routes
- `messaging/node_runner.py`: Messaging node execution
- No single AgentController to coordinate all adapters

**Problem 2: Adapter Pattern Not Properly Implemented**
- CLI adapter functionality mixed in `cli/managed/manager.py`
- HTTP adapter functionality in `api/routes.py` 
- No dedicated MCP adapter implementation
- Adapters don't follow consistent interface pattern

### Recommended Implementation

```python
# controllers/agent_controller.py
class AgentController:
    def __init__(self, service_registry: ServiceRegistry):
        self.services = service_registry
        
    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        # Central validation and routing
        validated_request = self._validate_request(request)
        
        # Route to appropriate service
        if request.request_type == RequestType.TASK:
            return await self.services.task_service.handle_task(validated_request)
        elif request.request_type == RequestType.TOOL:
            return await self.services.tool_service.execute_tool(validated_request)
        # ... other request types
    
    def _validate_request(self, request: AgentRequest) -> ValidatedRequest:
        # Common validation logic
        pass

# adapters/cli_adapter.py
class CLIAdapter:
    def __init__(self, agent_controller: AgentController):
        self.controller = agent_controller
        
    def handle_cli_command(self, command: str) -> str:
        # Convert CLI command to AgentRequest
        request = self._parse_cli_command(command)
        # Delegate to controller
        response = self.controller.handle_request(request)
        # Convert response to CLI format
        return self._format_cli_response(response)

# adapters/http_adapter.py  
class HTTPAdapter:
    def __init__(self, agent_controller: AgentController):
        self.controller = agent_controller
        
    async def handle_http_request(self, request: Request) -> Response:
        # Convert HTTP request to AgentRequest
        agent_request = self._parse_http_request(request)
        # Delegate to controller
        agent_response = await self.controller.handle_request(agent_request)
        # Convert response to HTTP format
        return self._format_http_response(agent_response)
```

## 2. Service Layer Analysis

### Current Implementation Issues

**Problem 1: Business Logic Scattered Across Modules**
- Task orchestration in `messaging/node_runner.py` and `messaging/workflow.py`
- Tool execution in `api/web_server_tools.py` and provider implementations
- Session management mixed with messaging infrastructure
- No clear service boundaries

**Problem 2: Missing Critical Services**
- No SafetyService for validation and security
- No ContextService for context management
- No EvaluationService for task quality checking
- ConfigService functionality mixed with settings management

### Recommended Service Structure

```python
# services/task_service.py
class TaskService:
    def __init__(self, tool_service: ToolService, 
                 context_service: ContextService, 
                 evaluation_service: EvaluationService):
        self.tool_service = tool_service
        self.context_service = context_service
        self.evaluation_service = evaluation_service
        
    async def execute_task(self, task_request: TaskRequest) -> TaskResponse:
        # Agentic loop implementation
        context = await self.context_service.build_context(task_request)
        
        while not self.evaluation_service.is_complete(task_request):
            # LLM call with context
            llm_response = await self._call_llm(context)
            
            # Tool execution if needed
            if llm_response.requires_tools:
                tool_results = await self.tool_service.execute_tools(
                    llm_response.tool_calls
                )
                context = self.context_service.update_context(tool_results)
            
            # Evaluation and retry logic
            if await self.evaluation_service.evaluate_response(llm_response):
                break
                
        return self._build_final_response(context)

# services/safety_service.py
class SafetyService:
    def __init__(self, config: SafetyConfig):
        self.config = config
        self.scanners = [
            InjectionScanner(),
            PermissionScanner(),
            EgressScanner()
        ]
        
    async def validate_action(self, action: AgentAction) -> ValidationResult:
        # Run all safety checks
        for scanner in self.scanners:
            result = scanner.scan(action)
            if not result.is_safe:
                return ValidationResult(safe=False, reason=result.reason)
                
        return ValidationResult(safe=True)

# services/context_service.py
class ContextService:
    def __init__(self, memory_repository: MemoryRepository, 
                 repo_intelligence: RepoIntelligenceRepository):
        self.memory_repo = memory_repository
        self.repo_intel = repo_intelligence
        
    async def build_context(self, request: TaskRequest) -> Context:
        # Context pipeline: memory + current task + repo intelligence
        base_context = self._get_base_context()
        memory_context = await self.memory_repo.get_relevant_memory(request)
        repo_context = await self.repo_intel.get_codebase_context(request)
        
        return self._combine_contexts([base_context, memory_context, repo_context])
        
    async def update_context(self, new_info: ContextUpdate) -> Context:
        # Context truncation and distillation
        updated = self._add_to_context(self.current_context, new_info)
        return await self._truncate_context(updated)
```

## 3. Repository Layer Analysis

### Current Implementation Issues

**Problem 1: Inconsistent Repository Pattern**
- `messaging/session.py` has SessionStore (good repository pattern)
- Filesystem operations scattered throughout codebase
- No consistent interface for repositories
- Direct data access from services and API routes

**Problem 2: Missing Critical Repositories**
- No LLMRepository for model routing
- No SandboxRepository for isolated execution
- No EditStrategyRepository for safe file operations
- No RepoIntelligenceRepository for codebase analysis

### Recommended Repository Structure

```python
# repositories/base_repository.py
class BaseRepository(ABC):
    """Base class for all repositories."""
    
    @abstractmethod
    async def get(self, key: str) -> Any:
        pass
        
    @abstractmethod
    async def save(self, data: Any) -> str:
        pass
        
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

# repositories/llm_repository.py
class LLMRepository(BaseRepository):
    def __init__(self, provider_registry: ProviderRegistry):
        self.providers = provider_registry
        self.router = ModelRouter()
        
    async def complete(self, request: LLMRequest) -> LLMResponse:
        # Model selection and routing
        provider = self.router.select_provider(request)
        
        # Streaming response handling
        try:
            response = await provider.complete(request)
            return self._process_response(response)
        except ProviderError as e:
            # Fallback chain
            fallback_provider = self.router.get_fallback(request)
            return await fallback_provider.complete(request)

# repositories/filesystem_repository.py
class FilesystemRepository(BaseRepository):
    def __init__(self, base_path: Path):
        self.base_path = base_path
        
    async def read_file(self, file_path: str) -> FileContent:
        # Safe file reading with validation
        full_path = self._validate_path(file_path)
        try:
            content = full_path.read_text()
            return FileContent(path=file_path, content=content)
        except Exception as e:
            raise FilesystemError(f"Failed to read {file_path}: {e}")
            
    async def write_file(self, file_path: str, content: str) -> WriteResult:
        # Safe file writing with validation
        full_path = self._validate_path(file_path)
        try:
            full_path.write_text(content)
            return WriteResult(success=True, path=file_path)
        except Exception as e:
            raise FilesystemError(f"Failed to write {file_path}: {e}")

# repositories/sandbox_repository.py
class SandboxRepository(BaseRepository):
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        
    async def execute_command(self, command: str, 
                            cwd: str = "/", 
                            env: dict = None) -> SandboxResult:
        # Isolated command execution
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                env=env or {},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            return SandboxResult(
                success=process.returncode == 0,
                stdout=stdout.decode(),
                stderr=stderr.decode(),
                exit_code=process.returncode
            )
            
        except asyncio.TimeoutError:
            raise SandboxTimeout(f"Command timed out after {self.timeout}s")
        except Exception as e:
            raise SandboxError(f"Sandbox execution failed: {e}")
```

## 4. Dependency Injection and Composition

### Current Issues
- Tight coupling between components
- No clear dependency injection pattern
- Services create their own dependencies
- Difficult to test and mock components

### Recommended Approach

```python
# composition/container.py
class ServiceContainer:
    def __init__(self, config: Settings):
        self.config = config
        self._services = {}
        self._repositories = {}
        
    def get_service(self, service_type: type) -> Any:
        if service_type not in self._services:
            self._services[service_type] = self._create_service(service_type)
        return self._services[service_type]
        
    def get_repository(self, repo_type: type) -> Any:
        if repo_type not in self._repositories:
            self._repositories[repo_type] = self._create_repository(repo_type)
        return self._repositories[repo_type]
        
    def _create_service(self, service_type: type) -> Any:
        if service_type == TaskService:
            return TaskService(
                tool_service=self.get_service(ToolService),
                context_service=self.get_service(ContextService),
                evaluation_service=self.get_service(EvaluationService)
            )
        elif service_type == ToolService:
            return ToolService(
                filesystem_repo=self.get_repository(FilesystemRepository),
                sandbox_repo=self.get_repository(SandboxRepository),
                # ... other dependencies
            )
        # ... other service types
        
    def _create_repository(self, repo_type: type) -> Any:
        if repo_type == SessionRepository:
            return SessionRepository(
                storage_path=self.config.session_storage_path
            )
        elif repo_type == LLMRepository:
            return LLMRepository(
                provider_registry=self._create_provider_registry()
            )
        # ... other repository types

# Main application composition
class NASIMApplication:
    def __init__(self, config: Settings):
        self.container = ServiceContainer(config)
        self.agent_controller = AgentController(
            service_registry=self.container
        )
        
        # Initialize adapters
        self.cli_adapter = CLIAdapter(self.agent_controller)
        self.http_adapter = HTTPAdapter(self.agent_controller)
        self.mcp_adapter = MCPAdapter(self.agent_controller)
```

## 5. Error Handling and Recovery

### Current Issues
- Inconsistent error handling across modules
- No centralized error recovery mechanism
- Errors bubble up without proper context
- No retry logic for transient failures

### Recommended Error Handling

```python
# errors/base_errors.py
class NASIMError(Exception):
    """Base class for all NASIM errors."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}
        self.timestamp = datetime.utcnow()
        
    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "message": str(self),
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }

class ValidationError(NASIMError):
    """Input validation failed."""
    pass

class ProviderError(NASIMError):
    """LLM provider failure."""
    pass

class SandboxError(NASIMError):
    """Sandbox execution failed."""
    pass

# services/error_handler.py
class ErrorHandler:
    def __init__(self, config: ErrorHandlingConfig):
        self.config = config
        self.retry_strategies = {
            ProviderError: ExponentialBackoffStrategy(max_retries=3),
            SandboxError: LinearBackoffStrategy(max_retries=2),
            # ... other error types
        }
        
    async def handle_error(self, error: NASIMError, 
                          context: dict = None) -> ErrorResolution:
        """Handle errors with appropriate recovery strategies."""
        error_context = {**(context or {}), **error.context}
        
        # Log the error
        self._log_error(error, error_context)
        
        # Apply retry strategy if available
        if retry_strategy := self.retry_strategies.get(type(error)):
            return await retry_strategy.attempt_recovery(error, error_context)
            
        # No recovery available
        return ErrorResolution(
            recovered=False,
            action="fail",
            message=f"Unrecoverable error: {error}"
        )
        
    def _log_error(self, error: NASIMError, context: dict):
        """Log error with full context."""
        log_data = {
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "timestamp": error.timestamp.isoformat()
        }
        logger.error("NASIM Error: {error_type}", **log_data)

# Example usage in services
class TaskService:
    def __init__(self, error_handler: ErrorHandler, ...):
        self.error_handler = error_handler
        # ... other dependencies
        
    async def execute_task(self, request: TaskRequest):
        try:
            # Normal task execution
            return await self._execute_task_internal(request)
            
        except NASIMError as e:
            resolution = await self.error_handler.handle_error(e, {
                "task_id": request.task_id,
                "step": "execution"
            })
            
            if resolution.recovered:
                return await self._execute_task_internal(request)
            else:
                raise TaskFailedError(
                    f"Task failed after recovery attempt: {e}",
                    context={
                        "original_error": e.to_dict(),
                        "recovery_attempt": resolution.action
                    }
                )
```

## 6. Monitoring and Observability

### Current Issues
- Limited monitoring capabilities
- No centralized metrics collection
- Inconsistent logging patterns
- No health checks for critical components

### Recommended Monitoring System

```python
# monitoring/metrics.py
class MetricsCollector:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)
        
    def increment(self, metric_name: str, value: int = 1):
        self.counters[metric_name] += value
        
    def time(self, metric_name: str, duration: float):
        self.timers[metric_name].append(duration)
        
    def set_gauge(self, metric_name: str, value: float):
        self.gauges[metric_name] = value
        
    def get_snapshot(self) -> dict:
        return {
            "counters": dict(self.counters),
            "timers": {k: self._calculate_stats(v) for k, v in self.timers.items()},
            "gauges": dict(self.gauges)
        }
        
    def _calculate_stats(self, values: list) -> dict:
        return {
            "count": len(values),
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "avg": sum(values) / len(values) if values else 0
        }

# monitoring/health_checks.py
class HealthChecker:
    def __init__(self, repositories: list):
        self.repositories = repositories
        self.checks = [
            ("llm_health", self._check_llm_health),
            ("filesystem_health", self._check_filesystem_health),
            ("sandbox_health", self._check_sandbox_health),
            # ... other health checks
        ]
        
    async def perform_health_check(self) -> HealthStatus:
        results = {}
        for check_name, check_func in self.checks:
            try:
                result = await check_func()
                results[check_name] = HealthCheckResult(
                    status="healthy" if result else "unhealthy",
                    details={"check": check_name}
                )
            except Exception as e:
                results[check_name] = HealthCheckResult(
                    status="error",
                    details={"check": check_name, "error": str(e)}
                )
                
        overall_status = "healthy" if all(
            r.status == "healthy" for r in results.values()
        ) else "degraded"
        
        return HealthStatus(
            status=overall_status,
            checks=results,
            timestamp=datetime.utcnow()
        )
        
    async def _check_llm_health(self) -> bool:
        # Test LLM connectivity
        try:
            llm_repo = self.repositories.get(LLMRepository)
            test_request = LLMRequest(prompt="ping", max_tokens=1)
            response = await llm_repo.complete(test_request)
            return response.success
        except Exception:
            return False

# monitoring/logging.py
class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
    def log_event(self, event_type: str, 
                  level: str = "info", 
                  context: dict = None):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "event": event_type,
            "level": level,
            ** (context or {})
        }
        
        getattr(self.logger, level)(json.dumps(log_record))
        
    def log_task_event(self, task_id: str, 
                      event_type: str, 
                      context: dict = None):
        self.log_event(event_type, context={
            "task_id": task_id,
            ** (context or {})
        })
```

## Implementation Roadmap

### Phase 1: Core Architecture (4-6 weeks)
1. **Week 1-2**: Implement AgentController and adapter refactoring
2. **Week 3-4**: Create base service classes (TaskService, ToolService, SessionService)
3. **Week 5-6**: Implement repository layer with base classes and key repositories

### Phase 2: Service Layer Completion (3-4 weeks)
1. **Week 1**: Implement SafetyService, ContextService, EvaluationService
2. **Week 2**: Enhance ToolService with registry and validation
3. **Week 3-4**: Implement error handling and recovery mechanisms

### Phase 3: External System Integration (4-6 weeks)
1. **Week 1-2**: Implement SandboxRepository and FilesystemRepository
2. **Week 3-4**: Develop RepoIntelligenceRepository with code analysis
3. **Week 5-6**: Implement MCPRepository and enhance LLM routing

### Phase 4: Monitoring and Testing (3-4 weeks)
1. **Week 1**: Implement monitoring and observability
2. **Week 2**: Add comprehensive logging and metrics
3. **Week 3-4**: Test suite enhancement and integration testing

## Conclusion

The current implementation provides a solid foundation but requires significant architectural refactoring to achieve the C4 design vision. By systematically implementing the missing components and following the recommended patterns, NASIM can evolve into a robust, maintainable, and extensible system that fully realizes its architectural potential.

The phased approach allows for incremental improvement while maintaining system stability, with each phase building upon the previous one to create a cohesive, well-architected AI coding assistant.