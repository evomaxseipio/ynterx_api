# Guía de Implementación - API Ynterx en Producción

## 📋 Información General

**Proyecto:** API Ynterx  
**Objetivo:** Migrar API desde PM2 a servicio systemd en producción  
**Ubicación:** `/var/www/ynterx-api`  
**Usuario:** `ynterxapiuser`  
**Puerto:** 8001  

## 🎯 Problemas Identificados

1. **Conflicto de módulo email:** `app/email.py` causa conflicto con módulo estándar de Python
2. **Problema de conectividad IPv6:** Servidor no puede conectarse a Google APIs via IPv6
3. **PM2 con watch habilitado:** Causa reinicios innecesarios en producción

## 🚀 Plan de Implementación

### Fase 1: Preparación del Sistema

#### 1.1 Crear usuario dedicado
```bash
# Crear usuario del sistema
sudo useradd -m -s /bin/bash ynterxapiuser

# Verificar creación
id ynterxapiuser
```

#### 1.2 Crear estructura de directorios
```bash
# Crear directorio principal
sudo mkdir -p /var/www/ynterx-api

# Crear directorios necesarios
sudo mkdir -p /var/www/ynterx-api/app/generated_contracts
sudo mkdir -p /var/www/ynterx-api/logs
sudo mkdir -p /var/log/ynterx-api
```

### Fase 2: Migración del Código

#### 2.1 Copiar aplicación
```bash
# Copiar desde ubicación actual
sudo cp -r /root/project/ynterx-api/* /var/www/ynterx-api/

# Cambiar propietario
sudo chown -R ynterxapiuser:ynterxapiuser /var/www/ynterx-api

# Cambiar permisos
sudo chmod -R 755 /var/www/ynterx-api
```

#### 2.2 Solucionar conflicto de módulo email
```bash
# Renombrar archivo problemático
sudo mv /var/www/ynterx-api/app/email.py /var/www/ynterx-api/app/email_service.py

# Verificar cambio
ls -la /var/www/ynterx-api/app/email_service.py
```

#### 2.3 Configurar permisos de archivos sensibles
```bash
# Configurar permisos del archivo .env
sudo chmod 600 /var/www/ynterx-api/.env

# Verificar permisos
ls -la /var/www/ynterx-api/.env
```

### Fase 3: Configuración del Entorno

#### 3.1 Configurar entorno virtual
```bash
# Cambiar al usuario ynterxapiuser
sudo su - ynterxapiuser

# Ir al directorio de la aplicación
cd /var/www/ynterx-api

# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Salir del usuario
exit
```

#### 3.2 Configurar DNS para IPv4
```bash
# Editar configuración de DNS
sudo nano /etc/systemd/resolved.conf
```

**Agregar al archivo:**
```ini
[Resolve]
DNS=8.8.8.8 8.8.4.4
DNSSEC=no
IPv6DNS=no
```

**Reiniciar servicio DNS:**
```bash
sudo systemctl restart systemd-resolved
```

### Fase 4: Configuración del Servicio Systemd

#### 4.1 Crear archivo de servicio
```bash
# Crear archivo del servicio
sudo nano /etc/systemd/system/ynterx-api.service
```

**Contenido completo del archivo:**
```ini
[Unit]
Description=Ynterx API Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ynterxapiuser
Group=ynterxapiuser
WorkingDirectory=/var/www/ynterx-api
Environment=PATH=/var/www/ynterx-api/.venv/bin
Environment=PYTHONPATH=/var/www/ynterx-api
Environment=GOOGLE_APIS_IPV4_ONLY=true
EnvironmentFile=/var/www/ynterx-api/.env
ExecStart=/var/www/ynterx-api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ynterx-api

[Install]
WantedBy=multi-user.target
```

#### 4.2 Activar y configurar el servicio
```bash
# Recargar configuración de systemd
sudo systemctl daemon-reload

# Habilitar servicio para inicio automático
sudo systemctl enable ynterx-api

# Iniciar el servicio
sudo systemctl start ynterx-api

# Verificar estado
sudo systemctl status ynterx-api
```

### Fase 5: Verificación y Testing

#### 5.1 Verificar funcionamiento del servicio
```bash
# Ver estado del servicio
sudo systemctl status ynterx-api

# Ver logs en tiempo real
sudo journalctl -u ynterx-api -f

# Ver logs de las últimas 50 líneas
sudo journalctl -u ynterx-api -n 50
```

