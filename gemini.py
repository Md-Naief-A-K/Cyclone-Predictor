import json
from google import genai
from google.genai import types

def ask_gemini(api_key, model_id, context, language, image_bytes=None, mime_type="image/png"):
    """
    Calls Gemini API using official google-genai SDK.
    Handles fallbacks gracefully.
    """
    clean_key = api_key.strip() if api_key else ""
    if not clean_key:
        raise ValueError("API key is missing! Please enter your Gemini API key in the sidebar.")

    # Model ID fallback
    model = "gemini-2.5-flash"

    client = genai.Client(api_key=clean_key)

    prompt = f"""You are a top-tier disaster response specialist. Analyze the cyclone telemetry provided below and output a strict JSON emergency response plan.

Required Local Language for Advisory Dispatch: {language}

Output MUST strictly follow this JSON schema (do NOT wrap in markdown or extra text):
{{
  "severity": "CRITICAL",
  "headline": "<Executive situational summary for controllers>",
  "evacuation": [
    {{"zone": "Zone A (Coastal)", "action": "Mandatory evacuation", "timing": "0-6 Hours"}}
  ],
  "insurance": {{
    "trigger": "Surge height > 2.0m threshold breached",
    "rationale": "Parametric payout activated for rapid municipal liquidity."
  }},
  "hardening": [
    {{"priority": "P0", "asset": "Substation Alpha", "action": "Deploy sandbag barriers and power shutoff"}}
  ],
  "advisory_en": "<Official English emergency broadcast message>",
  "advisory_local": "<Official emergency broadcast translated into {language}>"
}}

CYCLONE TELEMETRY CONTEXT:
{json.dumps(context, indent=2)}
"""

    contents = [prompt]
    if image_bytes:
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    if not response.text:
        raise RuntimeError("Received empty response from Gemini API.")

    return json.loads(response.text)