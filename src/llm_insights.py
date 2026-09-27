import os
import time
from typing import Any, Dict
import uuid

from google.genai.errors import ServerError
from src.clients.llm import GeminiClient
from src.utils.prompt import build_risk_prompt
from src.validations.schemas.llm_insights import DeliveryInsightContract
from src.loaders.delivery_risk_insights import DeliveryRiskInsightLoader


class DeliveryInsightGenerator:

  def __init__(
      self,
      primary_model: str = "gemini-3.8-flash",
      fallback_model: str = "gemini-3-flash",
  ):
    self.primary_model = primary_model
    self.fallback_model = fallback_model
    self.client_wrapper = GeminiClient(model_name=primary_model)

  def _generate_with_retry(
      self, prompt: str, config: Any, max_retries: int = 3
  ):
    """Executes call with exponential backoff and automatic model fallback."""
    models_to_try = [self.primary_model, self.fallback_model]

    for model in models_to_try:
      for attempt in range(1, max_retries + 1):
        try:
          start_time = time.perf_counter()
          response = self.client_wrapper.client.models.generate_content(
              model=model,
              contents=prompt,
              config=config,
          )
          duration_ms = int((time.perf_counter() - start_time) * 1000)
          return response, model, duration_ms

        except ServerError as e:
          # If high demand (503), pause and retry with exponential backoff
          if attempt < max_retries:
            backoff_sec = 2**attempt
            print(
                f"[Gemini 503] High demand on {model}. Retrying in"
                f" {backoff_sec}s (attempt {attempt}/{max_retries})..."
            )
            time.sleep(backoff_sec)
          else:
            print(f"[Gemini Error] Exhausted retries for {model}.")

    raise RuntimeError(
        "Failed to generate insights: all model endpoints unavailable."
    )

  def generate_and_save_insight(
      self,
      risk_record_id: uuid.UUID | str,
      telemetry_payload: Dict[str, Any],
  ) -> uuid.UUID:
    prompt = build_risk_prompt(telemetry_payload)
    config = self.client_wrapper.get_model_config()

    # Call with backoff & fallback
    response, used_model, execution_duration_ms = self._generate_with_retry(
        prompt, config
    )

    # Validate output contract
    insight_validated = DeliveryInsightContract.model_validate_json(
        response.text
    )

    # Observability
    usage = response.usage_metadata
    prompt_tokens = usage.prompt_token_count if usage else 0
    completion_tokens = usage.candidates_token_count if usage else 0
    total_tokens = usage.total_token_count if usage else 0

    model_metadata = {
        "model_name": used_model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "execution_duration_ms": execution_duration_ms,
    }

    # Persist to database
    return DeliveryRiskInsightLoader.insert_insight(
        risk_record_id=risk_record_id,
        insight_payload=insight_validated.model_dump(),
        model_meta=model_metadata,
    )