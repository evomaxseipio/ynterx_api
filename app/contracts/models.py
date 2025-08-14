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

# Tabla contract (ajustada al esquema definitivo)
contract = Table(
    "contract",
    metadata,
    Column("contract_id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("contract_number", String(50), unique=True),
    Column("contract_type_id", Integer, nullable=False),
    Column("contract_service_id", Integer),
    Column("contract_status_id", Integer, nullable=False, server_default=text("1")),
    Column("contract_date", Date, nullable=False, server_default=text("CURRENT_DATE")),
    Column("start_date", Date),
    Column("end_date", Date),
    Column("title", String(200)),
    Column("description", Text),
    Column("template_name", String(100)),
    Column("generated_filename", String(200)),
    Column("file_path", Text),
    Column("folder_path", Text),
    Column("version", Integer, server_default=text("1")),
    Column("is_active", Boolean, server_default=text("true")),
    Column("created_by", UUID),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
)

# Tabla contract_participant
contract_participant = Table(
    "contract_participant",
    metadata,
    Column("contract_participant_id", Integer, primary_key=True),
    Column("contract_id", UUID, ForeignKey("contract.contract_id", ondelete="CASCADE"), nullable=False),
    Column("person_id", UUID, ForeignKey("person.person_id"), nullable=False),
    Column("person_type_id", Integer),
    Column("company_id", Integer),
    Column("is_primary", Boolean, server_default=text("false")),
    Column("participation_percentage", Numeric(5,2)),
    Column("notes", Text),
    Column("is_active", Boolean, server_default=text("true")),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
)

# Tabla contract_loan (simplificada)
contract_loan = Table(
    "contract_loan",
    metadata,
    Column("contract_loan_id", Integer, primary_key=True),
    Column("contract_id", UUID, ForeignKey("contract.contract_id", ondelete="CASCADE"), nullable=False),
    Column("loan_amount", Numeric(15,2), nullable=False),
    Column("currency", String(3), server_default=text("'USD'")),
    Column("interest_rate", Numeric(5,4)),
    Column("term_months", Integer),
    Column("loan_type", String(30)),
    Column("monthly_payment", Numeric(15,2)),
    Column("final_payment", Numeric(15,2)),
    Column("discount_rate", Numeric(5,4)),
    Column("payment_qty_quotes", Integer),
    Column("payment_type", String(20)),
    Column("is_active", Boolean, server_default=text("true")),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
)

# Adjust this import according to your database setup
# from app.database import Base  # Replace with your actual Base import

Base = declarative_base()  # Remove this line if you already have Base defined elsewhere

class Contract(Base):
    """SQLAlchemy model for storing contract records in database"""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    client_name = Column(String, index=True)
    contract_date = Column(String)
    amount = Column(String)
    description = Column(Text)
    template_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    original_data = Column(Text)  # Store the complete JSON data as string
    file_size = Column(Integer)  # File size in bytes

    def __repr__(self):
        return f"<Contract(id={self.id}, filename='{self.filename}', client='{self.client_name}')>"

class Template(Base):
    """SQLAlchemy model for storing template information"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String, default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)  # Track how many times template was used

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', filename='{self.filename}')>"



# Modelo para property
property_table = Table(
    "property",
    metadata,
    Column(
        "property_id",
        Integer,
        primary_key=True,
        autoincrement=True
    ),
    Column("property_type", String(50), nullable=False),
    Column("cadastral_number", String(50), nullable=True),
    Column("title_number", Text, nullable=True),
    Column("surface_area", Numeric(12, 2), nullable=True),
    Column("covered_area", Numeric(12, 2), nullable=True),
    Column("property_value", Numeric(15, 2), nullable=True),
    Column("property_owner", String(100), nullable=True),
    Column("owner_civil_status", String(50), nullable=True),
    Column("owner_document_number", String(50), nullable=True),
    Column("owner_nationality", String(50), nullable=True),
    Column("currency", String(3), nullable=False, server_default="USD"),
    Column("property_description", Text, nullable=True),
    Column("address_line1", Text, nullable=True),
    Column("address_line2", Text, nullable=True),
    Column("city_id", Integer, ForeignKey("city.city_id"), nullable=True),
    Column("postal_code", String(20), nullable=True),
    Column("image_path", Text, nullable=True),
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
    Column("created_by", UUID, ForeignKey("person.person_id"), nullable=True),
    Column("updated_by", UUID, ForeignKey("person.person_id"), nullable=True),
)

# Modelo para contract_property (relación many-to-many)
contract_property = Table(
    "contract_property",
    metadata,
    Column(
        "contract_property_id",
        Integer,
        primary_key=True,
        autoincrement=True
    ),
    Column(
        "contract_id",
        UUID,
        ForeignKey("contract.contract_id", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "property_id",
        Integer,
        ForeignKey("property.property_id"),
        nullable=False
    ),
    Column("property_role", String(30), nullable=False),
    Column("is_primary", Boolean, server_default=expression.false()),
    Column("notes", Text, nullable=True),
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

# Modelo para client_referrer (relación Cliente ↔ Referidor)
client_referrer = Table(
    "client_referrer",
    metadata,
    Column(
        "client_referrer_id",
        BigInteger,
        primary_key=True,
        autoincrement=True
    ),
    Column(
        "client_id",
        UUID,
        ForeignKey("client.client_id", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "referrer_id",
        UUID,
        ForeignKey("person.person_id", ondelete="CASCADE"),
        nullable=False
    ),
    Column(
        "relation_date",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
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
        "created_by",
        UUID,
        ForeignKey("person.person_id"),
        nullable=True,
    ),
    Column(
        "updated_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    Column(
        "updated_by",
        UUID,
        ForeignKey("person.person_id"),
        nullable=True,
    ),
    # Índice único para evitar duplicados
    UniqueConstraint('client_id', 'referrer_id', 'is_active', name='uq_client_referrer_active')
)

# New contract_bank_account table
contract_bank_account = Table(
    "contract_bank_account",
    metadata,
    Column(
        "bank_account_id",
        BigInteger,
        primary_key=True,
        autoincrement=True,
    ),
    Column("contract_id", UUID, ForeignKey("contract.contract_id", ondelete="CASCADE"), nullable=False),
    Column(
        "client_person_id",
        UUID,
        ForeignKey("person.person_id"),
        nullable=True,
    ),
    Column("holder_name", String(100), nullable=False),
    Column("bank_name", String(100), nullable=False),
    Column("account_number", String(50), nullable=False),
    Column("account_type", String(20), nullable=False),
    Column("bank_code", String(20), nullable=True),
    Column("swift_code", String(20), nullable=True),
    Column("iban", String(34), nullable=True),
    Column("currency", String(3), nullable=False, server_default=text("'USD'")),
    Column(
        "created_at",
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    CheckConstraint(
        "account_type IN ('corriente', 'ahorros', 'inversion', 'other')",
        name="contract_bank_account_account_type_check",
    ),
)

class ContractParagraph(Base):
    """SQLAlchemy model for contract paragraphs"""
    __tablename__ = "contract_paragraphs"

    id = Column(Integer, primary_key=True, index=True)
    contract_type_id = Column(Integer, nullable=False)
    section = Column(String(100), nullable=False)
    order_position = Column(Integer, nullable=False, default=1)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    paragraph_variables = Column(Text)  # JSONB as text for now
    paragraph_description = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ContractParagraph(id={self.id}, section='{self.section}', title='{self.title}')>"
