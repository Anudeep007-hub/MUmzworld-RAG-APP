import os, json, re
from dotenv import load_dotenv
from openai import OpenAI
from .schemas import ProductAttributes, PDPOutput

load_dotenv()

EN_MODEL = "openrouter/auto"
AR_MODEL = "openrouter/auto"
def _get_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
    )

def _call(model: str, prompt: str) -> str:
    client = _get_client()
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
    )
    return r.choices[0].message.content.strip()

def generate_pdp(attrs: ProductAttributes, guidelines: dict) -> PDPOutput:
    if not attrs.is_baby_product:
        return PDPOutput(
            grounded=False,
            confidence_score=0.0,
            refusal_reason="Image does not appear to be a baby or mother-related product.",
            refused_fields=["all"]
        )

    attr_str = attrs.model_dump_json(indent=2)
    guide_str = json.dumps(guidelines, indent=2)

    en_prompt = f"""You are writing product copy for Mumzworld, a baby e-commerce platform.

Product attributes:
{attr_str}

Category writing guidelines:
{guide_str}

Generate a Product Detail Page in English. Return ONLY valid JSON:
{{
  "title_en": "...",
  "description_en": "2-3 sentences, {guidelines['tone']} tone",
  "bullets_en": ["feature 1", "feature 2", "feature 3"]
}}

Rules:
- Only use information present in the attributes. Do not invent specs.
- If a field cannot be determined, use null.
- No markdown, return raw JSON only."""

    ar_prompt = f"""أنت تكتب محتوى منتج لموقع Mumzworld لتجارة منتجات الأمومة والطفولة.

صفات المنتج:
{attr_str}

أسلوب الكتابة: {guidelines['arabic_style']}

اكتب صفحة تفاصيل المنتج باللغة العربية. أعد JSON فقط:
{{
  "title_ar": "...",
  "description_ar": "2-3 جمل",
  "bullets_ar": ["ميزة 1", "ميزة 2", "ميزة 3"]
}}

قواعد:
- استخدم فقط المعلومات الموجودة في الصفات. لا تخترع مواصفات.
- إذا لم يمكن تحديد حقل، استخدم null.
- لا تستخدم markdown، أعد JSON فقط."""

    try:
        en_raw = re.sub(r"```json|```", "", _call(EN_MODEL, en_prompt)).strip()
        ar_raw = re.sub(r"```json|```", "", _call(AR_MODEL, ar_prompt)).strip()
        en_data = json.loads(en_raw)
        ar_data = json.loads(ar_raw)
    except (json.JSONDecodeError, Exception) as e:
        return PDPOutput(
            grounded=False,
            confidence_score=0.0,
            refusal_reason=f"Generation failed: {str(e)}",
            refused_fields=["all"]
        )

    refused = [k for k, v in {**en_data, **ar_data}.items() if v is None]

    return PDPOutput(
        title_en=en_data.get("title_en"),
        title_ar=ar_data.get("title_ar"),
        description_en=en_data.get("description_en"),
        description_ar=ar_data.get("description_ar"),
        bullets_en=en_data.get("bullets_en", []),
        bullets_ar=ar_data.get("bullets_ar", []),
        confidence_score=attrs.confidence,
        grounded=True,
        refused_fields=refused,
    )