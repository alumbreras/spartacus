# 🔧 Configuración de Azure OpenAI en Spartacus

## Estado Actual

✅ **¡El sistema ya está configurado para usar Azure OpenAI!**

Spartacus Desktop está preparado para funcionar con Azure OpenAI desde el primer momento:

- ✅ `AzureOpenAIClient` implementado en `agentic_lib/llm_clients/azure_openai_client.py`
- ✅ `BaseAgent` configurado para usar Azure OpenAI por defecto
- ✅ `SpartacusAgentManager` inicializa Azure OpenAI automáticamente
- ✅ Todas las APIs están preparadas para el cliente de Azure

## ¿Qué Necesitas Hacer?

Solo necesitas configurar tus credenciales de Azure OpenAI:

### Opción 1: Script Automático (Recomendado)

```bash
# Ejecuta el script de configuración interactivo
python scripts/setup_azure_openai.py
```

El script te guiará paso a paso para:
- ✅ Crear el archivo `.env` con tus credenciales
- ✅ Validar la configuración
- ✅ Probar la conexión con Azure OpenAI

### Opción 2: Manual

Crea un archivo `.env` en la raíz del proyecto:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=tu_api_key_aqui
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-4
AZURE_OPENAI_API_VERSION=2024-10-21

# Backend Settings
SPARTACUS_HOST=127.0.0.1
SPARTACUS_PORT=8000
SPARTACUS_LOG_LEVEL=INFO

# Development
SPARTACUS_RELOAD=true
```

## Cómo Obtener las Credenciales

1. **Azure Portal**: Ve a https://portal.azure.com
2. **OpenAI Service**: Busca tu servicio de Azure OpenAI
3. **Keys and Endpoint**: Ve a la sección "Keys and Endpoint"
4. **Copia**:
   - **API Key**: Una de las claves disponibles
   - **Endpoint**: El endpoint de tu servicio
   - **Deployment Name**: El nombre de tu modelo desplegado

## Modelos Compatibles

Azure OpenAI en Spartacus soporta:

- ✅ **GPT-4** (recomendado)
- ✅ **GPT-4 Turbo**  
- ✅ **GPT-3.5 Turbo**
- ✅ **GPT-4o**
- ✅ **GPT-4o Mini**

## Versiones de API Soportadas

- ✅ **2024-10-21** (recomendada - tool calling completo)
- ✅ **2024-08-01-preview** (structured outputs)
- ✅ **2024-06-01** (tool_choice='required')

## Verificar la Configuración

Después de configurar las credenciales:

```bash
# Prueba la conexión
python test_standalone.py

# O inicia Spartacus completo
python start_spartacus.py
```

## Arquitectura Técnica

### Cliente Azure OpenAI

```python
from agentic_lib.llm_clients.azure_openai_client import AzureOpenAIClient

# Inicialización automática desde variables de entorno
client = AzureOpenAIClient()

# Llamada a Azure OpenAI con tool calling
response = await client.invoke(
    messages=messages,
    tools=tools,
    tool_choice="required"
)
```

### Integración en Agents

```python
# El BaseAgent usa Azure OpenAI por defecto
class BaseAgent:
    def __init__(self, llm_client: AzureOpenAIClient, tools, system_prompt):
        self.llm_client = llm_client  # Azure OpenAI client
        # ...
```

### Configuración en Agent Manager

```python
# Agent Manager inicializa Azure OpenAI automáticamente
class SpartacusAgentManager:
    async def initialize(self):
        self.llm_client = AzureOpenAIClient()  # Auto-configuración
        # ...
```

## Solución de Problemas

### Error: ModuleNotFoundError: No module named 'spartacus_backend'

✅ **Solucionado**: Usa el launcher principal:
```bash
python start_spartacus.py
```

### Error: Address already in use (Port 8000)

```bash
# Mata procesos en puerto 8000
lsof -ti:8000 | xargs kill -9

# O usa un puerto diferente
SPARTACUS_PORT=8001 python start_spartacus.py
```

### Error: Azure OpenAI Authentication

1. ✅ Verifica el API Key
2. ✅ Confirma el endpoint (debe incluir https://)
3. ✅ Verifica el deployment name
4. ✅ Comprueba la versión de API

### Error: Tool calling no funciona

- ✅ Usa API version 2024-06-01 o superior
- ✅ Verifica que tu modelo soporte tool calling
- ✅ Confirma que el deployment está activo

## Logs del Sistema

Cuando funcione correctamente verás:

```log
{"level": "INFO", "message": "✅ LLM client initialized", "component": "spartacus"}
{"level": "INFO", "message": "✅ Agent Manager initialized with 5 agents and 4 tools"}
```

## Siguientes Pasos

Una vez configurado Azure OpenAI:

1. ✅ Ejecuta `python start_spartacus.py`
2. ✅ Ve a http://127.0.0.1:8000/docs para la API
3. ✅ Prueba el chat en la interfaz Electron
4. ✅ Los agentes ahora usarán Azure OpenAI real (no mock)

## Beneficios de Azure OpenAI

- 🛡️ **Seguridad**: Cumplimiento empresarial
- 🌍 **Privacidad**: Datos en tu región
- ⚡ **Rendimiento**: Baja latencia
- 🔧 **Control**: Gestión de cuotas y límites
- 📊 **Monitoreo**: Métricas detalladas en Azure

---

**¡Azure OpenAI está listo para potenciar tus agentes de Spartacus!** 🏛️ 