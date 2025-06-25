"""Models for user-related tables."""

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import expression

from app.database import metadata

users = Table(
    "users",
    metadata,
    Column("user_id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("person_id", UUID, ForeignKey("person.person_id"), nullable=False),
    Column("username", String(50), unique=True, nullable=False),
    Column("email", String(255), unique=True, nullable=False),
    Column("password_hash", String(255), nullable=False),
    Column("password_salt", String(255), nullable=False),
    Column("user_role_id", Integer, ForeignKey("user_role.user_role_id"), nullable=False),
    Column(
        "last_login",
        TIMESTAMP,
        nullable=True,
    ),
    Column("login_attempts", Integer, server_default=text("0")),
    Column("locked_until", TIMESTAMP, nullable=True),
    Column("password_reset_token", String(255), nullable=True),
    Column("password_reset_expires", TIMESTAMP, nullable=True),
    Column(
        "email_verified",
        Boolean,
        server_default=expression.false(),
        nullable=False,
    ),
    Column("email_verification_token", String(255), nullable=True),
    Column(
        "two_factor_enabled",
        Boolean,
        server_default=expression.false(),
        nullable=False,
    ),
    Column("two_factor_secret", String(255), nullable=True),
    Column("session_token", String(255), nullable=True),
    Column("session_expires", TIMESTAMP, nullable=True),
    Column("preferences", JSONB, nullable=True),
    Column("language", String(10), server_default=text("'en'")),
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
    Column("created_by", UUID, ForeignKey("users.user_id"), nullable=True),
    Column("updated_by", UUID, ForeignKey("users.user_id"), nullable=True),
)

user_roles = Table(
    "user_roles",
    metadata,
    Column(
        "user_role_id",
        Integer,
        primary_key=True,
        server_default=text("nextval('user_roles_user_role_id_seq')"),
    ),
    Column("role_name", String(255), nullable=False),
    Column("role_description", String(255), nullable=True),
    Column("permissions", JSONB, nullable=False),
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
