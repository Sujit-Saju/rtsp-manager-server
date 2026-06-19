# ============================================
# File     : run.py
# Author   : Sujit
# Created  : 2026-06-10
# Desc     : Application entry point running
#            Quart app via Hypercorn server
# ============================================

from app import create_app
from app.core.config import Config
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