#### 5.2 Verificar conectividad
```bash
# Verificar que el puerto esté abierto
sudo netstat -tlnp | grep 8001

# Probar conectividad local
curl http://localhost:8001/health

# Probar endpoint de contratos
curl http://localhost:8001/contracts/
```

#### 5.3 Verificar Google Drive
```bash
# Verificar variables de entorno
sudo cat /var/www/ynterx-api/.env | grep GOOGLE

# Verificar archivo de credenciales
ls -la /var/www/ynterx-api/credentials.json
```

### Fase 6: Comandos de Gestión

#### 6.1 Comandos básicos del servicio
```bash
# Iniciar servicio
sudo systemctl start ynterx-api

# Detener servicio
sudo systemctl stop ynterx-api

# Reiniciar servicio
sudo systemctl restart ynterx-api

# Ver estado
sudo systemctl status ynterx-api
```

#### 6.2 Comandos de logs
```bash
# Ver logs en tiempo real
sudo journalctl -u ynterx-api -f

# Ver logs de hoy
sudo journalctl -u ynterx-api --since today

# Ver logs de las últimas 2 horas
sudo journalctl -u ynterx-api --since "2 hours ago"

# Ver logs con timestamps
sudo journalctl -u ynterx-api -n 100 --no-pager
```

#### 6.3 Comandos de monitoreo
```bash
# Ver uso de recursos
sudo systemctl show ynterx-api --property=MemoryCurrent,CPUUsageNSec

# Ver procesos del servicio
ps aux | grep ynterx-api

# Ver conexiones de red
sudo netstat -tlnp | grep 8001
```

## 🔧 Configuración de Variables de Entorno

### Archivo .env requerido
```bash
# Configuración de producción
NODE_ENV=production
PORT=8001
USE_GOOGLE_DRIVE=true

# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/ynterx_db

# JWT
JWT_SECRET_KEY=your-super-secret-production-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Google Drive
GOOGLE_CREDENTIALS_PATH=/var/www/ynterx-api/credentials.json
GOOGLE_DRIVE_FOLDER_ID=your-folder-id

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📁 Estructura de Directorios Final

```
/var/www/ynterx-api/
├── app/
│   ├── generated_contracts/     # Contratos generados
│   ├── email_service.py         # Renombrado desde email.py
│   └── ...
├── logs/                        # Logs de la aplicación
├── .venv/                       # Entorno virtual
├── .env                         # Variables de entorno
├── credentials.json             # Credenciales de Google Drive
└── requirements.txt             # Dependencias
```

## ✅ Checklist de Verificación

### Pre-implementación
- [ ] Usuario `ynterxapiuser` creado
- [ ] Directorio `/var/www/ynterx-api` creado
- [ ] Aplicación copiada correctamente
- [ ] Archivo `email.py` renombrado a `email_service.py`
- [ ] Permisos configurados correctamente

### Post-implementación
- [ ] Servicio systemd creado y configurado
- [ ] Servicio habilitado para inicio automático
- [ ] Servicio iniciado y funcionando
- [ ] Puerto 8001 abierto y escuchando
- [ ] API responde correctamente
- [ ] Google Drive funcionando
- [ ] Logs sin errores críticos

## 🚨 Troubleshooting

### Problema: Servicio no inicia
```bash
# Ver logs detallados
sudo journalctl -u ynterx-api -n 100

# Verificar permisos
sudo chown -R ynterxapiuser:ynterxapiuser /var/www/ynterx-api
```

### Problema: Error de módulo email
```bash
# Verificar que el archivo fue renombrado
ls -la /var/www/ynterx-api/app/email_service.py

# Si no existe, renombrar manualmente
sudo mv /var/www/ynterx-api/app/email.py /var/www/ynterx-api/app/email_service.py
```

### Problema: Error de Google Drive
```bash
# Verificar conectividad
ping googleapis.com

# Verificar credenciales
ls -la /var/www/ynterx-api/credentials.json

# Verificar variables de entorno
sudo cat /var/www/ynterx-api/.env | grep GOOGLE
```

### Problema: Puerto no disponible
```bash
# Verificar que el puerto esté libre
sudo netstat -tlnp | grep 8001

# Si está ocupado, cambiar puerto en .env
sudo nano /var/www/ynterx-api/.env
```

## 📞 Contacto de Soporte

**Desarrollador:** Equipo de Desarrollo Ynterx  
**Fecha:** Octubre 2025  
**Versión:** 1.0  

---

**Nota:** Este documento debe ser seguido paso a paso para garantizar una implementación exitosa de la API en producción.
