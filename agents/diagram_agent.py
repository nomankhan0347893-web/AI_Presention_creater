from core.state import DeckState
from tools.mermaid_tool import render_mermaid_to_png
from core.logger import logger
from core.llm import llm_pro
from langchain_core.prompts import ChatPromptTemplate

def run_diagram_agent(deck_state: DeckState) -> DeckState:
    """
    Diagram Agent: Selects suitable slides and compiles Mermaid code to PNG.
    Uses LLM to generate the Mermaid code based on slide content.
    """
    logger.info("Diagram Agent: Evaluating slides for visual diagrams and generating code...")
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "ROLE: You are the Data Visualization & Diagram Agent. "
                   "TASK: Convert slide text into highly legible, professional Mermaid.js code. "
                   "RULES: "
                   "1. Read the slide title and content to determine the best visual layout (e.g., flowchart TD, graph LR, sequence diagram). "
                   "2. Create nodes that summarize the core concepts logically. Do not make the diagram overly complex or cluttered. "
                   "3. Output ONLY valid, compilable Mermaid.js syntax. "
                   "4. DO NOT wrap the code in markdown blocks like ```mermaid. ONLY output the raw code. "
                   "5. CRITICAL: You MUST inject the provided theme colors into the diagram using the %%{{init}}%% directive at the very top of the code so the diagram matches the presentation. "
                   "   Example: %%{{init: {{'theme': 'base', 'themeVariables': {{ 'primaryColor': '{primary}', 'primaryTextColor': '{text_color}', 'lineColor': '{accent}'}}}}}}%% "
                   "Your diagrams will be rendered to PNGs for executive-level presentations, so ensure they are clear, clean, and structurally perfect."),
        ("user", "Title: {title}\nContent:\n{content}\nTheme Colors: Primary={primary}, Text={text_color}, Accent={accent}\nGenerate Mermaid code.")
    ])
    
    chain = prompt_template | llm_pro
    
    import time
    for slide in deck_state.slides:
        if slide.has_diagram:
            time.sleep(3)
            logger.info(f"Diagram Agent: Generating Mermaid code for Slide {slide.slide_number}...")
            content_str = "\\n".join(slide.raw_content)
            try:
                theme = deck_state.theme
                result = chain.invoke({
                    "title": slide.title, 
                    "content": content_str,
                    "primary": theme.primary_color,
                    "text_color": theme.text_color,
                    "accent": getattr(theme, 'accent_color', '#000000')
                })
                
                content_val = result.content
                if isinstance(content_val, list):
                    content_val = content_val[0]
                    if isinstance(content_val, dict) and "text" in content_val:
                        content_val = content_val["text"]
                content_val = str(content_val)
                    
                mermaid_code = content_val.strip()
                # Clean markdown blocks if present
                if mermaid_code.startswith("```mermaid"):
                    mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
                elif mermaid_code.startswith("```"):
                    mermaid_code = mermaid_code.replace("```", "").strip()
                    
                slide.diagram_mermaid_code = mermaid_code
                
                logger.info(f"Diagram Agent: Compiling Mermaid diagram for Slide {slide.slide_number}...")
                png_path = render_mermaid_to_png(slide.diagram_mermaid_code, slide.slide_number)
                slide.notes = (slide.notes or "") + f" | Diagram PNG: {png_path}"
            except Exception as e:
                logger.error(f"Diagram Agent failed for Slide {slide.slide_number}: {e}")
                slide.has_diagram = False # Fallback to text only if diagram generation fails
            
    deck_state.current_step = "DIAGRAMS"
    return deck_state
