#!/usr/bin/env python3
"""
Script para leer Gmail directamente usando la API de Google
Sin pasar por el MCP server que está dando problemas
"""

import os
import json
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

async def read_real_gmail():
    """Lee directamente Gmail usando la API de Google"""
    print("📧 Leyendo Gmail DIRECTAMENTE con Google API...")
    
    # Ruta del archivo de tokens
    token_file = os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")
    
    if not os.path.exists(token_file):
        print("❌ No se encontró el archivo de tokens OAuth")
        return
    
    try:
        # Cargar tokens
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        print("✅ Tokens OAuth encontrados")
        
        # Extraer credenciales correctas
        oauth_keys = token_data.get('installed', {})
        
        # Crear credenciales usando los tokens del archivo
        creds = Credentials(
            token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=oauth_keys.get('client_id'),
            client_secret=oauth_keys.get('client_secret')
        )
        
        # Refrescar token si es necesario
        if creds.expired and creds.refresh_token:
            print("🔄 Refrescando token...")
            creds.refresh(Request())
            
            # Guardar tokens actualizados
            token_data['access_token'] = creds.token
            if hasattr(creds, 'expiry') and creds.expiry:
                token_data['expires_in'] = int((creds.expiry - creds.expiry.utcnow()).total_seconds())
            
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            print("✅ Token actualizado y guardado")
        
        # Crear cliente Gmail
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Cliente Gmail creado exitosamente")
        
        # Listar mensajes recientes
        print("\n📬 Buscando mensajes recientes en tu Gmail...")
        results = service.users().messages().list(
            userId='me',
            maxResults=5,
            q='in:inbox'
        ).execute()
        
        messages = results.get('messages', [])
        print(f"📋 Encontrados {len(messages)} mensajes en la bandeja de entrada")
        
        if not messages:
            print("📭 No hay mensajes en tu bandeja de entrada")
            return
        
        # Leer los primeros 3 mensajes
        for i, message in enumerate(messages[:3]):
            print(f"\n📧 === MENSAJE {i+1} ===")
            
            # Obtener detalles del mensaje
            msg_detail = service.users().messages().get(
                userId='me',
                id=message['id']
            ).execute()
            
            # Extraer headers importantes
            headers = msg_detail['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
            from_sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Fecha desconocida')
            
            print(f"📋 ID: {message['id']}")
            print(f"📋 De: {from_sender}")
            print(f"📋 Asunto: {subject}")
            print(f"📋 Fecha: {date}")
            
            # Extraer contenido del mensaje
            payload = msg_detail['payload']
            body = ""
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        import base64
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            elif payload['body'].get('data'):
                import base64
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
            if body:
                print(f"📄 Contenido: {body[:200]}...")
            else:
                print("📄 Sin contenido de texto plano")
            
            print("-" * 50)
        
        print("\n🎉 ¡Lectura de Gmail completada exitosamente!")
        print("✅ Confirmado: Spartacus puede acceder a tu Gmail real")
        
    except Exception as e:
        print(f"❌ Error leyendo Gmail: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(read_real_gmail()) 