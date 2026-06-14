from groq import Groq
import json
import re
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings

logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)
TEXT_MODEL = "llama-3.3-70b-versatile"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq(prompt: str, system: str = None, temperature: float = 0.1) -> dict:
    """
    Call Groq with llama-3.3-70b-versatile. Returns parsed JSON dict.
    Low temperature (0.1) for deterministic policy/decision outputs.
    """
    start = time.time()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=2000,
        timeout=30.0,
    )

    latency_ms = (time.time() - start) * 1000
    raw_text = response.choices[0].message.content
    usage = response.usage

    parsed = _parse_json_response(raw_text)
    parsed["_meta"] = {
        "model": TEXT_MODEL,
        "latency_ms": latency_ms,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
    }
    return parsed


def _parse_json_response(text: str) -> dict:
    cleaned = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from Groq response: {cleaned[:200]}")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq_vision(image_base64: str, media_type: str, prompt: str) -> dict:
    """
    Call Groq with llama-3.2-11b-vision-preview. Returns parsed JSON dict.
    Fallback for when Gemini Vision is rate-limited or unavailable.
    """
    start = time.time()
    data_url = f"data:{media_type};base64,{image_base64}"
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt + "\n\nCRITICAL: Respond with ONLY a valid JSON object. No markdown code blocks, just pure JSON."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                }
            ]
        }
    ]

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=0.1,
        max_tokens=1000,
        timeout=30.0,
    )

    latency_ms = (time.time() - start) * 1000
    raw_text = response.choices[0].message.content
    usage = response.usage

    parsed = _parse_json_response(raw_text)
    parsed["_meta"] = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "latency_ms": latency_ms,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
    }
    return parsed

