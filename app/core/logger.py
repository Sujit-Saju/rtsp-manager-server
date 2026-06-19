# ============================================
# File     : logger.py
# Author   : Sujit
# Created  : 2026-06-10
# Desc     : Logger setup for application-wide
#            structured logging with formatting
# ============================================

import logging

def setup_logger():
    logging.basicConfig(
        level   = logging.INFO,
        format  = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger("ai-vms")

logger = setup_logger()