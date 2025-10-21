"""
Loan Payments Module

This module handles loan payment schedules and payment management for contracts.
It integrates with the database function sp_generate_loan_payment_schedule to create
payment schedules when contracts are created.
"""

from .models import *
from .schemas import *
from .service import LoanPaymentService
from .router import router

__all__ = [
    "LoanPaymentService",
    "router",
]
