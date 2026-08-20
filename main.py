import sys
import argparse
from core.orchestrator import run_presentation_pipeline
from core.logger import logger

def main():
    parser = argparse.ArgumentParser(description="AI Presentation Designer Agent (Phase 4)")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Build an executive overview presentation on AI Agents in Healthcare, focusing on diagnostics, workflow automation, and patient care outcomes.",
        help="User prompt describing the desired presentation."
    )
    args = parser.parse_args()
    
    logger.info("=================================================================")
    logger.info("  STARTING AI PRESENTATION DESIGNER AGENT (LANGGRAPH WORKFLOW)   ")
    logger.info("=================================================================")
    logger.info(f"PROMPT: {args.prompt}")
    
    deck_state = run_presentation_pipeline(user_prompt=args.prompt)
    
    logger.info("=================================================================")
    logger.info(f"  PRESENTATION COMPLETE! Output: {deck_state.pptx_output_path}")
    logger.info("=================================================================")

if __name__ == "__main__":
    main()
