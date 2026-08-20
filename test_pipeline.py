import os
from core.orchestrator import run_presentation_pipeline
from core.logger import logger

def run_samples():
    prompts = [
        "AI Agents in Healthcare: Diagnostics, Workflow Automation, and Patient Outcomes",
        "Fintech Payment Infrastructure: Real-time Settlements and Security Architecture",
        "Sustainable Smart Grids: Energy Transition and Renewable Integration Strategies"
    ]
    
    for i, prompt in enumerate(prompts, start=1):
        logger.info(f"\n=======================================================")
        logger.info(f" RUNNING SAMPLE {i}/3: {prompt}")
        logger.info(f"=======================================================")
        
        deck_state = run_presentation_pipeline(user_prompt=prompt)
        logger.info(f"Sample {i} completed -> {deck_state.pptx_output_path}")

if __name__ == "__main__":
    run_samples()
