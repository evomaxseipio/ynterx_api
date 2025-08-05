from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    String,
    Table,
    Text,
    CheckConstraint,
    UniqueConstraint,
    text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import expression

from app.database import metadata

contract_paragraphs = Table(
    "contract_paragraphs",
    metadata,
    Column(
        "paragraph_id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),
    Column("person_role", Text, nullable=False),
    Column("contract_type", Text, nullable=False),
    Column("section", Text, nullable=False),
    Column("order_position", Integer, default=1),
    Column("title", String(255), nullable=True),
    Column("paragraph_content", Text, nullable=False),
    Column("paragraph_variables", JSONB, nullable=True),
    Column("contract_services", Text, default="mortgage"),
    Column(
        "is_active",
        Boolean,
        server_default=expression.true(),
        nullable=False,
    ),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),

    # Constraints
    UniqueConstraint(
        "person_role",
        "contract_type",
        "section",
        "contract_services",
        name="contract_paragraphs_person_role_contract_type_section_contr_key"
    ),
    CheckConstraint(
        "contract_type = ANY (ARRAY['juridica'::text, 'fisica_soltera'::text, 'fisica_casada'::text])",
        name="contract_paragraphs_contract_type_check"
    ),
    CheckConstraint(
        "contract_services = ANY (ARRAY['mortgage'::text, 'services'::text, 'loan'::text])",
        name="contract_paragraphs_contract_services_check"
    ),
)

# Indexes
Index(
    "idx_contract_paragraphs_lookup",
    contract_paragraphs.c.person_role,
    contract_paragraphs.c.contract_type,
    contract_paragraphs.c.section,
    contract_paragraphs.c.contract_services,
    contract_paragraphs.c.is_active,
)

Index(
    "idx_contract_paragraphs_order",
    contract_paragraphs.c.order_position,
)
