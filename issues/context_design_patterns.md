# Issue #001: Context Design Patterns - Following Google ADK Best Practices

**📅 Created:** 2025-01-21  
**🏷️ Labels:** `architecture`, `design-decision`, `context`, `research`  
**👤 Assignee:** Development Team  
**⚡ Priority:** High  

---

## 🎯 **PROBLEM STATEMENT**

Currently, we have an unclear separation of responsibilities between:
- `spartacus_services/context.py` (Pydantic model for conversation state)
- `agentic_lib/base_agent.py` (Agent logic with OpenAI-specific conversation handling)

**Key Questions:**
1. What methods should belong to the `Context` class vs `BaseAgent`?
2. How should we handle conversation history manipulation?
3. What patterns does Google ADK use for similar scenarios?

---

## 🔍 **CURRENT STATE ANALYSIS**

### **Current Context Implementation:**
```python
class Context(BaseModel):
    message_history: List[Dict[str, Any]] = []
    session_id: Optional[str] = None
    # ... other fields
    
    # Basic utility methods
    def add_simple_user_message(self, content: str) -> None
    def clear_history(self) -> None  
    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]
```

### **Current BaseAgent Implementation:**
```python
class BaseAgent:
    def _add_assistant_message_to_history(self, context, content, tool_calls)
    def _add_tool_result_to_history(self, context, tool_call_id, result)
    # ... OpenAI-specific formatting logic
```

---

## 📚 **RESEARCH: GOOGLE ADK PATTERNS (COMPLETED ✅)**

### **✅ Google ADK Architecture Analysis:**

#### **1. Context Hierarchy Pattern:**
```python
# Google ADK follows a hierarchical context pattern:

# 1. InvocationContext (Full Access)
class InvocationContext:
    """Comprehensive context for agent core logic"""
    session: Session
    agent: Agent
    invocation_id: str
    user_content: Content
    # Services: memory_service, artifact_service, session_service

# 2. CallbackContext (Read/Write State + Artifacts)  
class CallbackContext(ReadonlyContext):
    """For agent/model callbacks - can modify state"""
    state: Dict[str, Any]  # MUTABLE
    def save_artifact(filename, part) -> int
    def load_artifact(filename) -> Part

# 3. ToolContext (Full Tool Capabilities)
class ToolContext(CallbackContext):
    """For tools - everything + auth + memory"""
    function_call_id: str
    def request_credential(auth_config) -> None
    def get_auth_response(auth_config) -> AuthCredential
    def search_memory(query) -> SearchResults
    def list_artifacts() -> List[str]

# 4. ReadonlyContext (Base - Read Only)
class ReadonlyContext:
    """Base context - read-only access"""
    invocation_id: str
    agent_name: str
    state: Dict[str, Any]  # READ-ONLY VIEW
```

#### **2. Separation of Concerns:**
- **Context = Data Container + Basic Operations**
- **Agent = Complex Business Logic**
- **Services = External Dependencies**

#### **3. Google ADK Key Principles:**
1. **Layered Permissions**: More privileged contexts for more complex operations
2. **Automatic State Tracking**: Changes via context are auto-persisted
3. **Service Injection**: External services available through context
4. **Platform Agnostic**: Context doesn't contain platform-specific logic

---

## 🎯 **DESIGN OPTIONS TO EVALUATE**

### **Option A: Minimal Context (Data Only) - ❌ Not Google ADK Pattern**
```python
class Context(BaseModel):
    """Pure data container - no business logic"""
    message_history: List[Dict[str, Any]] = []
    session_id: Optional[str] = None
    
    # Only basic data access (Google ADK has MORE than this)
    def get_messages(self) -> List[Dict[str, Any]]
    def set_messages(self, messages: List[Dict[str, Any]]) -> None
```

### **Option B: Smart Context (Data + Basic Operations) - ✅ Matches Google ADK**
```python
class Context(BaseModel):
    """Data container + basic operations (Google ADK pattern)"""
    message_history: List[Dict[str, Any]] = []
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    # ✅ Basic, platform-agnostic operations (like Google ADK)
    def add_user_message(self, content: str) -> None
    def add_assistant_message(self, content: str) -> None  
    def clear_history(self) -> None
    def get_last_messages(self, n: int) -> List[Dict[str, Any]]
    
    # ✅ State management (like Google ADK CallbackContext)
    def get_state_value(self, key: str, default: Any = None) -> Any
    def set_state_value(self, key: str, value: Any) -> None
```

### **Option C: Layered Context (Data + Adapters) - ✅ Advanced Google ADK Pattern**
```python
class SpartacusContext(BaseModel):
    """Base context - matches Google ADK ReadonlyContext"""
    message_history: List[Dict[str, Any]] = []
    session_id: Optional[str] = None
    state: Dict[str, Any] = {}
    
    # Basic operations only
    def get_last_messages(self, n: int) -> List[Dict[str, Any]]
    def clear_history(self) -> None

class AgentContext(SpartacusContext):
    """Agent-level context - matches Google ADK CallbackContext"""
    
    # Mutable state operations
    def add_user_message(self, content: str) -> None
    def add_assistant_message(self, content: str) -> None
    def update_state(self, key: str, value: Any) -> None

class OpenAIAgentAdapter:
    """Platform-specific operations - keeps Context clean"""
    @staticmethod
    def add_assistant_message_with_tools(
        context: AgentContext, 
        content: str, 
        tool_calls: List[Any]
    ) -> None:
        # OpenAI-specific formatting logic here
    
    @staticmethod 
    def add_tool_result(
        context: AgentContext,
        tool_call_id: str, 
        result: str
    ) -> None:
        # OpenAI-specific tool result formatting
```

