import json
import textwrap
from typing import Any, Dict

# Strict persona and grounding instructions to prevent hallucination
SYSTEM_INSTRUCTION = textwrap.dedent("""
    You are an automated logistics risk intelligence engine for last-mile delivery operations.
    Your mission is to evaluate real-time telemetry (weather, traffic, AQI, and holiday context) and generate actionable dispatch advisories.

    RULES TO PREVENT HALLUCINATIONS:
    1. Grounding: Base all assessments purely on the provided metrics. Never assume or invent conditions not explicitly present in the data.
    2. Zero Speculation: If metrics are within nominal operational ranges, explicitly classify urgency as LOW.
    3. Strict Logic:
       - CRITICAL: Road closures (is_road_closed=true), traffic delay_pct >= 50%, AQI >= 201, wind_gust_mps >= 20, or heavy rain.
       - MODERATE: Traffic delay_pct between 20% and 49%, AQI between 101 and 200, wind_gust_mps between 10 and 19, or is_holiday=true.
       - LOW: Normal traffic flow (delay_pct < 20%), normal AQI (<= 100), mild weather, open roads.
    4. Recommendations: Actionable fleet instructions (e.g., extend delivery SLA, switch to vans, equip couriers with masks).
    5. Output: Provide valid structured data meeting the schema without markdown wrappers or conversational filler.
""").strip()

_PROMPT_TEMPLATE = textwrap.dedent("""
    Evaluate the following real-time delivery telemetry record and generate an operational advisory:

    === TELEMETRY RECORD ===
    __TELEMETRY_JSON__
    ========================

    ANALYSIS REQUIREMENTS:
    - Determine urgency_level strictly by the defined thresholds (LOW, MODERATE, CRITICAL).
    - Provide a concise headline summarizing the core operational impact (under 15 words).
    - Provide dispatch_recommendation with concrete routing, vehicle assignment, or courier safety steps.
    - Provide customer_advisory with a clear, polite customer update explaining delivery status without exposing internal telemetry numbers.
""").strip()


def build_risk_prompt(telemetry_data: Dict[str, Any]) -> str:
  """Safely formats telemetry data into the prompt without triggering Python f-string brace syntax errors."""
  # Convert telemetry dictionary to clean JSON string
  clean_json = json.dumps(telemetry_data, indent=2, default=str)

  # Safe substitution using exact string replacement
  return _PROMPT_TEMPLATE.replace("__TELEMETRY_JSON__", clean_json)