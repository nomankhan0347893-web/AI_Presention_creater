import os
from config import PREVIEWS_DIR
from core.logger import logger

def render_html_to_png_preview(html_content: str, slide_num: int) -> str:
    """
    Renders HTML slide content into a 16:9 1920x1080 PNG screenshot preview.
    Uses Playwright headless browser if available, or HTML file fallback.
    """
    output_filename = f"slide_preview_{slide_num}.png"
    output_path = os.path.join(PREVIEWS_DIR, output_filename)
    html_temp_path = os.path.join(PREVIEWS_DIR, f"slide_{slide_num}.html")
    
    with open(html_temp_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(f"file:///{os.path.abspath(html_temp_path).replace('\\', '/')}")
            page.screenshot(path=output_path, full_page=False)
            browser.close()
        logger.info(f"Playwright rendered slide preview -> {output_path}")
        return output_path
    except Exception as e:
        clean_msg = str(e).encode("ascii", "ignore").decode("ascii")
        logger.warning(f"Playwright fallback active. Saved HTML file at {html_temp_path}")
        return html_temp_path

def render_all_slides_to_png(slides: list, theme) -> list:
    """
    Renders all HTML slides into 16:9 1920x1080 PNG screenshots in a single browser session.
    Much faster than launching Chrome per slide!
    """
    preview_paths = []
    
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            
            for slide in slides:
                output_filename = f"slide_preview_{slide.slide_number}.png"
                output_path = os.path.join(PREVIEWS_DIR, output_filename)
                html_temp_path = os.path.join(PREVIEWS_DIR, f"slide_{slide.slide_number}.html")
                
                body_content = slide.html_layout if slide.html_layout else "<h1>Layout Error</h1>"
                styles = slide.css_styles if slide.css_styles else f"body {{ background-color: {theme.background_color}; }}"
                html_content = f"<!DOCTYPE html>\n<html>\n<head>\n<style>\n{styles}\n</style>\n</head>\n<body>\n{body_content}\n</body>\n</html>"
                
                with open(html_temp_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    
                page.goto(f"file:///{os.path.abspath(html_temp_path).replace('\\', '/')}")
                page.screenshot(path=output_path, full_page=False)
                preview_paths.append(output_path)
                
            browser.close()
            logger.info(f"Playwright batch-rendered {len(slides)} slide previews successfully.")
            return preview_paths
            
    except Exception as e:
        clean_msg = str(e).encode("ascii", "ignore").decode("ascii")
        logger.warning(f"Playwright batch rendering failed: {clean_msg}. Falling back to single mode.")
        for slide in slides:
            body_content = slide.html_layout if slide.html_layout else "<h1>Layout Error</h1>"
            styles = slide.css_styles if slide.css_styles else f"body {{ background-color: {theme.background_color}; }}"
            html_content = f"<!DOCTYPE html>\n<html>\n<head>\n<style>\n{styles}\n</style>\n</head>\n<body>\n{body_content}\n</body>\n</html>"
            preview_paths.append(render_html_to_png_preview(html_content, slide.slide_number))
        return preview_paths
