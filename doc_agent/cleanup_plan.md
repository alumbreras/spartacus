# Plan de Limpieza de Agent Manager

## Objetivo
Limpiar mocks innecesarios del `agent_manager.py` manteniendo la funcionalidad real de Gmail que necesitas para desarrollo.

## Problemas Actuales Identificados
1. **Backend muere constantemente** - necesitamos investigar por qué
2. **Mocks innecesarios** - hay código mock que confunde y no aporta valor
3. **Funcionalidad real de Gmail debe mantenerse** - NO queremos mails falsos

## Análisis del Código Actual

### Código que MANTENER (es necesario):
- ✅ `GmailMCPClient` - conectividad real con Gmail
- ✅ `BaseAgent` con `AzureOpenAIClient` - LLM real
- ✅ Gmail tools (`gmail_send_tool`, `gmail_search_tool`, `gmail_read_tool`) - funcionalidad real
- ✅ Sistema de context con `gmail_client` para herramientas
- ✅ Manejo de errores sin fallback a mocks

### Código que ELIMINAR (mocks innecesarios):
- ❌ `MockAgent` class - no queremos respuestas falsas
- ❌ `MockTool` class - no queremos herramientas falsas  
- ❌ Fallbacks a mocks cuando falla LLM - mejor error claro
- ❌ Respuestas mock de email - preferimos error real

### Código que SIMPLIFICAR:
- 🔧 `AgentInstance` class - parece sobre-engineered, simplificar
- 🔧 Múltiples configuraciones de agentes - mantener solo default y email
- 🔧 Logging excesivo - mantener solo lo esencial

## Plan de Acción

### Paso 1: Investigar por qué muere el backend
- Revisar logs de error específicos
- Verificar dependencias e imports

### Paso 2: Limpiar mocks innecesarios
- Eliminar `MockAgent` y `MockTool` classes
- Quitar fallbacks a mocks
- Mantener solo agentes reales con LLM y Gmail

### Paso 3: Simplificar estructura
- Simplificar `AgentInstance` o eliminarlo si no es necesario
- Mantener estructura básica de agentes: default y email
- Limpiar código duplicado

### Paso 4: Preservar funcionalidad real
- Asegurar que Gmail tools funcionan con cliente real
- Mantener manejo de errores sin mocks
- Verificar que LLM client funciona correctamente

## Resultado Esperado
Un `agent_manager.py` limpio que:
- Solo use funcionalidad REAL (LLM + Gmail)
- Falle claramente cuando algo no funciona (sin mocks confusos)
- Mantenga la conectividad Gmail real para desarrollo
- Sea más fácil de debuggear y mantener

## ¿Proceder con este plan?
- [ ] Revisar backend crash primero
- [ ] Limpiar mocks según plan
- [ ] Verificar funcionalidad Gmail se mantiene 