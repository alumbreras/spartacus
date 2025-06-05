#!/usr/bin/env python3
"""
Verify Gmail authentication completion
"""
import json
from pathlib import Path

def verify_gmail_auth():
    """Check if Gmail OAuth token exists and is valid"""
    print("🔍 VERIFICANDO AUTENTICACIÓN GMAIL")
    print("=" * 40)
    
    token_file = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"
    
    if not token_file.exists():
        print("❌ No existe archivo de token")
        return False
    
    try:
        with open(token_file) as f:
            token_data = json.load(f)
        
        print(f"📄 Token file: {token_file}")
        print(f"🔑 Keys found: {list(token_data.keys())}")
        
        if "access_token" in token_data:
            print("✅ access_token: PRESENTE")
            print("✅ Gmail authentication: COMPLETA")
            return True
        else:
            print("❌ access_token: FALTANTE")
            print("⚠️  Solo credenciales cliente encontradas")
            return False
            
    except Exception as e:
        print(f"❌ Error reading token: {e}")
        return False

if __name__ == "__main__":
    success = verify_gmail_auth()
    
    if success:
        print("\n🎉 ¡Gmail está autenticado!")
        print("   Ahora puedes usar comandos de email reales")
    else:
        print("\n⏳ Completa la autenticación OAuth primero")
        print("   Después ejecuta este script de nuevo") 