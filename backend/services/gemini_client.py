import google.generativeai as genai
import base64
import json
import re
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
vision_model = genai.GenerativeModel("gemini-2.0-flash-lite")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=15),
    retry=retry_if_exception_type(Exception)
)
def call_gemini_vision(image_base64: str, media_type: str, prompt: str) -> dict:
    """
    Send an image + prompt to Gemini. Returns parsed JSON dict.
    Handles: base64 decode, retry on 429, JSON extraction from response.
    Always instructs model to return ONLY valid JSON — no preamble.
    """
    start = time.time()
    image_data = base64.b64decode(image_base64)

    full_prompt = (
        f"{prompt}\n\n"
        "CRITICAL: Respond with ONLY a valid JSON object. "
        "No markdown, no code fences, no explanation. Pure JSON only."
    )

    response = vision_model.generate_content([
        {"mime_type": media_type, "data": image_data},
        full_prompt
    ])

    latency_ms = (time.time() - start) * 1000
    raw_text = response.text

    parsed = _parse_json_response(raw_text)
    parsed["_meta"] = {
        "model": "gemini-2.0-flash-lite",
        "latency_ms": latency_ms,
    }
    return parsed


def call_gemini_text(prompt: str) -> dict:
    """Text-only Gemini call for lightweight classification tasks."""
    start = time.time()
    full_prompt = (
        f"{prompt}\n\n"
        "CRITICAL: Respond with ONLY a valid JSON object. No markdown. Pure JSON only."
    )
    response = vision_model.generate_content(full_prompt)
    latency_ms = (time.time() - start) * 1000
    parsed = _parse_json_response(response.text)
    parsed["_meta"] = {"model": "gemini-2.0-flash-lite", "latency_ms": latency_ms}
    return parsed


def _parse_json_response(text: str) -> dict:
    cleaned = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Attempt to extract JSON object from surrounding text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from Gemini response: {cleaned[:200]}")
