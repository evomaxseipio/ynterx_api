"""Schemas for debtors module."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID


class DebtByCurrencySchema(BaseModel):
    """Schema for debt by currency data."""
    amount: float = Field(..., description="Debt amount")
    currency: str = Field(..., description="Currency code")
    total_contract: int = Field(..., description="Total number of contracts")


class ContractSchema(BaseModel):
    """Schema for contract data."""
    contract_loan_id: int = Field(..., description="Contract loan ID")
    contract_id: str = Field(..., description="Contract ID (UUID)")
    contract_number: str = Field(..., description="Contract number")
    loan_amount: float = Field(..., description="Loan amount")
    total_amount_due: float = Field(..., description="Total amount due")
    currency: str = Field(..., description="Currency code")
    start_date: date = Field(..., description="Contract start date")


class DebtorSchema(BaseModel):
    """Schema for debtor data."""
    client_id: str = Field(..., description="Client ID")
    client_type: str = Field(..., description="Client type (person or company)")
    client_name: str = Field(..., description="Client name")
    client_identification: str = Field(..., description="Client identification number")
    document_type: str = Field(..., description="Document type")
    client_active: bool = Field(..., description="Client active status")
    client_phone: Optional[str] = Field(None, description="Client phone number")
    client_email: Optional[str] = Field(None, description="Client email")
    client_address: Optional[str] = Field(None, description="Client address")
    total_contracts: int = Field(..., description="Total number of contracts")
    debt_by_currency: List[DebtByCurrencySchema] = Field(..., description="Debt breakdown by currency")
    contracts: List[ContractSchema] = Field(..., description="List of contracts")


class SummarySchema(BaseModel):
    """Schema for summary data."""
    total_debtors: int = Field(..., description="Total number of debtors")
    active_contracts: int = Field(..., description="Total active contracts")
    total_debt_usd: float = Field(..., description="Total debt in USD")
    exchange_rate_used: float = Field(..., description="Exchange rate used")
    sum_in_dop: float = Field(..., description="Total sum in DOP")
    sum_in_usd: float = Field(..., description="Total sum in USD")
    sum_in_other_currencies: float = Field(..., description="Total sum in other currencies")


class PaginationSchema(BaseModel):
    """Schema for pagination data."""
    total: int = Field(..., description="Total number of items")
    per_page: int = Field(..., description="Items per page")
    page: int = Field(..., description="Current page number")
    offset: int = Field(..., description="Offset for pagination")


class DebtorsResponseSchema(BaseModel):
    """Schema for debtors response."""
    success: bool = Field(..., description="Whether the operation was successful")
    error: Optional[str] = Field(None, description="Error code if any")
    message: str = Field(..., description="Response message")
    summary: SummarySchema = Field(..., description="Summary data")
    debtors: List[DebtorSchema] = Field(default_factory=list, description="List of debtors")
    pagination: PaginationSchema = Field(..., description="Pagination information")


