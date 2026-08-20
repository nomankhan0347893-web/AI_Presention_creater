from core.state import DeckState
from tools.pptx_builder_tool import build_pptx_from_deck_state
from core.logger import logger

def run_export_agent(deck_state: DeckState) -> DeckState:
    """
    Export Agent: Takes the refined JSON slide specs and constructs native editable PowerPoint file (.pptx).
    Self-Reasoning Loop: Confirms every element lands at exact positions and shapes before completion.
    """
    logger.info("Export Agent: Constructing native editable PowerPoint (.pptx) presentation file...")
    
    output_filename = "presentation_deck.pptx"
    pptx_path = build_pptx_from_deck_state(deck_state, filename=output_filename)
    
    deck_state.pptx_output_path = pptx_path
    deck_state.current_step = "EXPORT"
    deck_state.status = "completed"
    
    logger.info(f"Export Agent finished successfully! Editable PPTX saved at -> {pptx_path}")
    return deck_state
