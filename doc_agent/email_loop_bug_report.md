# 🔍 INFORME: Bug del Bucle Infinito en Email Agent

**Fecha:** 6 de Junio 2025  
**Investigado por:** Assistant AI  
**Severidad:** Alta  
**Estado:** Identificado y Solución Propuesta  

## 📋 Resumen Ejecutivo

Se ha identificado un bug crítico en el Email Agent donde el agente entra en un bucle infinito al enviar emails a sí mismo, alcanzando el límite máximo de 20 iteraciones. Paradójicamente, el agente funciona correctamente cuando envía emails a otros destinatarios.

## 🚨 Síntomas Observados

### ✅ Comportamiento Normal (Email a Terceros)
```
User: "perfecto. Manda un email a Elisa (elisa.vilches@gmail.com)"
→ Agent: Envía email → Llama final_answer → Termina
→ Resultado: 1 iteración, task completa
```

### ❌ Comportamiento Problemático (Email a Uno Mismo)
```
User: "mandame un mensaje a mi mismo con un TODO"
→ Agent: Envía email → NO llama final_answer → Continúa loop
→ Resultado: 20 iteraciones, máximo alcanzado, "I've reached the maximum number of reasoning steps"
```

## 🔬 Análisis de Root Cause

### 1. **Lógica de Finalización del Agent**

El `BaseAgent` depende de que se llame la herramienta `final_answer` para terminar el bucle:

```python
# agentic_lib/base_agent.py:145-155
if tool_name == "final_answer":
    arguments = json.loads(tool_call.function.arguments)
    final_answer_content = arguments.get("answer", "Task completed.")
    
    # ✅ MUST add tool response even for final_answer
    context.message_history.append({...})
    
    executed_tools.append(f"final_answer")
    return executed_tools, True, final_answer_content  # ← AQUÍ SE TERMINA EL LOOP
```

### 2. **System Prompt del Email Agent**

```python
# spartacus_backend/services/agent_manager.py:194-198
"instructions": "You are an email management specialist. You can send emails, search through Gmail, read specific emails, and help organize email communications. Use Gmail tools to manage emails efficiently."
```

**PROBLEMA IDENTIFICADO:** El system prompt no incluye instrucciones explícitas sobre **cuándo** llamar `final_answer`.

### 3. **Respuesta de la Herramienta Gmail**

```python
# agentic_lib/gmail_tools.py:38-42
return (f"Successfully sent email to '{', '.join(args.to)}' "
        f"with subject '{args.subject}'. "
        f"Server confirmation: {response_text}")
```

La herramienta gmail_send responde con confirmación exitosa, pero el LLM no interpreta esto como una señal para finalizar.

### 4. **Diferencia Contextual**

**Hipótesis Principal:** Cuando el usuario pide "envía email a Elisa", es claro que la tarea está completa una vez enviado. Pero cuando dice "mándame un mensaje a mí mismo", el LLM puede interpretar:

- "¿Debo verificar que lo recibió?"
- "¿Debo hacer algo más con el mensaje?"
- "¿'A mí mismo' significa que debo hacer algo adicional?"

## 📊 Evidencia de los Logs

```
{"timestamp": "2025-06-05T21:39:03.655238", "level": "INFO", "message": "Email sent successfully, result: {'content': [{'type': 'text', 'text': 'Email sent successfully with ID: 197420882b6dd392'}]}", "component": "spartacus"}
{"timestamp": "2025-06-05T21:39:03.655623", "level": "INFO", "message": "Base agent iteration 6", "component": "spartacus"}
...
{"timestamp": "2025-06-05T21:40:06.294685", "level": "INFO", "message": "Email sent successfully, result: {'content': [{'type': 'text', 'text': 'Error: Recipient email address is invalid: [YOUR_EMAIL_HERE]'}]}", "component": "spartacus"}
Base agent reached max iterations (20)
```

**Observación:** El agente continuó intentando enviar emails incluso después de éxito.

## 🛠️ Soluciones Propuestas

### Solución 1: **Mejorar System Prompt** (Recomendada)

```python
# Nuevo system prompt para Email Agent
"instructions": """You are an email management specialist. You can send emails, search through Gmail, read specific emails, and help organize email communications. 

IMPORTANT: After successfully completing ANY email operation (send, search, read), you MUST call the final_answer tool to provide the result to the user and complete the task. Do not continue processing unless explicitly asked to perform additional operations.

Examples:
- After sending an email: Call final_answer with "Email sent successfully to [recipient]"
- After searching emails: Call final_answer with the search results
- After reading an email: Call final_answer with the email content"""
```

### Solución 2: **Modificar la Herramienta Gmail**

```python
# Opción: Modificar gmail_send_function para incluir hint de finalización
return (f"Successfully sent email to '{', '.join(args.to)}' "
        f"with subject '{args.subject}'. "
        f"Task completed. Call final_answer to provide this result to the user.")
```

### Solución 3: **Lógica de Auto-Finalización**

```python
# En BaseAgent, agregar lógica para auto-finalizar después de herramientas de acción
if tool_name in ["gmail_send", "gmail_create", "gmail_delete"]:
    # Herramientas de acción que típicamente finalizan la tarea
    suggested_final_answer = f"Task completed: {str(tool_result)}"
    # Agregar sugerencia al contexto para próxima iteración
```

## 🔧 Plan de Implementación

### Fase 1: **Solución Inmediata** (15 minutos)
1. Actualizar system prompt del Email Agent
2. Probar con ambos casos de uso
3. Verificar que no rompe funcionalidad existente

### Fase 2: **Mejoras Adicionales** (30 minutos)
1. Revisar prompts de otros agents especializados
2. Añadir tests para casos de bucle infinito
3. Implementar logging más detallado para debugging

### Fase 3: **Robustez a Largo Plazo** (1 hora)
1. Crear framework de "task completion detection"
2. Añadir métricas de monitoring para loops
3. Implementar circuit breakers para prevenir loops

## 🧪 Test Cases para Validación

```python
# Test Case 1: Email a terceros (debe seguir funcionando)
user_input = "Envía email a test@example.com con asunto 'Test'"
expected_iterations = 1
expected_tools = ["gmail_send", "final_answer"]

# Test Case 2: Email a uno mismo (debe arreglarse)
user_input = "Mándame un email a mí mismo con 'TODO: revisar este bug'"
expected_iterations = 1  # NO 20
expected_tools = ["gmail_send", "final_answer"]

# Test Case 3: Múltiples operaciones (debe requerir múltiples pasos)
user_input = "Envía email a test@example.com y luego búscame emails de ayer"
expected_iterations = 2
expected_tools = ["gmail_send", "gmail_search", "final_answer"]
```

## 📈 Impacto y Prioridad

- **Impacto:** Alto - Degrada UX significativamente
- **Frecuencia:** Media - Solo en casos específicos de self-email
- **Complejidad Fix:** Baja - Cambio de prompt principalmente
- **Riesgo:** Bajo - Cambio no afecta funcionalidad core

## 🎯 Conclusión

El bug está causado por una ambigüedad en las instrucciones del agente sobre cuándo completar la tarea. La solución más efectiva es mejorar el system prompt para ser más explícito sobre la finalización de tareas, especialmente después de operaciones exitosas.

**Recomendación:** Implementar la Solución 1 inmediatamente, seguida de las Fases 2 y 3 para robustez a largo plazo. 