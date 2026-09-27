import os
from google import genai
from google.genai import types
from src.utils.prompt import SYSTEM_INSTRUCTION
from src.validations.schemas.llm_insights import DeliveryInsightContract


class GeminiClient:

  def __init__(self, model_name: str = "gemini-3.8-flash"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
      raise ValueError("GEMINI_API_KEY environment variable is not configured.")

    self.client = genai.Client(api_key=api_key)
    self.model_name = model_name

  def get_model_config(self) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,  # Low temperature for deterministic, operational decisions
        response_mime_type="application/json",
        response_schema=DeliveryInsightContract,
    )