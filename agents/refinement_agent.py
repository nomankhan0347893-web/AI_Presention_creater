import os
from typing import List, Optional
from pydantic import BaseModel, Field
from core.state import DeckState, SlideState, SlideElement
from tools.browser_tool import render_all_slides_to_png, render_html_to_png_preview
from core.logger import logger
from core.llm import llm_pro
import time
from langchain_core.prompts import ChatPromptTemplate

class RefinementReview(BaseModel):
    meets_standards: bool = Field(description="True if the slide requires no further adjustments.")
    feedback: str = Field(description="Reasoning for adjustments or approval.")
    refined_elements: Optional[List[SlideElement]] = Field(description="If adjustments are needed, provide the fully corrected list of slide elements.")
    refined_html: Optional[str] = Field(description="If layout adjustments are needed, provide the updated HTML.")
    refined_css: Optional[str] = Field(description="If layout adjustments are needed, provide the updated CSS.")

def run_refinement_agent(deck_state: DeckState) -> DeckState:
    """
    Refinement Agent: Takes design from good to professional.
    Checks alignment, spacing, text length, color use, image treatment.
    Fixes issues directly and loops until every slide meets the standard.
    """
    logger.info("Refinement Agent: Perfecting the deck against design standards...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "ROLE: You are the final Refinement & QA Agent. "
                   "TASK: Take the design from 'good' to 'genuinely professional' by actively fixing visual and structural flaws. "
                   "RULES: "
                   "1. Ensure strict adherence to the coordinate grid templates. Elements MUST NOT drift or overlap. "
                   "2. Check typography: Maximum 2 font families allowed. Check text length: Maximum 5 lines of body text per text block. "
                   "3. Ensure the colors strictly match the theme. No rogue colors. "
                   "4. If anything falls short, do not just flag it: FIX IT DIRECTLY. Provide the modified HTML/CSS and structurally updated element arrays. "
                   "5. Remove repetitive bullets, trim verbose text, fix overlapping positions, and apply standard layout grids. "
                   "6. If it meets standards perfectly without any required changes, set meets_standards=true. If you fix anything, set it to false so the pipeline updates the slide. "
                   "Do not stop until you reason the slide is flawlessly professional."),
        ("user", "Slide {slide_num} Data:\n"
                 "HTML: {html}\n"
                 "CSS: {css}\n"
                 "Elements: {elements}\n"
                 "Review and refine.")
    ])
    
    chain = prompt | llm_pro.with_structured_output(RefinementReview)
    
    for slide in deck_state.slides:
        logger.info(f"Refinement Agent: Reviewing Slide {slide.slide_number}...")
        elements_str = str([e.model_dump() for e in slide.elements])
        
        try:
            review = chain.invoke({
                "slide_num": slide.slide_number,
                "html": slide.html_layout or "N/A",
                "css": slide.css_styles or "N/A",
                "elements": elements_str
            })
            
            if review.meets_standards:
                logger.info(f"Slide {slide.slide_number} meets standards. Feedback: {review.feedback}")
            else:
                logger.info(f"Slide {slide.slide_number} refined. Feedback: {review.feedback}")
                if review.refined_elements:
                    slide.elements = review.refined_elements
                if review.refined_html:
                    slide.html_layout = review.refined_html
                if review.refined_css:
                    slide.css_styles = review.refined_css
                    
        except Exception as e:
            logger.error(f"Refinement Agent failed on Slide {slide.slide_number}: {e}")

    # Render all final HTML slide previews in a single fast browser session
    logger.info("Refinement Agent: Batch-rendering final slide previews with Playwright...")
    render_all_slides_to_png(deck_state.slides, deck_state.theme)

    deck_state.current_step = "REFINEMENT"
    return deck_state

def _build_html_for_preview(slide: SlideState, theme) -> str:
    """Combines LLM-generated HTML and CSS into a standalone document for Playwright rendering."""
    body_content = slide.html_layout if slide.html_layout else "<h1>Layout Error</h1>"
    styles = slide.css_styles if slide.css_styles else f"body {{ background-color: {theme.background_color}; }}"
    
    return f"<!DOCTYPE html>\n<html>\n<head>\n<style>\n{styles}\n</style>\n</head>\n<body>\n{body_content}\n</body>\n</html>"
