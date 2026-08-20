import os
import requests
from PIL import Image, ImageDraw, ImageFont
from config import DIAGRAMS_DIR
from core.logger import logger

def render_mermaid_to_png(mermaid_code: str, slide_num: int) -> str:
    """
    Renders Mermaid code to a PNG file using the Kroki REST API or local PIL visual generator fallback.
    Returns the file path of the rendered diagram PNG.
    """
    output_filename = f"diagram_slide_{slide_num}.png"
    output_path = os.path.join(DIAGRAMS_DIR, output_filename)
    
    # Clean up mermaid code
    clean_code = mermaid_code.strip()
    if clean_code.startswith("```mermaid"):
        clean_code = clean_code[len("```mermaid"):].strip()
    elif clean_code.startswith("```"):
        clean_code = clean_code[3:].strip()
        
    if clean_code.endswith("```"):
        clean_code = clean_code[:-3].strip()
        
    try:
        # Use Kroki API for high quality Mermaid rendering
        url = "https://kroki.io/mermaid/png"
        response = requests.post(url, data=clean_code.encode('utf-8'), headers={"Content-Type": "text/plain"}, timeout=10)
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Successfully rendered Mermaid diagram via Kroki API -> {output_path}")
            return output_path
        else:
            logger.warning(f"Kroki API returned status {response.status_code}, switching to fallback renderer.")
    except Exception as e:
        logger.warning(f"Network call to Kroki failed: {e}. Using fallback diagram renderer.")

    # Fallback Visual Diagram Generator using PIL
    return _generate_fallback_diagram_png(clean_code, output_path)


def _generate_fallback_diagram_png(code: str, output_path: str) -> str:
    """Creates a clean diagram placeholder box with text layout."""
    img = Image.new("RGBA", (800, 500), (240, 244, 248, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer box
    draw.rectangle([20, 20, 780, 480], outline=(13, 110, 253), width=4)
    draw.text((40, 40), "PROCESS / WORKFLOW DIAGRAM", fill=(13, 110, 253))
    
    # Parse lines to draw boxes
    lines = [l.strip() for l in code.split("\n") if "-->" in l or "[" in l or "graph" in l or "flowchart" in l]
    y_offset = 100
    for i, line in enumerate(lines[:5]):
        draw.rectangle([60, y_offset, 740, y_offset + 50], fill=(255, 255, 255), outline=(108, 117, 125), width=2)
        draw.text((80, y_offset + 15), line[:70], fill=(33, 37, 41))
        y_offset += 70
        
    img.save(output_path, "PNG")
    logger.info(f"Fallback diagram saved -> {output_path}")
    return output_path
