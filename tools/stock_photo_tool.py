import os
import requests
from PIL import Image, ImageDraw, ImageFont
from config import UNSPLASH_ACCESS_KEY, PEXELS_API_KEY, IMAGES_DIR
from core.logger import logger

def search_and_download_stock_image(query: str, slide_num: int) -> str:
    """
    Searches Unsplash or Pexels API for contextually relevant stock photos.
    Evaluates image and downloads to storage/images/.
    Falls back to a styled high-resolution visual placeholder if API keys are missing.
    """
    output_filename = f"image_slide_{slide_num}.jpg"
    output_path = os.path.join(IMAGES_DIR, output_filename)
    
    # Clean search query
    clean_query = query.strip().replace(" ", "+")
    
    # 1. Try Unsplash API if key available
    if UNSPLASH_ACCESS_KEY:
        try:
            url = f"https://api.unsplash.com/search/photos?page=1&query={clean_query}&per_page=3&client_id={UNSPLASH_ACCESS_KEY}"
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    img_url = results[0]["urls"]["regular"]
                    img_resp = requests.get(img_url, timeout=10)
                    if img_resp.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(img_resp.content)
                        logger.info(f"Downloaded Unsplash photo for '{query}' -> {output_path}")
                        return output_path
        except Exception as e:
            logger.warning(f"Unsplash API request failed: {e}")
            
    # 2. Try Pexels API if key available
    if PEXELS_API_KEY:
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/v1/search?query={clean_query}&per_page=3"
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200:
                photos = resp.json().get("photos", [])
                if photos:
                    img_url = photos[0]["src"]["large"]
                    img_resp = requests.get(img_url, timeout=10)
                    if img_resp.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(img_resp.content)
                        logger.info(f"Downloaded Pexels photo for '{query}' -> {output_path}")
                        return output_path
        except Exception as e:
            logger.warning(f"Pexels API request failed: {e}")

    # 3. Fallback: Styled Visual Stock Image Generator
    return _generate_fallback_stock_image(query, output_path)


def _generate_fallback_stock_image(query: str, output_path: str) -> str:
    """Generates a high-quality stylized visual background with text overlay zone."""
    img = Image.new("RGB", (1280, 720), (28, 40, 56))
    draw = ImageDraw.Draw(img)
    
    # Abstract aesthetic geometric background
    draw.rectangle([0, 0, 1280, 720], fill=(20, 30, 45))
    draw.polygon([(0, 0), (800, 0), (400, 720), (0, 720)], fill=(13, 110, 253))
    draw.polygon([(800, 0), (1280, 0), (1280, 720), (600, 720)], fill=(33, 45, 65))
    
    # Text overlay
    draw.text((60, 600), f"VISUAL ASSET: {query.upper()}", fill=(255, 255, 255))
    
    img.save(output_path, "JPEG", quality=90)
    logger.info(f"Generated fallback stock photo asset for '{query}' -> {output_path}")
    return output_path
