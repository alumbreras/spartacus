# 🔄 ISSUE: Actualización y Compatibilidad de OpenAI

**Fecha:** 6 de Junio 2025  
**Prioridad:** Media 🟡  
**Categoría:** Dependencias / Infraestructura  
**Estado:** Abierto  
**Assigned to:** TBD  

## 📋 Situación Actual

### **Versiones en Uso**
- **Librería**: `openai==1.54.5` (instalada pero no especificada en requirements.txt)
- **Cliente**: `AsyncAzureOpenAI`
- **API Version**: Intentando usar "2024-08-01-preview" para structured output

### **Dependencias Actuales**
```python
# Dependencias de openai 1.54.5
anyio
distro
httpx
jiter
pydantic
sniffio
tqdm
typing-extensions
```

### **Problemas Identificados**
1. ❌ **Versión no especificada** en requirements.txt
2. ❌ **Errores de compatibilidad** con structured output:
   ```
   BadRequestError: Error code: 400 - {'error': {'message': "Invalid parameter: 'response_format' of type 'json_schema' is not supported with this model..."
   ```
3. ❌ **Múltiples intentos fallidos** con diferentes versiones de API:
   - 2024-08-06: resource not available
   - 2024-07-01-preview: BadRequest
   - 2024-08-01-preview: BadRequest
   - 2024-09-01-preview: BadRequest
   - 2024-10-01-preview: BadRequest
   - 2024-11-01-preview: BadRequest

## 🎯 Objetivos

1. **Fijar versión de librería** en requirements.txt a `openai==1.54.5`
2. **Resolver compatibilidad** con structured output
3. **Documentar** versiones soportadas y limitaciones

## 🛠️ Plan de Acción

### **1. Investigación (Priority 1)**
- [x] Verificar última versión estable de `openai` Python SDK (✅ 1.54.5)
- [ ] Consultar documentación de Azure OpenAI sobre structured output
- [ ] Probar diferentes modelos para structured output
- [ ] Documentar versiones de API soportadas por cada modelo

### **2. Actualización de Dependencias (Priority 2)**
- [ ] Actualizar requirements.txt con `openai==1.54.5`
- [ ] Verificar compatibilidad de dependencias:
  - [ ] anyio
  - [ ] distro
  - [ ] httpx
  - [ ] jiter
  - [ ] pydantic
  - [ ] sniffio
  - [ ] tqdm
  - [ ] typing-extensions
- [ ] Crear script de migración si necesario

### **3. Mejoras de Código (Priority 3)**
- [ ] Implementar fallback para modelos sin structured output
- [ ] Añadir logging detallado de versiones
- [ ] Crear tests de compatibilidad

## 📝 Notas Técnicas

### **Versiones de API Relevantes**
```python
# API version "2024-06-01" # tool_choice='required' available
# API version "2024-08-01-preview" # structured output available
```

### **Propiedades Útiles de Respuesta**
```python
# completion.choices[0].message.content
# completion.choices[0].message.tool_calls
# completion.choices[0].message.tool_calls[0].function.arguments
# completion.choices[0].message.tool_calls[0].function.name
```

## 🔗 Referencias

- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Azure OpenAI API Versions](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)
- [Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)

## ⚠️ Consideraciones

1. **Backward Compatibility**: Asegurar que cambios no rompan funcionalidad existente
2. **Modelo Actual**: Verificar qué modelo estamos usando y sus limitaciones
3. **Costos**: Evaluar impacto en costos de API con diferentes versiones

---

**Impact**: Esta actualización es crucial para mantener el sistema actualizado y aprovechar nuevas características como structured output. 