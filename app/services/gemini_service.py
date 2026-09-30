import json
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import httpx

from app.config import settings

logger = logging.getLogger("pocketsmart.gemini")

class GeminiService:
    """Dedicated service layer for communicating with Google Gemini API."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-1.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def is_configured(self) -> bool:
        """Check if a Gemini API key is configured."""
        return bool(self.api_key and len(self.api_key) > 5)

    def _clean_json_response(self, text: str) -> str:
        """Clean markdown code block wrappers (```json ... ```) from response."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    async def generate_text_plan(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Send prompt to Gemini and parse structured JSON response."""
        if not self.is_configured():
            logger.info("Gemini API key not configured. Using fallback engine.")
            return None

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        contents = [{"parts": [{"text": prompt}]}]
        body: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        if system_instruction:
            body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        headers = {"Content-Type": "application/json"}

        # Attempt with 1 retry for transient network errors
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    response = await client.post(url, json=body, headers=headers)
                    if response.status_code == 200:
                        res_json = response.json()
                        candidates = res_json.get("candidates", [])
                        if not candidates:
                            logger.warning("Gemini returned no candidates.")
                            return None

                        content_parts = candidates[0].get("content", {}).get("parts", [])
                        if not content_parts:
                            return None

                        raw_text = content_parts[0].get("text", "")
                        cleaned_text = self._clean_json_response(raw_text)
                        parsed = json.loads(cleaned_text)
                        return parsed
                    else:
                        logger.error(f"Gemini API returned HTTP {response.status_code}: {response.text}")
                        if attempt == 0:
                            continue
                        return None
            except Exception as e:
                logger.error(f"Error calling Gemini API (attempt {attempt + 1}): {str(e)}")
                if attempt == 0:
                    continue
                return None

        return None

    async def generate_multimodal_plan(
        self, 
        prompt: str, 
        image_path: Path, 
        mime_type: str = "image/jpeg",
        system_instruction: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Send multimodal request (outfit image + text prompt) to Gemini."""
        if not self.is_configured():
            logger.info("Gemini API key not configured. Multimodal will use smart visual fallback.")
            return None

        if not image_path.exists():
            logger.warning(f"Image path not found: {image_path}. Calling text plan instead.")
            return await self.generate_text_plan(prompt, system_instruction)

        try:
            with open(image_path, "rb") as img_file:
                image_bytes = img_file.read()
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

            parts = [
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": image_b64
                    }
                },
                {"text": prompt}
            ]

            body: Dict[str, Any] = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            if system_instruction:
                body["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            headers = {"Content-Type": "application/json"}

            async with httpx.AsyncClient(timeout=50.0) as client:
                response = await client.post(url, json=body, headers=headers)
                if response.status_code == 200:
                    res_json = response.json()
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                        cleaned_text = self._clean_json_response(raw_text)
                        return json.loads(cleaned_text)
                else:
                    logger.error(f"Gemini Multimodal returned HTTP {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error calling Gemini Multimodal: {str(e)}")
            return None

gemini_service = GeminiService()
