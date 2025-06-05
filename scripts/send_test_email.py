#!/usr/bin/env python3
"""
Script para enviar un email de prueba directamente a alberto.lumbreras@gmail.com
"""

import sys
import os
import asyncio

sys.path.append('/Users/a.lumbreras/Code/personal/spartacus')

from agentic_lib.gmail_tools import gmail_send_function, GmailSendInput

async def send_test_email():
    print("📧 Sending test email to alberto.lumbreras@gmail.com...")
    
    # Email data
    email_args = GmailSendInput(
        to=["alberto.lumbreras@gmail.com"],
        subject="Spartacus Desktop Test ✅",
        body="""¡Hola Alberto!

Este es un correo de prueba enviado desde Spartacus Desktop.

🎉 ¡El sistema está funcionando correctamente!

✅ Backend con Azure OpenAI
✅ Agentes inteligentes
✅ Integración Gmail MCP
✅ Autenticación OAuth completada

¡Saludos desde Spartacus! 🏛️

---
Enviado desde Spartacus Desktop - Una alternativa a Claude Desktop
"""
    )
    
    try:
        print(f"📤 Enviando email a: {email_args.to}")
        print(f"📋 Asunto: {email_args.subject}")
        
        # Pass None as context since the function accepts ctx parameter
        result = await gmail_send_function(None, email_args)
        
        print(f"✅ Resultado: {result}")
        
        if "sent successfully" in str(result).lower():
            print("🎉 ¡Email enviado exitosamente!")
        else:
            print("⚠️  El email puede haber usado datos mock")
            
        return result
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(send_test_email()) 