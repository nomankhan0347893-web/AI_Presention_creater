import os
import json
import random
from config import STORAGE_DIR

THEME_MEMORY_FILE = os.path.join(STORAGE_DIR, 'theme_memory.json')

PROFESSIONAL_PALETTES = [
    {
        'id': 'emerald_cyan',
        'background_color': '#0F292B',
        'text_color': '#FFFFFF',
        'primary_color': '#38B2AC',
        'accent_color': '#81E6D9',
        'secondary_bg_color': '#1A3638',
        'font_title': 'Georgia',
        'font_body': 'Arial'
    },
    {
        'id': 'navy_coral',
        'background_color': '#0B1120',
        'text_color': '#F8FAFC',
        'primary_color': '#FB7185',
        'accent_color': '#FDA4AF',
        'secondary_bg_color': '#1E293B',
        'font_title': 'Georgia',
        'font_body': 'Arial'
    },
    {
        'id': 'charcoal_gold',
        'background_color': '#18181B',
        'text_color': '#FAFAFA',
        'primary_color': '#F59E0B',
        'accent_color': '#FCD34D',
        'secondary_bg_color': '#27272A',
        'font_title': 'Georgia',
        'font_body': 'Arial'
    },
    {
        'id': 'slate_mint',
        'background_color': '#0F172A',
        'text_color': '#F1F5F9',
        'primary_color': '#34D399',
        'accent_color': '#6EE7B7',
        'secondary_bg_color': '#1E293B',
        'font_title': 'Georgia',
        'font_body': 'Arial'
    },
    {
        'id': 'classic_light',
        'background_color': '#F8FAFC',
        'text_color': '#0F172A',
        'primary_color': '#2563EB',
        'accent_color': '#60A5FA',
        'secondary_bg_color': '#E2E8F0',
        'font_title': 'Arial',
        'font_body': 'Calibri'
    }
]

def get_next_theme() -> dict:
    history = []
    if os.path.exists(THEME_MEMORY_FILE):
        try:
            with open(THEME_MEMORY_FILE, 'r') as f:
                history = json.load(f)
        except Exception:
            pass
            
    recent_ids = history[-2:] if len(history) >= 2 else history
    
    available_palettes = [p for p in PROFESSIONAL_PALETTES if p['id'] not in recent_ids]
    if not available_palettes:
        available_palettes = PROFESSIONAL_PALETTES
        
    selected = random.choice(available_palettes)
    
    history.append(selected['id'])
    history = history[-5:]
    
    with open(THEME_MEMORY_FILE, 'w') as f:
        json.dump(history, f)
        
    return selected
