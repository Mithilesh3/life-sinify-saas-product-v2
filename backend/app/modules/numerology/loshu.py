# modules/numerology/loshu.py

from typing import Dict


def generate_loshu_grid(dob: str) -> Dict:
    if not dob:
        return {}

    digits = [int(d) for d in dob if d.isdigit()]
    grid = {str(i): digits.count(i) for i in range(1, 10)}

    missing = [k for k, v in grid.items() if v == 0]

    return {
        "grid_counts": grid,
        "missing_numbers": missing
    }