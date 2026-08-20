from core.state import DeckState
from tools.stock_photo_tool import search_and_download_stock_image
from core.logger import logger
from core.llm import llm_light
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class ImageQuery(BaseModel):
    optimized_query: str = Field(description="The highly optimized search query for stock photo APIs.")

def run_image_agent(deck_state: DeckState) -> DeckState:
    """
    Image Agent: Sources and selects high quality stock photos.
    Self-Reasoning Loop: Uses an LLM to generate the absolute best visual search query.
    """
    logger.info("Image Agent: Sourcing stock photo assets...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "ROLE: You are the Visual Asset Image Agent. "
                   "TASK: Optimize search queries for fetching high-quality stock photos (like Unsplash/Pexels). "
                   "RULES: "
                   "1. Review the slide title, content, and the initial concept query. "
                   "2. Transform abstract or complex concepts into concrete, highly visual, and highly searchable keywords (max 3-4 words). "
                   "3. Avoid text overlays or generic clip-art queries. Focus on professional photography keywords (e.g. 'modern corporate office', 'team collaboration', 'abstract blue technology')."),
        ("user", "Slide Title: {title}\nSlide Content: {content}\nInitial Concept: {concept}\nOutput the optimized stock photo search query.")
    ])
    
    chain = prompt | llm_light.with_structured_output(ImageQuery)
    
    for slide in deck_state.slides:
        if slide.has_image and slide.image_search_query:
            logger.info(f"Image Agent: Optimizing query for Slide {slide.slide_number}...")
            
            try:
                content_str = "\\n".join(slide.raw_content)
                result = chain.invoke({
                    "title": slide.title,
                    "content": content_str,
                    "concept": slide.image_search_query
                })
                
                final_query = result.optimized_query
                logger.info(f"Image Agent: Optimized query to -> '{final_query}'. Downloading...")
                
                img_path = search_and_download_stock_image(final_query, slide.slide_number)
                slide.notes = (slide.notes or "") + f" | Image JPG: {img_path}"
                
            except Exception as e:
                logger.error(f"Image Agent query optimization failed: {e}. Falling back to original.")
                img_path = search_and_download_stock_image(slide.image_search_query, slide.slide_number)
                slide.notes = (slide.notes or "") + f" | Image JPG: {img_path}"
            
    deck_state.current_step = "IMAGES"
    return deck_state
