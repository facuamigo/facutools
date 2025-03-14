import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get constants from environment with fallbacks
PROJECT_NAME = os.getenv("FACUTOOLS_PROJECT_NAME", "guias-uba")
PARENT = os.getenv("FACUTOOLS_PARENT", f"projects/{PROJECT_NAME}/locations/global")