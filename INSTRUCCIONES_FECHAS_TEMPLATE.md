# 📅 Instrucciones para Variables de Fechas en Templates

## 🎯 Variables Disponibles

### Fechas de Préstamo y Pagos
- **`{{loan_start_date_text}}`** - Fecha de inicio del préstamo (contract_date) en formato legal completo
- **`{{loan_start_date_simple}}`** - Fecha de inicio del préstamo en formato simple
- **`{{first_payment_date_text}}`** - Fecha del primer pago (contract_date + 1 mes) en formato legal completo
- **`{{first_payment_date_simple}}`** - Fecha del primer pago en formato simple
- **`{{last_payment_date_text}}`** - Fecha del último pago (contract_end_date) en formato legal completo
- **`{{last_payment_date_simple}}`** - Fecha del último pago en formato simple

### Fechas de Contrato (formato DD/MM/YYYY)
- **`{{contract_date}}`** - Fecha de inicio del contrato
- **`{{contract_end_date}}`** - Fecha de fin del contrato

## 📝 Formatos de Salida

### Formato Legal Completo
```
TREINTA Y UNO (31) del mes de JULIO del año DOS MIL VEINTICINCO (2025)
```

### Formato Simple
```
TREINTA Y UNO (31) del mes de JULIO de 2025
```

## 🔧 Cómo Usar en Templates

### 1. Template de Pago (Recomendado)
```word
2.2 FORMA DE PAGO. Los pagos deberán realizarse en las fechas establecidas en el presente contrato, sin requerimiento previo ni puesta en mora, en el domicilio de LA PRIMERA PARTE, conforme a la siguiente modalidad: ONCE ({{payment_qty_quotes}}) cuotas fijas y consecutivas de {{monthly_payment_text}}, o su equivalente en pesos dominicanos, y una última cuota de {{final_payment_text}}, o su equivalente en pesos dominicanos. El préstamo iniciará el día {{loan_start_date_text}}, el primer pago se efectuará el día {{first_payment_date_text}}, y el último el día {{last_payment_date_text}}, sin necesidad de intimación alguna.
```

### 2. Template de Fecha de Contrato
```word
Este contrato se celebra el día {{loan_start_date_text}}, y tendrá vigencia hasta el día {{last_payment_date_text}}.
```

## 🎨 Aplicar Formato en Word

### Para Texto en Negrita:
1. Selecciona la variable en el template (ej: `{{first_payment_date_text}}`)
2. Aplica formato de negrita (Ctrl+B)
3. El texto reemplazado mantendrá el formato

### Para Texto en Mayúsculas:
1. Selecciona la variable
2. Aplica formato de mayúsculas (Ctrl+Shift+A)
3. El texto ya viene en mayúsculas, pero puedes reforzar el formato

## 📊 Ejemplos de Salida

### Con Datos de Entrada:
```json
{
  "contract_date": "31/07/2025",
  "contract_end_date": "31/07/2026"
}
```

### Resultado Procesado:
```
El préstamo iniciará el día TREINTA Y UNO (31) del mes de JULIO del año DOS MIL VEINTICINCO (2025), el primer pago se efectuará el día TREINTA Y UNO (31) del mes de AGOSTO del año DOS MIL VEINTICINCO (2025), y el último el día TREINTA Y UNO (31) del mes de JULIO del año DOS MIL VEINTISÉIS (2026)
```

## ⚠️ Notas Importantes

1. **Formato de Entrada**: Las fechas deben venir en formato `"DD/MM/YYYY"`
2. **Valores por Defecto**: Si no se proporcionan fechas, se usará "FECHA A DETERMINAR"
3. **Mayúsculas**: Todo el texto legal viene en mayúsculas automáticamente
4. **Compatibilidad**: Funciona con las variables de pagos existentes

## 🔄 Variables Relacionadas

Estas variables de fechas funcionan perfectamente con:
- `{{monthly_payment_text}}` - Texto del pago mensual
- `{{final_payment_text}}` - Texto del pago final
- `{{payment_qty_quotes}}` - Cantidad de cuotas
- `{{payment_type}}` - Tipo de pago

## 📊 Lógica de Fechas

- **`{{loan_start_date_text}}`** = `contract_date` (sin modificar)
- **`{{first_payment_date_text}}`** = `contract_date` + 1 mes
- **`{{last_payment_date_text}}`** = `contract_end_date` (sin modificar)

## 🧪 Pruebas

Para probar las variables, ejecuta:
```bash
python3 test_date_variables.py
```

Esto mostrará ejemplos de todas las variables disponibles y su formato de salida. 