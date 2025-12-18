# =========================================================
# MODELS PACKAGE
# =========================================================
# Centraliza a importação dos models do sistema
# Facilita uso em:
# - Migrations
# - Seeds
# - Queries
# - Relatórios
# =========================================================

from app.extensions import db

# ==============================
# CORE
# ==============================
from .tenant import Tenant
from .user import User

# ==============================
# AGENDA / OPERAÇÃO
# ==============================
from .service import Service
from .appointment import Appointment
from .available_slot import AvailableSlot

# ==============================
# FINANCEIRO
# ==============================
from .payment import Payment
from .expense import Expense
from .cash_session import CashSession
from .cash_movement import CashMovement

# ==============================
# EXPORTS
# ==============================
__all__ = [
    # Core
    "Tenant",
    "User",

    # Agenda
    "Service",
    "Appointment",
    "AvailableSlot",

    # Financeiro
    "Payment",
    "Expense",
    "CashSession",
    "CashMovement",
]
