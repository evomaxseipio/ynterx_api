from sqlalchemy import (
    TIMESTAMP,
    Table, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Date, Numeric,
    BigInteger, text, CheckConstraint, UniqueConstraint,
    UUID as SA_UUID
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.database import metadata
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from sqlalchemy.sql import expression


# Company table
company = Table(
    "company",
    metadata,
    Column("company_id", Integer, primary_key=True, autoincrement=True),
    Column("company_name", String(200), nullable=False),
    Column("company_rnc", String(20), nullable=True),
    Column("mercantil_registry", String(20), nullable=True),
    Column("nationality", String(100), nullable=True),
    Column("email", String(100), nullable=True),
    Column("phone", String(20), nullable=True),
    Column("website", String(100), nullable=True),
    Column("company_type", String(30), nullable=True),
    Column("company_description", Text, nullable=True),
    Column("frontImagePath", Text, nullable=True),
    Column("backImagePath", Text, nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
)


# Company Address table
company_address = Table(
    "company_address",
    metadata,
    Column("company_address_id", Integer, primary_key=True, autoincrement=True),
    Column("company_id", Integer, ForeignKey("company.company_id"), nullable=False),
    Column("address_line1", String(100), nullable=False),
    Column("address_line2", String(100), nullable=True),
    Column("city", String(100), nullable=True),
    Column("postal_code", String(20), nullable=True),
    Column("address_type", String(20), nullable=False, server_default=text("'Business'")),
    Column("email", String(100), nullable=True),
    Column("phone", String(20), nullable=True),
    Column("is_principal", Boolean, server_default=text("false"), nullable=False),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
)


# Company Manager table
company_manager = Table(
    "company_manager",
    metadata,
    Column("manager_id", Integer, primary_key=True, autoincrement=True),
    Column("company_id", Integer, ForeignKey("company.company_id", ondelete="CASCADE"), nullable=False),
    Column("manager_full_name", String(200), nullable=True),
    Column("manager_position", String(100), nullable=True),
    Column("manager_address", Text, nullable=True),
    Column("manager_document_number", String(50), nullable=True),
    Column("manager_nationality", String(50), nullable=True),
    Column("manager_civil_status", String(50), nullable=True),
    Column("is_principal", Boolean, server_default=text("false"), nullable=False),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    Column("updated_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    Column("created_by", UUID, ForeignKey("person.person_id"), nullable=True),
    Column("updated_by", UUID, ForeignKey("person.person_id"), nullable=True),
)