---

## 📊 **EVALUATION CRITERIA (Updated with Google ADK Research)**

| Criteria | Weight | Option A | Option B | Option C |
|----------|--------|----------|----------|----------|
| **Google ADK Alignment** | 30% | ❌ Too minimal | ✅ Good match | ✅ Perfect match |
| **Maintainability** | 25% | ✅ Simple | ✅ Balanced | ⚠️ More complex |
| **Extensibility** | 20% | ❌ Limited | ✅ Good | ✅ Excellent |
| **Simplicity** | 15% | ✅ Very simple | ✅ Simple | ⚠️ Complex |
| **Performance** | 10% | ✅ Fast | ✅ Fast | ⚠️ Overhead |

### **Score Summary:**
- **Option A**: ❌ 6/10 - Too minimal, doesn't match Google ADK patterns
- **Option B**: ✅ 8.5/10 - Good balance, matches Google ADK CallbackContext  
- **Option C**: ✅ 8/10 - Perfect pattern match but added complexity

---

## 🎯 **RECOMMENDED APPROACH: Option B (Smart Context)**

### **Why Option B Wins:**
1. **✅ Matches Google ADK CallbackContext pattern** exactly
2. **✅ Right balance** of functionality vs simplicity  
3. **✅ Platform-agnostic** basic operations in Context
4. **✅ Complex logic stays in BaseAgent** (OpenAI formatting)
5. **✅ Easy to test** and mock
6. **✅ Future-proof** for multiple LLM providers

### **Recommended Implementation:**
```python
class Context(BaseModel):
    """Spartacus Context - inspired by Google ADK CallbackContext"""
    
    # Core data (like Google ADK)
    message_history: List[Dict[str, Any]] = Field(default_factory=list)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    
    # State management (like Google ADK)
    state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Basic message operations (platform-agnostic)
    def add_user_message(self, content: str) -> None:
        """Add basic user message to history"""
        self.message_history.append({
            "role": "user", 
            "content": content
        })
    
    def add_assistant_message(self, content: str) -> None:
        """Add basic assistant message to history""" 
        self.message_history.append({
            "role": "assistant",
            "content": content
        })
    
    # Utility methods
    def clear_history(self) -> None:
        self.message_history = []
    
    def get_last_messages(self, n: int) -> List[Dict[str, Any]]:
        return self.message_history[-n:] if self.message_history else []
    
    # State management (like Google ADK)
    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value
```

### **BaseAgent keeps complex logic:**
```python
class BaseAgent:
    # ✅ OpenAI-specific complex operations stay here
    def _add_assistant_message_to_history(self, context: Context, content: str, tool_calls: List[Any]):
        """Complex OpenAI-specific formatting"""
        # Handle tool_call.id, tool_call.function.name etc.
    
    def _add_tool_result_to_history(self, context: Context, tool_call_id: str, result: str):
        """Complex OpenAI tool result formatting"""
        # Handle tool_call_id linking etc.
```

---

## 💬 **DISCUSSION OUTCOME**

### **✅ DECISION: Implement Option B**

**Rationale:**
1. **Perfect alignment with Google ADK patterns**
2. **Clean separation**: Basic ops in Context, complex ops in BaseAgent
3. **Extensible**: Can add more providers without changing Context
4. **Testable**: Easy to mock and unit test
5. **Future-proof**: Follows industry best practices

---

## 📝 **ACTION ITEMS**

- [x] **Research Lead**: Complete Google ADK pattern analysis ✅
- [ ] **Development Team**: Implement Option B Context redesign
- [ ] **Testing**: Update tests to use new Context API
- [ ] **Documentation**: Update architecture docs with Google ADK alignment
- [ ] **Migration**: Provide clean migration path from current implementation

---

## 🔗 **RELATED ISSUES**

- #002: FastAPI Backend Integration (depends on this decision)
- #003: Multi-LLM Provider Support (benefits from this pattern)
- #004: Context Persistence Strategy (aligns with Google ADK state management)

---

## 📋 **ACCEPTANCE CRITERIA**

✅ **Decision Criteria Met:**
- [x] Google ADK patterns researched and documented ✅
- [x] All options evaluated against criteria matrix ✅
- [x] Team consensus reached on preferred approach ✅ (Option B)
- [ ] Implementation plan created
- [ ] Breaking changes documented

✅ **Implementation Ready:**
- [ ] Context redesigned following Option B
- [ ] BaseAgent updated to use new Context API
- [ ] Tests updated to reflect new patterns
- [ ] Documentation updated with Google ADK alignment notes

---

**📞 Next Review:** Implementation sprint planning  
**⏰ Target Resolution:** Before Phase 2 FastAPI backend begins  
**🎯 Success Metric:** Context design matches Google ADK CallbackContext pattern 