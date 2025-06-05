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

person = Table(
    "person",
    metadata,
    Column(
        "person_id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")
    ),
    Column("first_name", String(255), nullable=False),
    Column("last_name", String(255), nullable=False),
    Column("middle_name", String(255), nullable=True),
    Column("date_of_birth", Date, nullable=True),
    Column("gender_id", Integer, ForeignKey("gender.gender_id"), nullable=True),
    Column(
        "nationality_country_id",
        Integer,
        ForeignKey("country.country_id"),
        nullable=True,
    ),
    Column(
        "marital_status_id",
        Integer,
        ForeignKey("marital_status.marital_status_id"),
        nullable=True,
    ),
    Column(
        "education_level_id",
        Integer,
        ForeignKey("education_level.education_level_id"),
        nullable=True,
    ),
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
