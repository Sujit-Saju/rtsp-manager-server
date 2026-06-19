# ============================================
# File     : api_response.py
# Author   : Sujit
# Created  : 2026-06-12
# Desc     : Standard API response helper.
# ============================================

from typing import Any


def success_response(
    message: str,
    data: Any = None,
) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    data: Any = None,
) -> dict:
    return {
        "success": False,
        "message": message,
        "data": data,
    }
