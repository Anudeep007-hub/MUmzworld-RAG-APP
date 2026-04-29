import os, json, re
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import base64, io
from .schemas import ProductAttributes

load_dotenv()

# vision.py
# vision.py — guaranteed to work, OpenRouter picks for you
VISION_MODEL = "openrouter/auto"

# generator.py
EN_MODEL = "openrouter/auto"
AR_MODEL = "openrouter/auto"
def _get_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
    )

def _image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

SYSTEM = """You are a product analyst for a baby/mother e-commerce store.
Given an image, extract product attributes as JSON only.
If this is NOT a baby/mother/child related product, set is_baby_product to false.
Be conservative with confidence. Return null for fields you cannot determine.

Return ONLY valid JSON:
{
  "product_type": string or null,
  "brand": string or null,
  "color": string or null,
  "target_age": string or null,
  "key_features": [string],
  "materials": string or null,
  "confidence": float between 0 and 1,
  "is_baby_product": boolean
}"""

def extract_attributes(image: Image.Image) -> ProductAttributes:
    client = _get_client()
    b64 = _image_to_base64(image)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }],
        max_tokens=500,
    )

    raw = re.sub(r"```json|```", "", response.choices[0].message.content.strip()).strip()
    data = json.loads(raw)
    return ProductAttributes(**data)