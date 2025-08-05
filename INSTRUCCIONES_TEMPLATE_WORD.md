# Instrucciones para Configurar Template de Word

## 📝 Configuración del Template

### 1. Variables Disponibles
Las variables disponibles para usar en el template son:

#### Para Monto del Préstamo:
#### Opción 1 (Recomendada - Sin duplicación):
```
{{loan_amount_text}}
```

#### Opción 2 (Alternativa - Solo texto):
```
{{loan_amount_text_simple}} ({{loan_currency}} {{loan_amount}})
```

#### Para Pagos:
#### Pago Mensual (Recomendado):
```
{{monthly_payment_text}}
```

#### Pago Final (Recomendado):
```
{{final_payment_text}}
```

#### Pago Mensual (Alternativo):
```
{{monthly_payment_text_simple}} ({{loan_currency}} {{monthly_payment}})
```

#### Pago Final (Alternativo):
```
{{final_payment_text_simple}} ({{loan_currency}} {{final_payment}})
```

### 2. Ejemplos de Uso en Template

#### Monto del Préstamo (Opción 1 - Recomendada):
```
1.1 MONTO DEL PRESTAMO: Por medio del presente contrato LA PRIMERA PARTE otorga a favor de LA SEGUNDA PARTE, quien acepta y recibe conforme, bajo los términos y condiciones expresadas en el presente contrato, un préstamo hipotecario por un monto total de {{loan_amount_text}}, o su equivalente en pesos dominicanos.
```

#### Forma de Pago (Recomendado):
```
2.2 FORMA DE PAGO. Los pagos deberán realizarse en las fechas establecidas en el presente contrato, sin requerimiento previo ni puesta en mora, en el domicilio de LA PRIMERA PARTE, conforme a la siguiente modalidad: ONCE ({{payment_qty_quotes}}) cuotas fijas y consecutivas de {{monthly_payment_text}}, o su equivalente en pesos dominicanos, y una última cuota de {{final_payment_text}}, o su equivalente en pesos dominicanos. El primer pago se efectuará el día VEINTISÉIS (26) del mes de ABRIL de 2025, y el último el día VEINTISÉIS (26) del mes de MARZO de 2026, sin necesidad de intimación alguna.
```

### 3. Configurar Negrita en Word

#### Paso 1: Abrir el Template
1. Abre el archivo `mortgage_template.docx` en Microsoft Word
2. Localiza las secciones donde quieres insertar los montos

#### Paso 2: Insertar las Variables
1. Escribe las variables: `{{loan_amount_text}}`, `{{monthly_payment_text}}`, `{{final_payment_text}}`
2. Selecciona **SOLO** cada variable
3. Aplica formato de **negrita** (Ctrl+B)
4. El texto debe quedar así: **{{loan_amount_text}}**, **{{monthly_payment_text}}**, **{{final_payment_text}}**

#### Paso 3: Verificar el Formato
- Las variables deben estar en negrita
- El resto del texto debe estar en formato normal
- Ejemplo:
  ```
  ...un préstamo hipotecario por un monto total de **{{loan_amount_text}}**, o su equivalente...
  ...cuotas fijas y consecutivas de **{{monthly_payment_text}}**, y una última cuota de **{{final_payment_text}}**...
  ```

### 4. Resultados Esperados

#### Monto del Préstamo:
```
...un préstamo hipotecario por un monto total de **TREINTA MIL DÓLARES ESTADOUNIDENSES (USD 30,000.00)**, o su equivalente...
```

#### Forma de Pago:
```
...ONCE (11) cuotas fijas y consecutivas de **DOS MIL QUINIENTOS DÓLARES ESTADOUNIDENSES (USD 2,500.00)**, o su equivalente en pesos dominicanos, y una última cuota de **CINCO MIL DÓLARES ESTADOUNIDENSES (USD 5,000.00)**, o su equivalente...
```

### 5. Características del Texto Generado
- ✅ **Mayúsculas**: Todo el texto está en mayúsculas
- ✅ **Negrita**: Se mantiene el formato de negrita del template
- ✅ **Formato**: Incluye el símbolo de moneda y el monto numérico
- ✅ **Soporte**: Funciona con USD y DOP
- ✅ **Automático**: Se genera automáticamente desde los datos del loan
- ✅ **Formato inglés**: Coma para miles, punto para decimales (30,000.00)

### 6. Ejemplos de Salida

#### Para USD:
```
TREINTA MIL DÓLARES ESTADOUNIDENSES (USD 30,000.00)
DOS MIL QUINIENTOS DÓLARES ESTADOUNIDENSES (USD 2,500.00)
CINCO MIL DÓLARES ESTADOUNIDENSES (USD 5,000.00)
```

#### Para DOP:
```
CINCO MIL PESOS DOMINICANOS (RD$ 5,000.00)
DOS MIL PESOS DOMINICANOS (RD$ 2,000.00)
MIL PESOS DOMINICANOS (RD$ 1,000.00)
```

### 7. Notas Importantes
- El texto se genera automáticamente en mayúsculas
- El formato de negrita se mantiene del template
- **NO usar {{loan_amount_text}} + {{loan_currency}} + {{loan_amount}} juntos** (causa duplicación)
- **NO usar {{monthly_payment_text}} + {{loan_currency}} + {{monthly_payment}} juntos** (causa duplicación)
- **NO usar {{final_payment_text}} + {{loan_currency}} + {{final_payment}} juntos** (causa duplicación)
- Variables disponibles: 
  - `{{loan_amount_text}}` (recomendado)
  - `{{monthly_payment_text}}` (recomendado)
  - `{{final_payment_text}}` (recomendado)

### 8. Solución de Problemas
Si el texto no aparece en negrita:
1. Verifica que solo la variable esté seleccionada al aplicar negrita
2. Asegúrate de que el formato se aplique correctamente
3. Prueba con un texto simple primero para verificar el formato

Si hay duplicación del formato numérico:
1. Usa solo `{{loan_amount_text}}`, `{{monthly_payment_text}}`, `{{final_payment_text}}` (recomendado)
2. NO combines las variables de texto con las variables individuales de moneda y monto
3. Si necesitas solo texto, usa las versiones `_simple` con las variables individuales 