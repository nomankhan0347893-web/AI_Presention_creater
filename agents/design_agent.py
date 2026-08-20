import os
from typing import List, Optional
from pydantic import BaseModel, Field
from core.state import DeckState, SlideElement, ElementPosition, ElementStyle
from config import DIAGRAMS_DIR, IMAGES_DIR
from core.logger import logger
from core.llm import llm_pro
import time
from langchain_core.prompts import ChatPromptTemplate

class DesignedSlide(BaseModel):
    html_layout: str = Field(description="HTML snippet representing the visual layout of the slide.")
    css_styles: str = Field(description="CSS styles applied to the HTML layout.")
    elements: List[SlideElement] = Field(description="Structured list of every text box, image, and diagram with precise positions (%, in) and styles.")

def run_design_agent(deck_state: DeckState) -> DeckState:
    """
    Design Agent: Lays each slide out using HTML/CSS following a design standard.
    Alongside the visual layout, it produces a structured description of each slide 
    (listing every text box, image, diagram, position, size, and content).
    """
    logger.info("Design Agent: Llaying out slides with HTML/CSS and generating structured descriptions...")
    
    theme = deck_state.theme
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "ROLE: You are the Design Layout Agent mapping content to strict predefined grid templates. "
                   "TASK: Construct a visually stunning and perfectly aligned HTML/CSS slide layout and output a structured list of elements matching the strict templates below. "
                   "RULES: "
                   "1. You MUST select and implement the exact coordinate grid for the requested layout_type. DO NOT invent your own layout. "
                   "   - 'title_slide': Title (left:'10%', top:'20%', width:'80%', height:'35%', font_size:'40pt', font_weight:'bold'), Subtitle/Presenter (left:'10%', top:'60%', width:'80%', height:'30%', font_size:'24pt'). Group subtitle and presenter name into this single element using multiple lines. Decorate HTML/CSS with abstract shapes. NEVER include images or diagrams. "
                   "   - 'section_divider': Massive Watermark Number (left:'60%', top:'10%', width:'30%', height:'80%', font_size:'160pt', opacity: 0.1), Section Title (left:'10%', top:'30%', width:'50%', height:'25%', font_size:'36pt'), Subtitle/Body (left:'10%', top:'60%', width:'50%', height:'30%', font_size:'20pt'). NEVER include images or diagrams on section dividers. "
                   "   - 'standard_content': Title (left:'5%', top:'5%', width:'90%', height:'15%', font_size:'32pt'), Body (left:'5%', top:'28%', width:'45%', height:'64%', font_size:'18pt'), Image/Diagram (left:'54%', top:'28%', width:'42%', height:'64%'). (If no image/diagram, let Body span width '90%'). "
                   "   - 'card_grid': Title (left:'5%', top:'5%', width:'90%', height:'15%', font_size:'32pt'). Break content into small individual text elements (cards) positioned in a 2x2 or 3x3 grid using top:'28%|60%' and left:'5%|35%|65%'. Use solid background colors and a slight border-radius. NEVER include images or diagrams. "
                   "   - 'closing_slide': Title (left:'10%', top:'35%', width:'80%', height:'30%', font_size:'40pt') centered. NEVER include images or diagrams. "
                   "2. Ensure consistent typography hierarchy, padding, and alignment across all outputs. Use max 2 fonts. "
                   "3. Use the provided Theme colors (Background, Primary, Accent, Secondary_BG) intelligently via CSS. "
                   "4. ALONGSIDE the HTML/CSS, produce a deeply structured description mapping every heading, text block, image, and diagram to a separate element in the JSON array using the precise coordinates dictated above. "
                   "5. If 'Has Image' is True, you MUST include an element with type='image'. If 'Has Diagram' is True, include type='diagram'. For section_divider, title_slide, closing_slide, and card_grid, do NOT include image or diagram elements. "
                   "6. CRITICAL: The HTML preview must perfectly match the native PPTX output. DO NOT use advanced CSS like 'backdrop-filter', 'glassmorphism', complex gradients, or drop-shadows. Use only FLAT solid colors and basic border-radius. "
                   "7. CRITICAL: DO NOT invent custom font colors in the JSON elements. You MUST set color to the provided text_color variable for body text, or primary color for headings to ensure readability. "
                   "8. CRITICAL: Group all body bullet points into a SINGLE text element with a list content=['bullet 1', 'bullet 2', 'bullet 3'] assigned to body coordinates. Group Subtitle and Presenter into a SINGLE element. Never create multiple separate JSON elements at identical top/left coordinates. For 'card_grid' cards, you MUST explicitly set the 'background_color' property inside the JSON 'style' object (e.g., to the sec_bg color) so the PPTX builder draws the shape!"),
        ("user", "Slide Context:\nTitle: {title}\nLayout Type: {layout_type}\nContent: {content}\nHas Image: {has_image}\nHas Diagram: {has_diagram}\n"
                 "Theme colors: Background {bg}, Primary {primary}, Text {text_color}, Accent {accent}, Secondary BG {sec_bg}.\n"
                 "Return the html_layout, css_styles, and the elements list.")
    ])
    
    chain = prompt | llm_pro.with_structured_output(DesignedSlide)
    
    for slide in deck_state.slides:
        # Sleep to avoid hitting Gemini Free Tier 15 Requests-Per-Minute limit
        time.sleep(4)
        
        logger.info(f"Design Agent processing Slide {slide.slide_number}...")
        
        try:
            content_str = "\\n".join(slide.raw_content)
            has_img = False if slide.layout_type in ["section_divider", "title_slide", "closing_slide", "card_grid"] else slide.has_image
            has_diag = False if slide.layout_type in ["section_divider", "title_slide", "closing_slide", "card_grid"] else slide.has_diagram
            
            result = chain.invoke({
                "title": slide.title,
                "layout_type": slide.layout_type,
                "content": content_str,
                "has_image": has_img,
                "has_diagram": has_diag,
                "bg": theme.background_color,
                "primary": theme.primary_color,
                "text_color": theme.text_color,
                "accent": getattr(theme, 'accent_color', '#000000'),
                "sec_bg": getattr(theme, 'secondary_bg_color', '#FFFFFF')
            })
            
            slide.html_layout = result.html_layout
            slide.css_styles = result.css_styles
            
            # Map dynamic paths
            diagram_path = os.path.join(DIAGRAMS_DIR, f"diagram_slide_{slide.slide_number}.png") if slide.has_diagram else None
            image_path = os.path.join(IMAGES_DIR, f"image_slide_{slide.slide_number}.jpg") if slide.has_image else None
            
            for elem in result.elements:
                if elem.type:
                    elem.type = elem.type.lower()
                    if "diagram" in elem.type:
                        elem.type = "diagram"
                        elem.file_path = diagram_path
                    elif "image" in elem.type:
                        elem.type = "image"
                        elem.file_path = image_path
            
            slide.elements = result.elements
            
        except Exception as e:
            logger.error(f"Design Agent failed for Slide {slide.slide_number}: {e}")
        
    deck_state.current_step = "DESIGN"
    return deck_state
