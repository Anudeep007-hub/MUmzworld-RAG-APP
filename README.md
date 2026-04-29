# Mumzworld PDP Generator

Upload a baby product image. Get a bilingual English + Arabic product page in 10 seconds.

**Live demo:** [your-app.streamlit.app](https://your-app.streamlit.app) ← replace after deploy

---

## What it does

Mumzworld sells baby products to mothers across the GCC. Writing product pages in both English and Arabic for every SKU is slow and inconsistent. This tool solves that.

You upload a product image → the system:
1. Extracts product attributes from the image (type, color, features, target age)
2. Retrieves the matching Mumzworld category writing guidelines from a vector store
3. Generates a structured PDP in English (Llama 3.3 70B) and Arabic (Qwen 2.5 72B)
4. Validates every field against a Pydantic schema — null if uncertain, never hallucinated
5. Refuses generation entirely if the image isn't a baby/mother product

The Arabic output follows Mumzworld's tone per category — formal MSA for safety-critical products (car seats, formula), warmer tone for toys and feeding. Not a translation of the English.

---

## Setup

```bash
git clone https://github.com/yourname/mumzworld-pdp-generator
cd mumzworld-pdp-generator
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key      # free at aistudio.google.com
OPENROUTER_API_KEY=your_key  # free at openrouter.ai
```

Run:
```bash
streamlit run app.py
```

That's it. No database, no external services beyond the two API keys.

---

## Docker

```bash
docker build -t mumzworld-pdp .
docker run -p 8501:8501 --env-file .env mumzworld-pdp
```

Open http://localhost:8501

---

## Architecture

```
Image upload
  → Gemini 2.0 Flash (vision)   → ProductAttributes (Pydantic)
  → FAISS + sentence-transformers → category guidelines (RAG)
  → Llama 3.3 70B (OpenRouter)  → English PDP fields
  → Qwen 2.5 72B (OpenRouter)   → Arabic PDP fields
  → Pydantic validation          → PDPOutput schema
  → Streamlit                    → rendered bilingual page
```

**Why RAG here?** The LLM doesn't just write copy from scratch. It retrieves Mumzworld's category-specific tone, required attributes, and example patterns first. A stroller description pulls different guidelines than a formula tin. This keeps output consistent across categories without fine-tuning.

**Why separate models for EN and AR?** Qwen 2.5 72B has significantly better Arabic than Llama 3.3. Using one model for both languages produced Arabic that read like translated English. Two model calls, better output.

**Uncertainty handling:** If the vision model can't determine a field, it returns `null`. The generator is instructed not to fill nulls. Refused fields are surfaced in the UI in orange. If the image isn't baby-related, generation is blocked entirely with a reason.

---

## Evals

See `evals/run_evals.py` and `EVALS.md` for the full rubric and test cases.

Short version: 12 test cases across easy (clear stroller photo), medium (blurry/partial product), and adversarial (car photo, empty image, product outside Mumzworld scope). Scored on field accuracy, Arabic quality, schema validity, and grounding.

---

## Tradeoffs

See `TRADEOFFS.md` for the full write-up.

Short version:
- Picked image→PDP over the classifier and review synthesis problems because it hits multimodal + RAG + structured output + evals in one flow. The other problems only needed 1-2 of those.
- Used Gemini free tier for vision. It's better than Llava-13B on product images at zero cost.
- Streamlit over FastAPI + React because the submission needed a live demo, not an API. A production version would split these.
- Didn't add a feedback loop or caching. That's the obvious next thing.

---

## What I'd build next

- Human-in-the-loop review for the Arabic output before publishing
- Fine-tune on actual Mumzworld PDP data once access is available
- Batch mode: CSV of image URLs → bulk generate + export
- Confidence threshold gate: don't publish below 0.6, flag for manual review

---

## Tooling

- **Gemini 2.0 Flash (free tier)** — vision extraction. Used directly via `google-generativeai` SDK.
- **Llama 3.3 70B via OpenRouter (free)** — English copy generation.
- **Qwen 2.5 72B via OpenRouter (free)** — Arabic copy generation. Tried Llama for Arabic first, switched after output quality was poor.
- **sentence-transformers + FAISS** — local embeddings and retrieval, no API call needed.
- **Claude (claude.ai)** — architecture planning, code scaffolding, README draft. All logic reviewed and tested manually.
- **Pydantic v2** — schema validation throughout. Caught silent failures during testing.

---

## Time log

| Phase | Time |
|---|---|
| Problem scoping + architecture | 45 min |
| Data synthesis (knowledge base) + RAG setup | 60 min |
| Vision pipeline + validation | 60 min |
| Generator (EN + AR) | 75 min |
| Streamlit UI | 45 min |
| Evals + fixes | 60 min |
| README + deploy | 15 min |
| **Total** | **~6 hours** |

Went one hour over. The Arabic quality debugging (switching from Llama to Qwen mid-build) took longer than expected.