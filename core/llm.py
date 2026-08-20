import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI

load_dotenv()

# Initialize the Gemini Models with automatic Mistral fallback
_mistral_pro = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.2,
    max_retries=2,
)

_mistral_flash = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
)

_gemini_pro = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.2,
    max_tokens=8192,
    timeout=None,
    max_retries=2,
)

_gemini_flash = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)

# Export resilient models that automatically fallback to Mistral on Gemini 429
llm_pro = _gemini_pro.with_fallbacks([_mistral_pro])
llm_flash = _gemini_flash.with_fallbacks([_mistral_flash])
llm_light = _mistral_pro
