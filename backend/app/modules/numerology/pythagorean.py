# modules/numerology/pythagorean.py

from datetime import datetime
from typing import Dict


# =====================================================
# CORE REDUCTION ENGINE
# =====================================================

def reduce_number(num: int) -> int:
    """
    Reduces a number to a single digit,
    preserving master numbers 11 and 22.
    """
    while num > 9 and num not in (11, 22):
        num = sum(int(d) for d in str(num))
    return num


# =====================================================
# LIFE PATH NUMBER
# =====================================================

def calculate_life_path(dob: str) -> int:
    """
    dob format: YYYY-MM-DD
    """

    if not dob:
        return 0

    try:
        dt = datetime.strptime(dob, "%Y-%m-%d")
    except Exception:
        return 0

    total = dt.day + dt.month + dt.year
    return reduce_number(total)


# =====================================================
# DESTINY / EXPRESSION NUMBER
# =====================================================

def calculate_destiny(name: str) -> int:
    """
    Basic A=1 ... Z=26 mapping
    """

    if not name:
        return 0

    total = sum(ord(c.upper()) - 64 for c in name if c.isalpha())
    return reduce_number(total)


# =====================================================
# PUBLIC CONTRACT FUNCTION (SAFE)
# =====================================================

def generate_pythagorean_numbers(
    identity: Dict,
    birth_details: Dict
) -> Dict:
    """
    Standardized output contract for orchestration layer.
    Safe against None inputs.
    """

    identity = identity or {}
    birth_details = birth_details or {}

    name = identity.get("full_name", "")
    dob = birth_details.get("date_of_birth")

    life_path = calculate_life_path(dob)
    destiny = calculate_destiny(name)

    return {
        "life_path_number": life_path,
        "destiny_number": destiny,
        "expression_number": destiny,
        "system": "pythagorean"
    }