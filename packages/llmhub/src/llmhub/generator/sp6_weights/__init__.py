"""
SP6 - Weights: Derive scoring weights from RoleNeed.

Exports:
    - Weights (model)
    - derive_weights (function)
"""
from .models import Weights
from .calculator import derive_weights

__all__ = [
    "Weights",
    "derive_weights",
]
