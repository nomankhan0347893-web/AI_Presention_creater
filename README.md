# AI Presentation Creator

An advanced agentic AI pipeline that dynamically generates visually stunning, native PowerPoint (.pptx) presentations based on user prompts.

## How It Works

The system utilizes a multi-agent orchestration pipeline to break down the presentation creation process into specialized roles, mirroring a real-world design agency:

1. **Planning Agent:** Analyzes the user's prompt and generates a structured storyboard (slide count, themes, titles).
2. **Content Agent:** Fleshes out the narrative for each slide, adhering to strict constraints like "One Idea Per Slide".
3. **Design Agent:** Maps the content to precise geometric layouts (`title_slide`, `standard_content`, `card_grid`, etc.). It generates an HTML/CSS preview alongside a deeply structured JSON array of elements with exact coordinate placement (e.g., `top: 28%`).
4. **Refinement Agent:** Uses headless browser automation (Playwright) to screenshot the HTML layouts and iteratively critiques/adjusts the design for aesthetic perfection.
5. **PPTX Builder:** Translates the finalized JSON layout constraints into native, fully editable `python-pptx` shape objects.

## Tech Stack & Tools

- **Backend:** Python, FastAPI, LangChain
- **Frontend:** React, Vite, Tailwind CSS
- **LLMs:** Google Gemini (Primary), Mistral Large (Fallback)
- **Browser Automation:** Playwright (for fast batch rendering of slide previews)
- **Document Generation:** `python-pptx`

## Challenges & Solutions

During development, several complex bugs were encountered and resolved to create a stable, production-ready pipeline:

### 1. LLM Rate Limiting (Gemini 429 Quota Errors)
- **Error:** The pipeline generated 0 slides and looped infinitely because `gemini-3.6-flash` hit a `RESOURCE_EXHAUSTED` limit during the multi-agent handoffs.
- **Fix:** Implemented a robust fallback mechanism using LangChain's `.with_fallbacks()` to seamlessly switch to `Mistral-Large` when Gemini quotas are exceeded. Also downgraded the default model to `gemini-3.5-flash` which has a much higher free-tier limit, and added a strict 1-revision guardrail in the orchestrator to prevent infinite looping.

### 2. Massive Performance Bottleneck in Refinement Agent
- **Error:** The Refinement Agent took 5-6 minutes to evaluate slides because it was spinning up a new Playwright browser instance for every single slide screenshot.
- **Fix:** Rewrote `browser_tool.py` to use a batch renderer (`render_all_slides_to_png`). The system now launches Playwright *once*, processes all slides concurrently, and completes the entire visual pass in ~2 seconds.

### 3. Native PPTX Text Overlapping
- **Error:** Subtitles collided with Presenter Names, and Slide Titles wrapped into Body text when exported to native PPTX.
- **Fix:** Python-PPTX disables auto-scaling when font sizes are explicitly set per run. To solve the collision, the Design Agent's prompt was heavily constrained to:
  1. Mathematically shift standard body text down (from `24%` to `28%` top spacing).
  2. Group conflicting elements (like Subtitles and Presenter Names) into a *single* text frame so PowerPoint natively handles the paragraph stacking.

### 4. Missing Background Cards in PPTX Export
- **Error:** The HTML preview showed beautiful rounded background cards, but the PPTX export rendered them as invisible floating text.
- **Fix:** The LLM was correctly applying `background-color` in CSS but omitting it from the structured JSON metadata. Added a strict pipeline rule forcing the Design Agent to populate the `style.background_color` property inside the JSON payload for `card_grid` elements so the `pptx_builder_tool.py` knows to draw the `MSO_SHAPE.ROUNDED_RECTANGLE`.
