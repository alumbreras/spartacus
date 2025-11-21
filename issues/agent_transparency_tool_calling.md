# 🔍 ISSUE: Transparencia en Tool Calling del Agente

**Fecha:** 6 de Junio 2025  
**Prioridad:** Media 🟡  
**Categoría:** UX / Transparencia  
**Estado:** Abierto  
**Assigned to:** TBD  

## 📋 Descripción del Problema

Actualmente el agente es completamente opaco cuando ejecuta herramientas. El usuario no ve qué está haciendo, qué tools está llamando, ni qué resultados obtiene. Cuando alcanza el límite máximo de iteraciones, simplemente dice "I've reached the maximum number of reasoning steps" sin contexto.

### 🚨 Problemas Identificados

#### **Ejemplo Real - Búsqueda de Gmail:**
```
User: "Tengo algún correo de mi interiorista en la última semana?"
Spartacus: "I've reached the maximum number of reasoning steps. Please try rephrasing your request."
```

#### **Problemas de UX:**
- ❌ **Sin feedback visual**: Usuario no sabe si el agente está trabajando
- ❌ **Sin contexto de progreso**: No se ve qué tools se están llamando
- ❌ **Sin resultados intermedios**: No se muestran datos obtenidos de tools
- ❌ **Error messages opacos**: "Maximum reasoning steps" no explica QUÉ intentó hacer
- ❌ **Sin debugging info**: Imposible diagnosticar por qué falló

## 🎯 Objetivo

Implementar **transparencia completa** en el proceso de tool calling, similar a como lo hace Claude Desktop, mostrando:

1. **Tool calls en progreso** → "🔧 Buscando emails..."
2. **Resultados de tools** → Expandible con datos reales  
3. **Progreso de iteraciones** → "Iteración 3/20"
4. **Contexto en errores** → "Intenté buscar emails pero..."

## 🎨 Diseño UX Propuesto

### **Durante Tool Calling:**
```
🔧 Tool: gmail_search
   ↳ Buscando emails de "interiorista" en últimos 7 días...
   
✅ Resultados encontrados: 3 emails
   ▼ Ver detalles
   │ • Email 1: "Presupuesto cocina" - 5 Jun 2025
   │ • Email 2: "Reunión diseño" - 3 Jun 2025  
   │ • Email 3: "Materiales baño" - 1 Jun 2025
```

### **Durante Iteraciones:**
```
💭 Pensando... (Iteración 2/20)
🔧 Llamando herramienta: gmail_search
⏳ Procesando resultados...
✅ Análisis completado
```

### **En Error con Contexto:**
```
❌ Límite de iteraciones alcanzado (20/20)

🔍 Lo que intenté hacer:
• ✅ Busqué emails con "interiorista" 
• ✅ Encontré 3 resultados
• ❌ Falló al analizar contenido del email 2
• ❌ Reintenté análisis 15 veces

💡 Sugerencia: Inténtalo con un término más específico
```

## 🛠️ Implementación Técnica

### **Fase 1: Backend - Event Streaming**
```python
# Nuevos eventos para frontend
class AgentEvent(BaseModel):
    type: Literal["iteration", "tool_call", "tool_result", "thinking", "error"]
    iteration: int
    max_iterations: int
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
    tool_result: Optional[dict] = None
    message: str
```

### **Fase 2: WebSocket Real-time Updates**
```python
# spartacus_backend/api/chat.py
@app.websocket("/api/chat/stream/{chat_id}")
async def chat_stream(websocket: WebSocket, chat_id: str):
    await websocket.accept()
    
    async for event in agent_manager.run_agent_streaming(message, agent_id):
        await websocket.send_json(event.dict())
```

### **Fase 3: Frontend - Progressive UI**
```typescript
// spartacus_frontend/src/components/ToolCallDisplay.tsx
interface ToolCallDisplayProps {
  iteration: number;
  maxIterations: number;
  toolCalls: ToolCall[];
  currentStatus: "thinking" | "calling" | "processing" | "done";
}
```

## 📋 Tasks

### **Backend Implementation (Priority 1)**
- [ ] Crear sistema de eventos `AgentEvent` 
- [ ] Modificar `BaseAgent` para emitir eventos en cada step
- [ ] Implementar WebSocket endpoint para streaming
- [ ] Añadir eventos en `gmail_tools.py`:
  - `tool_call_start` con parámetros
  - `tool_call_result` con datos
  - `tool_call_error` con contexto

### **Frontend Implementation (Priority 2)** 
- [ ] Crear componente `ToolCallDisplay`
- [ ] Implementar WebSocket client para eventos real-time
- [ ] Añadir UI expandible para resultados de tools
- [ ] Crear indicador de progreso "Iteración X/20"
- [ ] Implementar mensajes de error con contexto

### **UX Enhancements (Priority 3)**
- [ ] Íconos específicos por tipo de tool:
  - 📧 `gmail_search`, `gmail_read`, `gmail_send`
  - 🤔 `final_answer`
  - ⚡ Otros tools futuros
- [ ] Animaciones de loading durante tool calls
- [ ] Collapse/expand automático de resultados largos
- [ ] Copy-to-clipboard para resultados de tools

### **Error Handling (Priority 4)**
- [ ] Context-aware error messages:
  - "Límite alcanzado mientras buscaba emails"
  - "Error de conexión durante gmail_search"
  - "No se encontraron resultados para 'interiorista'"
- [ ] Retry suggestions específicas por error
- [ ] Debug mode con logs completos

## 🔗 Referencias

- **Claude Desktop UX**: Ejemplo de transparencia en tool calling
- **OpenAI ChatGPT**: Muestra "browsing", "analyzing", etc.
- **Cursor**: Muestra steps de code generation
- **Nuestro BaseAgent**: `agentic_lib/base_agent.py` línea de iteraciones

## 📝 Casos de Uso a Cubrir

### **Gmail Search Success:**
```
🔧 gmail_search: Buscando "interiorista" (últimos 7 días)
✅ Encontrados 3 emails
📄 Leyendo email "Presupuesto cocina"...
✅ Análisis completado
```

### **Gmail Search No Results:**
```
🔧 gmail_search: Buscando "interiorista" 
❌ No se encontraron emails
💡 Sugerencia: Prueba con "interior", "diseño" o amplía el rango de fechas
```

### **Max Iterations with Context:**
```
⚠️ Proceso complejo - alcanzado límite de 20 iteraciones

🔍 Progreso completado:
• ✅ Busqué emails de interiorista (3 encontrados)
• ✅ Leí contenido de 2 emails 
• ⏳ Analizando el tercer email... [INTERRUMPIDO]

💡 Puedes preguntarme específicamente sobre los emails encontrados
```

## ⚡ Quick Wins

### **Implementación Mínima (MVP):**
1. Mostrar "🔧 Llamando a gmail_search..." 
2. Mostrar "✅ Encontrados X resultados"
3. Mostrar "💭 Iteración X/20" 
4. Error message: "Límite alcanzado buscando emails de interiorista"

### **Full Implementation:**
- Real-time streaming de todos los eventos
- UI expandible para cada tool call
- Copy-paste de resultados
- Debug mode completo

---

**Impact**: Esta transparencia mejorará dramáticamente la UX y la confianza del usuario en el sistema. ¡No más cajas negras! 