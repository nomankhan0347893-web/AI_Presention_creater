import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Default Presentation Theme & Design Standards
DEFAULT_THEME = {
    "background_color": "#F8F9FA",
    "text_color": "#212529",
    "primary_color": "#0D6EFD",
    "accent_color": "#6C757D",
    "font_title": "Arial",
    "font_body": "Calibri",
    "aspect_ratio": "16:9"
}

# Strict Design Rules
MAX_TEXT_LINES_PER_SLIDE = 5
MAX_FONT_FAMILIES = 2
MAX_FONT_SIZES = 3

# Prohibited Buzzwords (Design Standard Rule)
PROHIBITED_BUZZWORDS = [
    "unlock", "revolutionize", "seamless", "cutting edge", "leverage",
    "robust", "delve", "empower", "game changer", "elevate", "synergy",
    "paradigm", "next-gen", "state-of-the-art"
]

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DIAGRAMS_DIR = os.path.join(STORAGE_DIR, "diagrams")
IMAGES_DIR = os.path.join(STORAGE_DIR, "images")
PREVIEWS_DIR = os.path.join(STORAGE_DIR, "previews")
OUTPUT_DIR = os.path.join(STORAGE_DIR, "output")

# Ensure required storage directories exist
for path in [STORAGE_DIR, DIAGRAMS_DIR, IMAGES_DIR, PREVIEWS_DIR, OUTPUT_DIR]:
    os.makedirs(path, exist_ok=True)
