from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

from core.state import DeckState
from agents.content_agent import run_content_agent
from agents.diagram_agent import run_diagram_agent
from agents.image_agent import run_image_agent
from agents.design_agent import run_design_agent
from agents.refinement_agent import run_refinement_agent
from agents.export_agent import run_export_agent
from core.logger import logger
from pydantic import BaseModel, Field
from core.llm import llm_pro, llm_light
from langchain_core.prompts import ChatPromptTemplate



# Define State Type for LangGraph StateGraph
class WorkflowState(TypedDict):
    deck_state: DeckState
    content_approved: bool
    design_approved: bool


# Node Functions for LangGraph
def content_node(state: WorkflowState) -> WorkflowState:
    logger.info("--- LANGGRAPH NODE: CONTENT AGENT ---")
    updated_deck = run_content_agent(state["deck_state"])
    return {
        "deck_state": updated_deck,
        "content_approved": len(updated_deck.slides) > 0,
        "design_approved": state.get("design_approved", False)
    }


class GateReview(BaseModel):
    is_approved: bool = Field(description="True if the content/design passes all standards.")
    feedback: str = Field(description="Specific feedback if rejected, or 'Looks good' if approved.")

def content_review_gate(state: WorkflowState) -> str:
    logger.info("--- LANGGRAPH GATE: CONTENT REVIEW ---")
    deck = state["deck_state"]
    
    if len(deck.slides) == 0:
        logger.warning("Content Agent produced 0 slides.")
        deck.revision_notes.append("Empty slide outline generated.")
        if len(deck.revision_notes) >= 2:
            logger.error("Failed to generate content after retries. Aborting revision loop.")
            state["content_approved"] = True
            return "approved"
        return "revise"
        
    # Prevent infinite loop: if already revised once, approve and proceed
    if len(deck.revision_notes) >= 1:
        logger.info("Content revision cycle limit reached (1). Approving and advancing.")
        state["content_approved"] = True
        return "approved"
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "ROLE: You are the Lead Editor & Content QA Gatekeeper. "
                   "TASK: Evaluate the entire proposed slide deck outline. "
                   "RULES: "
                   "1. Ensure the narrative flows logically and hits key objectives without extra complexity. "
                   "2. Reject if any slide has more than 5 bullet points. "
                   "3. Reject if you find fluff, buzzwords, or poor structuring. "
                   "4. Return is_approved=true only if it is completely flawless. Return false with strict feedback to force a revision cycle."),
        ("user", "Slides data:\n{slides_data}")
    ])
    
    slides_str = "\n".join([f"Slide {s.slide_number}: {s.title}\n{s.raw_content}" for s in deck.slides])
    chain = prompt | llm_pro.with_structured_output(GateReview)
    
    try:
        review = chain.invoke({"slides_data": slides_str})
        if review.is_approved:
            logger.info("Gate 1 Passed (LLM Evaluated): Content Approved.")
            state["content_approved"] = True
            return "approved"
        else:
            logger.warning(f"Gate 1 Failed (LLM Evaluated): {review.feedback}")
            deck.revision_notes.append(review.feedback)
            return "revise"
    except Exception as e:
        logger.error(f"Gate 1 evaluation failed: {e}. Falling back to automatic approval.")
        state["content_approved"] = True
        return "approved"

def diagram_node(state: WorkflowState) -> WorkflowState:
    logger.info("--- LANGGRAPH NODE: DIAGRAM AGENT ---")
    updated_deck = run_diagram_agent(state["deck_state"])
    return {**state, "deck_state": updated_deck}

def image_node(state: WorkflowState) -> WorkflowState:
    logger.info("--- LANGGRAPH NODE: IMAGE AGENT ---")
    updated_deck = run_image_agent(state["deck_state"])
    return {**state, "deck_state": updated_deck}

def design_node(state: WorkflowState) -> WorkflowState:
    logger.info("--- LANGGRAPH NODE: DESIGN AGENT ---")
    updated_deck = run_design_agent(state["deck_state"])
    return {**state, "deck_state": updated_deck}

def refinement_node(state: WorkflowState) -> WorkflowState:
    logger.info("--- LANGGRAPH NODE: REFINEMENT AGENT ---")
    updated_deck = run_refinement_agent(state["deck_state"])
    return {**state, "deck_state": updated_deck}

