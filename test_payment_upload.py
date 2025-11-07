#!/usr/bin/env python3
"""
Script de prueba para verificar que la subida de imágenes de pago funciona correctamente
"""

import asyncio
import json
import requests
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
TEST_CONTRACT_ID = "a95f3a63-5753-44d6-8276-af481a6b4ff2"  # Contrato con Google Drive configurado

async def test_payment_image_upload():
    """Probar la subida de imagen de pago"""
    
    print("🚀 Iniciando prueba de subida de imagen de pago...")
    
    # 1. Verificar que el contrato existe y tiene folder_path
    print(f"\n📋 Paso 1: Verificando contrato {TEST_CONTRACT_ID}...")
    
    try:
        # Crear una imagen de prueba simple
        test_image_path = "test_payment_image.png"
        create_test_image(test_image_path)
        
        # 2. Probar subida de imagen de pago
        print(f"\n📤 Paso 2: Subiendo imagen de pago...")
        
        url = f"{BASE_URL}/loan-payments/upload-payment-image"
        
        with open(test_image_path, 'rb') as f:
            files = {'image_file': ('test_payment.png', f, 'image/png')}
            data = {
                'contract_id': TEST_CONTRACT_ID,
                'reference': 'TEST_PAYMENT_001'
            }
            
            response = requests.post(url, files=files, data=data)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Imagen subida exitosamente!")
                print(f"   - Local path: {result.get('local_path')}")
                print(f"   - Drive success: {result.get('drive_success')}")
                if result.get('drive_view_link'):
                    print(f"   - Drive link: {result.get('drive_view_link')}")
            else:
                print(f"❌ Error en la subida: {result.get('message')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

def create_test_image(filename):
    """Crear una imagen PNG simple para pruebas"""
    from PIL import Image, ImageDraw
    
    # Crear imagen de 100x100 píxeles
    img = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Dibujar texto de prueba
    draw.text((10, 40), "TEST PAYMENT", fill='black')
    
    # Guardar imagen
    img.save(filename, 'PNG')
    print(f"📷 Imagen de prueba creada: {filename}")

if __name__ == "__main__":
    asyncio.run(test_payment_image_upload())
