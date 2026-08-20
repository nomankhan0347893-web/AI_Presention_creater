from typing import List, Optional
from pydantic import BaseModel, Field
from core.state import DeckState, SlideState
from tools.buzzword_tool import check_and_clean_buzzwords
from core.logger import logger
from core.llm import llm_pro
from langchain_core.prompts import ChatPromptTemplate

class SlideDraft(BaseModel):
    title: str = Field(description="Slide title")
    purpose: str = Field(description="Purpose of the slide")
    layout_type: str = Field(description="Layout type: title_slide, section_divider, standard_content, card_grid, closing_slide")
    content: List[str] = Field(description="Bullet points for the slide (max 5)")
    has_diagram: bool = Field(description="True if the slide requires a mermaid diagram (process, structure, timeline)")
    has_image: bool = Field(description="True if the slide requires a stock photo")
    image_search_query: Optional[str] = Field(description="Search query if has_image is true", default=None)

class PresentationDraft(BaseModel):
    slides: List[SlideDraft] = Field(description="List of slides in the presentation")

def run_content_agent(deck_state: DeckState) -> DeckState:
    logger.info("Content Agent: Generating slide outline and direct content using LLM...")
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "ROLE: You are the Content Strategy Agent, the foundational intelligence of an AI Presentation Designer pipeline. "
                   "TASK: Generate a strictly structured, highly professional presentation outline based on the user's prompt and notes. "
                   "RULES: "
                   "1. Ensure logical narrative flow from introduction to conclusion. Create a comprehensive deck of AT LEAST 8 to 12 slides depending on the topic. Do not just make 5 slides. "
                   "2. ONE IDEA PER SLIDE. If an idea is complex, split it across multiple slides. Keep text concise: maximum of 5 short lines/bullets per slide. ABSOLUTELY NO walls of text. "
                   "3. You must assign each slide a specific layout_type: "
                   "   - 'title_slide' for the very first slide. "
                   "   - 'section_divider' for transitioning between major topics (use very sparse text). "
                   "   - 'card_grid' for listing multiple items (e.g., top 3 benefits, step 1/2/3). "
                   "   - 'standard_content' for normal explanatory slides. You will use this layout the most. "
                   "   - 'closing_slide' for the final takeaways or thank you. "
                   "4. Intelligently decide if a slide requires a visual diagram (has_diagram=True) for processes/structures, or a stock photo (has_image=True) for conceptual emotional impact. "
                   "5. Provide detailed, specific image_search_queries if an image is needed."),
        ("user", "Prompt: {prompt}\nNotes: {notes}\nFeedback from previous review: {revisions}\nCreate the structured presentation outline fixing any feedback provided.")
    ])
    
    chain = prompt_template | llm_pro.with_structured_output(PresentationDraft)
    
    try:
        rev_str = "\\n".join(deck_state.revision_notes) if deck_state.revision_notes else "None"
        draft = chain.invoke({"prompt": deck_state.user_prompt, "notes": deck_state.background_material or "", "revisions": rev_str})
        
        slides = []
        for i, s in enumerate(draft.slides, 1):
            is_non_media_layout = s.layout_type in ["section_divider", "title_slide", "closing_slide", "card_grid"]
            slide_state = SlideState(
                slide_number=i,
                layout_type=s.layout_type,
                title=s.title,
                purpose=s.purpose,
                has_diagram=False if is_non_media_layout else s.has_diagram,
                has_image=False if is_non_media_layout else s.has_image,
                image_search_query=None if is_non_media_layout else s.image_search_query,
                raw_content=s.content,
                notes="LLM generated"
            )
            
            slides.append(slide_state)
            
        deck_state.slides = slides
        logger.info(f"Content Agent generated {len(slides)} slides.")
        
    except Exception as e:
        logger.error(f"Content Agent failed: {e}")
        
    deck_state.current_step = "CONTENT_DRAFT"
    return deck_state
