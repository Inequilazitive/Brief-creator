# app/config.py

from pathlib import Path

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
BRAND_GUIDES_DIR = DATA_DIR / "brand_guides"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUTS_DIR = BASE_DIR / "outputs"
BRIEFS_DIR = OUTPUTS_DIR / "markdown"
PDF_DIR = OUTPUTS_DIR / "pdf"
ZIP_DIR = OUTPUTS_DIR / "zip"

# === Template files ===
EVERGREEN_TEMPLATE_PATH = TEMPLATES_DIR / "evergreen_template.txt"
EVERGREEN_SYSTEM_PROMPT_PATH = TEMPLATES_DIR / "evergreen_system.txt"
EVERGREEN_USER_PROMPT_PATH = TEMPLATES_DIR / "evergreen_user.txt"
PROMO_TEMPLATE_PATH = TEMPLATES_DIR / "promo_template.txt"

# === Output file naming ===
BRIEF_FILENAME_PATTERN = "brief_{index:02d}.md"

# === Default limits ===
NUM_BRIEFS = 20
NUM_STATICS = 10
NUM_VIDEOS = 10

# === Model Configuration ===
VLM_MODEL_NAME = "HuggingFaceTB/SmolVLM-Instruct"
LLM_MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
MAX_NEW_TOKENS = 100000   

# === Ensure folders exist on startup ===
for folder in [UPLOADS_DIR, PROCESSED_DIR, BRAND_GUIDES_DIR, BRIEFS_DIR, PDF_DIR, ZIP_DIR]:
    folder.mkdir(parents=True, exist_ok=True)