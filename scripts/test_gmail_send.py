#!/usr/bin/env python3
"""
Test script to send a Gmail email directly using the Gmail tools
"""

import sys
import os
sys.path.append('/Users/a.lumbreras/Code/personal/spartacus')

from agentic_lib.gmail_tools import gmail_send_function, GmailSendInput

async def test_gmail_send():
    print("🧪 Testing Gmail Send functionality...")
    
    # Test email data
    email_args = GmailSendInput(
        to=["a.lumbreras@gmail.com"],  # Your Gmail address
        subject="Prueba Spartacus Desktop",
        body="""Hola!

Este es un correo de prueba enviado desde Spartacus Desktop.

✅ Sistema funcionando correctamente
🚀 Gmail MCP integración activa
🤖 Agentes con Azure OpenAI operativos

Saludos desde Spartacus! 🏛️"""
    )
    
    try:
        print(f"📧 Sending email to: {email_args.to}")
        print(f"📄 Subject: {email_args.subject}")
        print("🔄 Executing Gmail send...")
        
        # Pass None as context since it's not used in our function
        result = await gmail_send_function(None, email_args)
        
        print("✅ Gmail send function completed!")
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print(f"🔍 Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gmail_send()) 