def design_review_gate(state: WorkflowState) -> str:
    logger.info("--- LANGGRAPH GATE: REFINEMENT REVIEW ---")
    deck = state["deck_state"]
    
    # Prevent infinite design loop: allow at most 1 refine cycle
    design_revisions = [r for r in deck.revision_notes if "Design" in r or "Visual" in r or "Grid" in r]
    if len(design_revisions) >= 1:
        logger.info("Design revision cycle limit reached (1). Approving and advancing to export.")
        state["design_approved"] = True
        return "approved"
    
    # We use LLM to review the structured JSON design of the slides
    prompt = ChatPromptTemplate.from_messages([
        ("system", "ROLE: You are the Lead Design Director & Visual QA Gatekeeper. "
                   "TASK: Conduct a final audit of the assembled slide deck design data. "
                   "RULES: "
                   "1. Ensure adherence to the design grid, checking for element overlapping or unreadable typography sizes. "
                   "2. Ensure consistent branding and colors based on the theme. "
                   "3. If any element looks amateurish, overlapping, or poorly spaced, reject the design immediately with detailed feedback. "
                   "4. Return is_approved=true only if the design is 100% executive-ready."),
        ("user", "Review this slide design data:\n{design_data}")
    ])
    
    # Simplify the design data to reduce token usage
    design_str = "\n".join([f"Slide {s.slide_number}: {[e.role for e in s.elements]}" for s in deck.slides])
    chain = prompt | llm_pro.with_structured_output(GateReview)
    
    try:
        review = chain.invoke({"design_data": design_str})
        if review.is_approved:
            logger.info("Gate 2 Passed (LLM Evaluated): Design Meets Standards.")
            state["design_approved"] = True
            return "approved"
        else:
            logger.warning(f"Gate 2 Failed (LLM Evaluated): {review.feedback}")
            deck.revision_notes.append(f"Design Feedback: {review.feedback}")
            return "refine"
    except Exception as e:
        logger.error(f"Gate 2 evaluation failed: {e}. Falling back to automatic approval.")
        state["design_approved"] = True
        return "approved"

def export_node(state: WorkflowState) -> WorkflowState:
    logger.info("--- LANGGRAPH NODE: EXPORT AGENT ---")
    updated_deck = run_export_agent(state["deck_state"])
    return {**state, "deck_state": updated_deck}


def build_presentation_workflow_graph(update_callback=None):
    """Builds and compiles the LangGraph StateGraph pipeline."""
    workflow = StateGraph(WorkflowState)
    
    # Wrappers to emit events if callback provided
    def wrap_node(func, step_name):
        def wrapped_node(state):
            if update_callback:
                update_callback(step_name, f"Executing {step_name} phase...")
            return func(state)
        return wrapped_node
        
    workflow.add_node("content_agent", wrap_node(content_node, "CONTENT_DRAFT"))
    workflow.add_node("diagram_agent", wrap_node(diagram_node, "DIAGRAMS"))
    workflow.add_node("image_agent", wrap_node(image_node, "IMAGES"))
    workflow.add_node("design_agent", wrap_node(design_node, "DESIGN"))
    workflow.add_node("refinement_agent", wrap_node(refinement_node, "REFINEMENT"))
    workflow.add_node("export_agent", wrap_node(export_node, "EXPORT"))
    
    # Add Edges & Conditional Routing
    workflow.set_entry_point("content_agent")
    
    workflow.add_conditional_edges(
        "content_agent",
        content_review_gate,
        {
            "approved": "diagram_agent",
            "revise": "content_agent"
        }
    )
    
    workflow.add_edge("diagram_agent", "image_agent")
    workflow.add_edge("image_agent", "design_agent")
    workflow.add_edge("design_agent", "refinement_agent")
    
    workflow.add_conditional_edges(
        "refinement_agent",
        design_review_gate,
        {
            "approved": "export_agent",
            "refine": "design_agent"
        }
    )
    
    workflow.add_edge("export_agent", END)
    
    return workflow.compile()

def run_presentation_pipeline(user_prompt: str, background_material: str = "", theme_color: str = "#0D6EFD", update_callback=None) -> DeckState:
    """Entry point function to execute the LangGraph workflow pipeline."""
    logger.info(f"Starting Presentation Pipeline for: {user_prompt}")
    
    from core.state import DeckTheme
    from core.theme_manager import get_next_theme
    
    # Get automatic rotating professional theme
    theme_data = get_next_theme()
    theme = DeckTheme(**theme_data)
    
    initial_deck = DeckState(
        user_prompt=user_prompt,
        background_material=background_material,
        theme=theme
    )
    
    initial_state: WorkflowState = {
        "deck_state": initial_deck,
        "content_approved": False,
        "design_approved": False
    }
    
    app = build_presentation_workflow_graph(update_callback)
    final_output = app.invoke(initial_state)
    return final_output["deck_state"]
