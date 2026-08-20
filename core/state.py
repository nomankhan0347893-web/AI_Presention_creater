from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class ElementPosition(BaseModel):
    left: str  # e.g. "5%" or "0.8in"
    top: str   # e.g. "10%" or "1.2in"
    width: str # e.g. "40%" or "5.0in"
    height: str# e.g. "60%" or "4.5in"


class ElementStyle(BaseModel):
    font_size: Optional[str] = "16pt"
    font_weight: Optional[str] = "normal"
    color: Optional[str] = "#212529"
    font_family: Optional[str] = "Open Sans"
    alignment: Optional[str] = "left"
    background_color: Optional[str] = None
    border_radius: Optional[str] = None


class SlideElement(BaseModel):
    id: str
    type: str  # "text" | "image" | "diagram"
    role: str  # "slide_title" | "subtitle" | "body_text" | "bullet_list" | "diagram" | "image"
    content: Optional[Union[str, List[str]]] = None
    file_path: Optional[str] = None
    position: ElementPosition
    style: Optional[ElementStyle] = Field(default_factory=ElementStyle)


class SlideState(BaseModel):
    slide_number: int
    layout_type: str  # e.g., "title_and_content", "split_2_column", "diagram_focus", "image_card"
    title: str
    purpose: str
    raw_content: List[str] = Field(default_factory=list)
    elements: List[SlideElement] = Field(default_factory=list)
    has_diagram: bool = False
    diagram_mermaid_code: Optional[str] = None
    has_image: bool = False
    image_search_query: Optional[str] = None
    html_layout: Optional[str] = None
    css_styles: Optional[str] = None
    notes: Optional[str] = None


class DeckTheme(BaseModel):
    id: str = "custom"
    background_color: str = "#0F292B"
    text_color: str = "#FFFFFF"
    primary_color: str = "#38B2AC"
    accent_color: str = "#81E6D9"
    secondary_bg_color: str = "#1A3638"
    font_title: str = "Georgia"
    font_body: str = "Arial"
    aspect_ratio: str = "16:9"
    footer_text: Optional[str] = None


class DeckState(BaseModel):
    user_prompt: str
    background_material: Optional[str] = None
    theme: DeckTheme = Field(default_factory=DeckTheme)
    slides: List[SlideState] = Field(default_factory=list)
    current_step: str = "INTAKE"  # INTAKE, CONTENT_DRAFT, DIAGRAMS, IMAGES, DESIGN, REFINEMENT, EXPORT, COMPLETE
    revision_notes: List[str] = Field(default_factory=list)
    status: str = "in_progress"
    pptx_output_path: Optional[str] = None
