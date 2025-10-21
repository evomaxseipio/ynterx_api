# Endpoints de Imágenes de Pagos

## Descripción

Los endpoints existentes de pagos han sido actualizados para manejar automáticamente la subida de imágenes de vouchers de banco. Las imágenes se almacenan tanto localmente como en Google Drive (si está disponible).

## Endpoints Actualizados

### 1. Subir Imagen de Pago (Opcional)

**POST** `/loan-payments/upload-payment-image`

Sube una imagen de voucher de banco a la carpeta `payments` del contrato.

**Parámetros:**
- `contract_id` (string): ID del contrato
- `reference` (string): Referencia del pago (usado como nombre del archivo)
- `image_file` (file): Archivo de imagen (JPEG, PNG, GIF, máximo 10MB)

**Respuesta:**
```json
{
  "success": true,
  "message": "Imagen subida exitosamente",
  "filename": "REF123.jpg",
  "local_path": "/path/to/contract/payments/REF123.jpg",
  "drive_success": true,
  "drive_view_link": "https://drive.google.com/file/d/...",
  "drive_error": null
}
```

### 2. Endpoints de Pagos con Soporte de Imágenes

Todos los endpoints de pagos existentes ahora soportan imágenes automáticamente:

#### **POST** `/loan-payments/register-transaction`
#### **POST** `/loan-payments/auto-payment`
#### **POST** `/loan-payments/specific-payment`

**Parámetros adicionales:**
- `image_file` (file, opcional): Imagen del voucher de banco

**Comportamiento:**
- Si se proporciona `image_file`, se sube automáticamente a la carpeta `payments`
- La URL de la imagen se asigna automáticamente a `url_bank_receipt`
- El nombre del archivo se basa en la `reference` del pago

## Estructura de Carpetas

```
contracts/
├── {contract_id}/
│   ├── {contract_id}.docx
│   ├── metadata.json
│   ├── attachments/
│   └── payments/          # Nueva carpeta para imágenes de pagos
│       ├── REF123.jpg
│       ├── REF456.png
│       └── ...
```

## Características

- **Validación de archivos**: Solo acepta imágenes (JPEG, PNG, GIF)
- **Límite de tamaño**: Máximo 10MB por archivo
- **Almacenamiento dual**: Local + Google Drive
- **Nombres únicos**: Usa la referencia del pago como nombre del archivo
- **Creación automática**: Crea la carpeta `payments` si no existe
- **Compatibilidad**: Funciona con Google Drive y almacenamiento local

## Uso

### Ejemplo con curl:

```bash
# Subir solo imagen (opcional)
curl -X POST "http://localhost:8000/loan-payments/upload-payment-image" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "contract_id=CONTRACT123" \
  -F "reference=PAYMENT456" \
  -F "image_file=@voucher.jpg"

# Registrar pago con imagen usando endpoint existente
curl -X POST "http://localhost:8000/loan-payments/auto-payment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "contract_loan_id=123" \
  -F "amount=1000.00" \
  -F "payment_method=Bank Transfer" \
  -F "reference=PAYMENT456" \
  -F "notes=Pago mensual" \
  -F "image_file=@voucher.jpg"

# O usar el endpoint de transacción específica
curl -X POST "http://localhost:8000/loan-payments/register-transaction" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "contract_loan_id=123" \
  -F "amount=1000.00" \
  -F "reference=PAYMENT456" \
  -F "image_file=@voucher.jpg"
```

### Ejemplo con JavaScript:

```javascript
// Subir imagen (opcional)
const formData = new FormData();
formData.append('contract_id', 'CONTRACT123');
formData.append('reference', 'PAYMENT456');
formData.append('image_file', fileInput.files[0]);

const response = await fetch('/loan-payments/upload-payment-image', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});

// Registrar pago con imagen usando endpoint existente
const paymentFormData = new FormData();
paymentFormData.append('contract_loan_id', '123');
paymentFormData.append('amount', '1000.00');
paymentFormData.append('reference', 'PAYMENT456');
paymentFormData.append('image_file', fileInput.files[0]);

const paymentResponse = await fetch('/loan-payments/auto-payment', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: paymentFormData
});
```
