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

# Tabla payment_schedule (cronograma de pagos)
payment_schedule = Table(
    "payment_schedule",
    metadata,
    Column("payment_schedule_id", Integer, primary_key=True),
    Column("contract_loan_id", Integer, ForeignKey("contract_loan.contract_loan_id", ondelete="CASCADE"), nullable=False),
    Column("payment_number", Integer, nullable=False),
    Column("due_date", Date, nullable=False),
    Column("amount_due", Numeric(15,2), nullable=False),
    Column("capital_amount", Numeric(15,2), nullable=False),
    Column("interest_amount", Numeric(15,2), nullable=False),
    Column("balance", Numeric(15,2), nullable=False),
    Column("payment_status", String(20), server_default=text("'pending'")),  # pending, paid, overdue, partial
    Column("payment_date", Date),
    Column("amount_paid", Numeric(15,2)),
    Column("notes", Text),
    Column("is_active", Boolean, server_default=text("true")),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
)

# Tabla payment_transactions (transacciones de pago)
payment_transactions = Table(
    "payment_transactions",
    metadata,
    Column("payment_transaction_id", Integer, primary_key=True),
    Column("payment_schedule_id", Integer, ForeignKey("payment_schedule.payment_schedule_id", ondelete="CASCADE"), nullable=False),
    Column("transaction_type", String(20), nullable=False),  # payment, refund, adjustment
    Column("amount", Numeric(15,2), nullable=False),
    Column("payment_method", String(30)),  # cash, bank_transfer, check, etc.
    Column("reference_number", String(50)),
    Column("transaction_date", Date, nullable=False),
    Column("processed_by", UUID),
    Column("notes", Text),
    Column("is_active", Boolean, server_default=text("true")),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
)

# Base declarativa para modelos SQLAlchemy
Base = declarative_base()

class PaymentSchedule(Base):
    """SQLAlchemy model for payment schedule records"""
    __tablename__ = "payment_schedule"

    payment_schedule_id = Column(Integer, primary_key=True, index=True)
    contract_loan_id = Column(Integer, ForeignKey("contract_loan.contract_loan_id"), nullable=False)
    payment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    amount_due = Column(Numeric(15,2), nullable=False)
    capital_amount = Column(Numeric(15,2), nullable=False)
    interest_amount = Column(Numeric(15,2), nullable=False)
    balance = Column(Numeric(15,2), nullable=False)
    payment_status = Column(String(20), default="pending")
    payment_date = Column(Date)
    amount_paid = Column(Numeric(15,2))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentTransaction(Base):
    """SQLAlchemy model for payment transaction records"""
    __tablename__ = "payment_transactions"

    payment_transaction_id = Column(Integer, primary_key=True, index=True)
    payment_schedule_id = Column(Integer, ForeignKey("payment_schedule.payment_schedule_id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Numeric(15,2), nullable=False)
    payment_method = Column(String(30))
    reference_number = Column(String(50))
    transaction_date = Column(Date, nullable=False)
    processed_by = Column(UUID)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
