# Pruebas Unitarias de Contratos

## 📁 Estructura de Carpetas

```
tests/contracts/
├── __init__.py
├── conftest.py                    # Fixtures comunes
├── README.md                      # Esta documentación
├── unit/
│   ├── __init__.py
│   └── test_contract_combinations.py  # 40 pruebas unitarias
├── data/
│   └── __init__.py                # Datos de prueba
├── fixtures/
│   └── __init__.py                # Fixtures específicos
└── validators/
    ├── __init__.py
    └── contract_validator.py      # Validador de reglas de negocio
```

## 🎯 Objetivo

Este conjunto de pruebas valida **40 combinaciones diferentes** de contratos para asegurar que se cumplan las reglas de negocio:

### 📋 Reglas de Negocio

1. **Notario**: **OBLIGATORIO** en todos los contratos
2. **Testigo**: **OBLIGATORIO** solo para personas jurídicas solteras
3. **Referidor**: **OPCIONAL** en todos los casos
4. **Empresas**: Pueden ser cliente o inversionista
5. **Personas**: Pueden ser cliente o inversionista

### 🏢 Tipos de Cliente (5)
- Persona Física Soltera
- Persona Física Casada
- Persona Jurídica Soltera ⚠️ (requiere testigo)
- Persona Jurídica Casada
- Empresa

###  Tipos de Inversionista (2)
- Persona
- Empresa

### 📋 Variaciones (4)
- Testigo + Referidor
- Solo Testigo
- Solo Referidor
- Sin Testigo ni Referidor

## 🧪 Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas de contratos
pytest tests/contracts/ -v

# Ejecutar solo las pruebas unitarias
pytest tests/contracts/unit/ -v

# Ejecutar con reporte detallado
pytest tests/contracts/ --tb=short -v

# Ejecutar pruebas que deben fallar
pytest tests/contracts/unit/test_contract_combinations.py::TestContractCombinations::test_combination_19_juridica_soltera_persona_with_referent_only_should_fail -v
```

## 📊 Resultados Esperados

### ✅ Casos Válidos (32 combinaciones)
- Casos 1-18, 21-22, 25-40: Todas las combinaciones válidas

### ❌ Casos que Deben Fallar (8 combinaciones)
- Casos 19-20, 23-24: Jurídica soltera sin testigo (obligatorio)

## 🔧 Fixtures Disponibles

- `base_contract_data`: Datos base para contratos
- `person_fisica_soltera`: Persona física soltera
- `person_fisica_casada`: Persona física casada
- `person_juridica_soltera`: Persona jurídica soltera
- `person_juridica_casada`: Persona jurídica casada
- `company_data`: Datos de empresa
- `witness_data`: Datos de testigo
- `referent_data`: Datos de referidor
- `notary_data`: Datos de notario

## 🎯 Validaciones

### ContractValidator
- `validate_contract_participants()`: Valida reglas de participantes
- `validate_contract_structure()`: Valida estructura básica
- `validate_loan_data()`: Valida datos del préstamo
- `validate_properties_data()`: Valida datos de propiedades

## 📈 Cobertura

- **40 combinaciones** de contratos
- **100%** de reglas de negocio validadas
- **Casos edge** cubiertos (jurídica soltera sin testigo)
- **Todas las variaciones** de participantes

## 🚀 Extensibilidad

Para agregar nuevas pruebas:

1. Agregar nuevos fixtures en `conftest.py`
2. Crear nuevas pruebas en `test_contract_combinations.py`
3. Agregar validaciones en `contract_validator.py`
4. Documentar en este README

