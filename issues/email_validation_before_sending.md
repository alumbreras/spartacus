# 🔒 ISSUE: Validación Explícita para Envío de Emails

**Fecha:** 6 de Junio 2025  
**Prioridad:** Alta 🔴  
**Categoría:** Seguridad / UX  
**Estado:** Abierto  
**Assigned to:** TBD  

## 📋 Descripción del Problema

Actualmente el LLM puede enviar emails sin confirmación explícita del usuario, lo cual presenta riesgos de seguridad y puede llevar a envíos no deseados o accidentales.

### 🚨 Riesgos Identificados
- ✅ **Bug del bucle infinito resuelto**: El LLM ya no envía emails en bucle
- ❌ **Falta validación del usuario**: Cualquier request puede resultar en envío automático
- ❌ **Sin preview del contenido**: Usuario no ve qué se va a enviar antes del envío
- ❌ **Sin confirmación explícita**: No hay step de "¿Confirmas enviar este email?"

## 🎯 Objetivo

Implementar un sistema de validación que **requiera confirmación explícita** del usuario antes de enviar cualquier email.

## 🔍 Investigación Requerida

### **MCP Tool Approval**
- [ ] **Verificar configuración MCP actual**: ¿Está habilitada la aprobación automática de herramientas?
- [ ] **Revisar documentación MCP**: ¿Por defecto MCP requiere aprobación para usar herramientas?
- [ ] **Analizar nuestra implementación**: ¿Estamos usando MCP correctamente o bypassing la validación?

### **Puntos a Investigar**
1. **¿Cómo se configura MCP tool approval?**
2. **¿Nuestra implementación actual respeta las validaciones MCP?**
3. **¿Qué herramientas deberían requerir confirmación?** (gmail_send vs gmail_read)

## 🛠️ Solución Propuesta

### **Fase 1: Investigación MCP**
```bash
# Revisar configuración MCP actual
npx @gongrzhe/server-gmail-autoauth-mcp --help
# Verificar si hay settings de tool approval
```

### **Fase 2: Implementación Frontend**
```typescript
interface EmailValidation {
  to: string;
  subject: string;
  body: string;
  action: 'preview' | 'confirm' | 'cancel';
}
```

### **Fase 3: Flow de Validación**
1. **LLM decide enviar email** → Call `gmail_send_request`
2. **Backend intercepta** → Envía preview al frontend  
3. **Frontend muestra modal** → "¿Confirmar envío de este email?"
4. **Usuario confirma/cancela** → Backend ejecuta acción final
5. **Respuesta al LLM** → "Email enviado" o "Email cancelado por usuario"

## 📋 Tasks

### **Investigación (Priority 1)**
- [ ] Revisar documentación MCP tool approval
- [ ] Analizar configuración actual de MCP en nuestro proyecto
- [ ] Verificar si `gmail_send` bypass las validaciones MCP
- [ ] Documentar findings en este issue

### **Implementación Backend (Priority 2)**
- [ ] Crear endpoint `POST /api/email/preview`
- [ ] Crear endpoint `POST /api/email/confirm/{session_id}`
- [ ] Modificar `gmail_send` tool para requerir confirmación
- [ ] Implementar sistema de sesiones temporales para pendientes

### **Implementación Frontend (Priority 3)**
- [ ] Crear modal de confirmación de email
- [ ] Añadir preview con destinatario, asunto y cuerpo
- [ ] Implementar botones "Enviar" / "Cancelar" / "Editar"
- [ ] Conectar con endpoints de confirmación

### **Testing (Priority 4)**
- [ ] Test: Email NO se envía sin confirmación
- [ ] Test: Email se envía correctamente tras confirmación  
- [ ] Test: Email se cancela correctamente
- [ ] Test: Multiple requests no crean conflictos

## 🔗 Referencias

- **Gmail MCP Documentation**: https://github.com/gongrzhe/server-gmail-autoauth-mcp
- **Nuestro issue del bucle infinito**: `doc_agent/email_loop_bug_report.md`
- **Tool calling implementation**: `agentic_lib/gmail_tools.py`

## 📝 Notas

### **Consideraciones de UX**
- Modal debe ser **non-intrusive** pero **clearly visible**
- Preview debe mostrar **TODO el contenido** del email
- Timeout de confirmación (ej: 5 minutos) para evitar sesiones colgadas

### **Consideraciones Técnicas**  
- Mantener compatibilidad con MCP estándar
- No romper otros tools (gmail_read, gmail_search)
- Session management para múltiples requests concurrentes

---

**Next Steps**: Comenzar con la investigación MCP para entender el baseline actual. 