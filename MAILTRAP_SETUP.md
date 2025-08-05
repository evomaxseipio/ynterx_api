# Configuración de Mailtrap para Notificaciones de Contratos

Este documento explica cómo configurar Mailtrap para las notificaciones de envío de contratos en la API de YnterX.

## 🚀 Configuración Rápida

### 1. Obtener Token de Mailtrap

1. Ve a [Mailtrap.io](https://mailtrap.io) y crea una cuenta gratuita
2. En tu dashboard, ve a **Settings** → **API Tokens**
3. Crea un nuevo token con permisos de envío
4. Copia el token generado

### 2. Configurar Variables de Entorno

Agrega las siguientes variables a tu archivo `.env`:

```bash
# Mailtrap Configuration
MAILTRAP_API_TOKEN=tu_token_aqui
SMTP_FROM_EMAIL=notificaciones@ynterx.com

# Destinatarios de notificaciones de contratos (opcional)
CONTRACT_EMAIL_RECIPIENTS=admin@ynterx.com,manager@ynterx.com
```

### 3. Probar la Configuración

Ejecuta el script de prueba:

```bash
python test_mailtrap.py
```

O usa el endpoint de prueba:

```bash
curl "http://localhost:8000/email/test-mailtrap?to=tu_email@ejemplo.com"
```

## 📧 Funcionalidades Implementadas

### Notificaciones Automáticas

Cuando se genera un contrato y se sube a Google Drive, automáticamente se envía una notificación por email con:

- ✅ Template HTML profesional
- ✅ Nombre personalizado del cliente
- ✅ Enlace directo al contrato en Google Drive
- ✅ Diseño responsive y moderno
- ✅ Categorización de emails para seguimiento

### Endpoints Disponibles

#### 1. Prueba de Email

```
GET /email/test-mailtrap
```

**Parámetros:**

- `to` (requerido): Email de destino
- `client_name` (opcional): Nombre del cliente
- `contract_url` (opcional): URL del contrato

#### 2. Prueba con Template

```
GET /email/test
```

**Parámetros:**

- `to` (requerido): Email de destino
- `client_name` (requerido): Nombre del cliente
- `contract_url` (requerido): URL del contrato

## 🔧 Configuración Avanzada

### Personalizar Template

El template de email se encuentra en:

```
app/utils/templates/contract_email_template.html
```

Variables disponibles:

- `{{client_name}}`: Nombre del cliente
- `{{contract_folder_url}}`: Enlace al contrato

### Configurar Destinatarios

Puedes configurar múltiples destinatarios en el archivo `.env`:

```bash
# Un solo email
CONTRACT_EMAIL_RECIPIENTS=admin@ynterx.com

# Múltiples emails (separados por coma)
CONTRACT_EMAIL_RECIPIENTS=admin@ynterx.com,manager@ynterx.com,legal@ynterx.com
```

### Sandbox de Mailtrap

Para desarrollo y pruebas, Mailtrap proporciona un sandbox donde puedes ver todos los emails enviados:

1. Ve a tu dashboard de Mailtrap
2. En la sección **Inboxes**, encontrarás un inbox por defecto
3. Todos los emails enviados aparecerán ahí para revisión

## 🐛 Solución de Problemas

### Error: "MAILTRAP_API_TOKEN not set"

**Solución:** Verifica que la variable esté configurada en tu archivo `.env`:

```bash
MAILTRAP_API_TOKEN=tu_token_aqui
```

### Error: "401 Unauthorized"

**Solución:** Verifica que el token de Mailtrap sea válido y tenga permisos de envío.

### Error: "Template not found"

**Solución:** Verifica que el archivo de template exista en:

```
app/utils/templates/contract_email_template.html
```

### Emails no se envían automáticamente

**Verifica:**

1. Que `USE_GOOGLE_DRIVE=true` en tu `.env`
2. Que el contrato se suba exitosamente a Google Drive
3. Que `CONTRACT_EMAIL_RECIPIENTS` esté configurado

## 📊 Monitoreo

### Logs de Email

Los logs de envío de emails se pueden encontrar en:

- **Éxito:** `INFO: Enviando correo vía Mailtrap API a: email@ejemplo.com`
- **Error:** `ERROR: Error al enviar correo con Mailtrap API: descripción del error`

### Métricas de Mailtrap

En tu dashboard de Mailtrap puedes ver:

- ✅ Emails enviados exitosamente
- ❌ Emails fallidos
- 📊 Estadísticas de entrega
- 📈 Rendimiento del servicio

## 🔄 Migración desde SendGrid

Si anteriormente usabas SendGrid, la migración es automática. El código ahora usa Mailtrap por defecto, pero mantiene SendGrid como respaldo comentado.

Para volver a SendGrid, edita `app/utils/email_services.py` y comenta la sección de Mailtrap.

## 🆘 Soporte

Si tienes problemas con la configuración:

1. Ejecuta `python test_mailtrap.py` para diagnóstico
2. Revisa los logs de la aplicación
3. Verifica la configuración en tu dashboard de Mailtrap
4. Contacta al equipo de desarrollo

---

**Nota:** Mailtrap es ideal para desarrollo y pruebas. Para producción, considera usar un servicio de email como SendGrid, Mailgun o Amazon SES.
