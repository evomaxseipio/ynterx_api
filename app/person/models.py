from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

from app.database import metadata

# Tabla person actualizada según la nueva estructura
person = Table(
    "person",
    metadata,
    Column(
        "person_id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")
    ),
    Column("first_name", String(50), nullable=False),
    Column("last_name", String(50), nullable=False),
    Column("middle_name", String(50), nullable=True),
    Column("date_of_birth", Date, nullable=True),
    Column("gender", String(50), nullable=True),  # Cambiado de gender_id a gender
    Column("nationality_country", String(50), nullable=True),  # Cambiado de nationality_country_id
    Column("marital_status", String(50), nullable=True),  # Cambiado de marital_status_id
    Column("occupation", String(50), nullable=True),  # Nuevo campo agregado
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
    Column(
        "created_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    Column(
        "updated_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
)

# Tablas de referencia mantenidas para compatibilidad con otros endpoints
gender = Table(
    "gender",
    metadata,
    Column("gender_id", Integer, primary_key=True),
    Column("gender_name", String(50), nullable=False),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
)

marital_status = Table(
    "marital_status",
    metadata,
    Column("marital_status_id", Integer, primary_key=True),
    Column("marital_status_name", String(50), nullable=False),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
)

education_level = Table(
    "education_level",
    metadata,
    Column("education_level_id", Integer, primary_key=True),
    Column("education_level_name", String(100), nullable=False),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
)

country = Table(
    "country",
    metadata,
    Column("country_id", Integer, primary_key=True),
    Column("country_name", String(100), nullable=False),
    Column("country_code", String(3), nullable=False),
    Column("phone_code", String(5), nullable=True),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
)

# Nuevas tablas para documentos y direcciones de personas
person_document = Table(
    "person_document",
    metadata,
    Column(
        "document_id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")
    ),
    Column("person_id", UUID, ForeignKey("person.person_id", ondelete="CASCADE"), nullable=False),
    Column("is_primary", Boolean, server_default=expression.false(), nullable=False),
    Column("document_type", String(50), nullable=False),
    Column("document_number", String(50), nullable=False),
    Column("issuing_country_id", Integer, ForeignKey("country.country_id"), nullable=True),
    Column("document_issue_date", Date, nullable=True),
    Column("document_expiry_date", Date, nullable=True),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
    Column(
        "created_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    Column(
        "updated_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
)

# Tabla de ciudades
city = Table(
    "city",
    metadata,
    Column("city_id", Integer, primary_key=True),
    Column("city_name", String(100), nullable=False),
    Column("country_id", Integer, ForeignKey("country.country_id"), nullable=True),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
)

# Tabla address (según el stored procedure del usuario, no person_address)
address = Table(
    "address",
    metadata,
    Column(
        "address_id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")
    ),
    Column("person_id", UUID, ForeignKey("person.person_id", ondelete="CASCADE"), nullable=False),
    Column("address_line1", String(255), nullable=False),
    Column("address_line2", String(255), nullable=True),
    Column("city_id", Integer, ForeignKey("city.city_id"), nullable=True),
    Column("postal_code", String(20), nullable=True),
    Column("address_type", String(50), nullable=True),
    Column("is_principal", Boolean, server_default=expression.false(), nullable=False),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
    Column(
        "created_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    Column(
        "updated_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
)
