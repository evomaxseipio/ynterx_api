#!/usr/bin/env python3
"""
Script de prueba para verificar JWT.
"""

import asyncio
from app.auth.jwt_service import jwt_service


async def test_jwt():
    """Probar funcionalidad JWT."""
    print("🧪 Probando JWT Service...")
    
    # Datos de prueba
    user_data = {
        "user_id": "22d27ac6-ae45-486b-a3f4-587a05b3932a",
        "person_id": "33e38bd7-bf56-597c-b4g5-698b16c4043b",
        "username": "test_user",
        "email": "test@ynterxal.com",
        "role": {
            "role_name": "admin",
            "permissions": ["read:contracts", "write:contracts", "delete:contracts"]
        }
    }
    
    try:
        # 1. Crear access token
        print("1. Creando access token...")
        access_token = jwt_service.create_access_token(user_data)
        print(f"✅ Access token creado: {access_token[:50]}...")
        
        # 2. Crear refresh token
        print("2. Creando refresh token...")
        refresh_token = jwt_service.create_refresh_token(user_data["user_id"])
        print(f"✅ Refresh token creado: {refresh_token[:50]}...")
        
        # 3. Verificar access token
        print("3. Verificando access token...")
        payload = jwt_service.verify_token(access_token)
        print(f"✅ Token verificado - User ID: {payload['sub']}")
        print(f"✅ Permisos: {payload.get('permissions', [])}")
        
        # 4. Verificar refresh token
        print("4. Verificando refresh token...")
        refresh_payload = jwt_service.verify_token(refresh_token)
        print(f"✅ Refresh token verificado - User ID: {refresh_payload['sub']}")
        print(f"✅ Tipo: {refresh_payload.get('type')}")
        
        # 5. Verificar expiración
        print("5. Verificando expiración...")
        is_expired = jwt_service.is_token_expired(access_token)
        print(f"✅ Token expirado: {is_expired}")
        
        # 6. Obtener user_id
        print("6. Obteniendo user_id...")
        user_id = jwt_service.get_user_id_from_token(access_token)
        print(f"✅ User ID obtenido: {user_id}")
        
        print("\n🎉 ¡Todas las pruebas JWT pasaron exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en prueba JWT: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_jwt()) 