

import streamlit as st
from PIL import Image
from pipeline.vision import extract_attributes
from pipeline.rag import retrieve
from pipeline.generator import generate_pdp

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Mumzworld PDP Generator", page_icon="🛒", layout="wide")
st.title("🛍️ Mumzworld — AI Product Page Generator")
st.caption("Upload a baby/mother product image → get bilingual EN/AR product copy instantly")

uploaded = st.file_uploader("Upload product image", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded product", width=300)

    with st.spinner("Analyzing image..."):
        attrs = extract_attributes(image)

    st.subheader("🔍 Extracted Attributes")
    st.json(attrs.model_dump())

    if not attrs.is_baby_product:
        st.error("⚠️ This doesn't appear to be a baby/mother product. Generation refused.")
        st.stop()

    query = f"{attrs.product_type} {' '.join(attrs.key_features)}"
    guidelines = retrieve(query)

    st.info(f"📂 Matched category: **{guidelines['category']}** — tone: *{guidelines['tone']}*")

    with st.spinner("Generating bilingual product page..."):
        pdp = generate_pdp(attrs, guidelines)

    if not pdp.grounded:
        st.error(f"Generation refused: {pdp.refusal_reason}")
        st.stop()

    # Confidence badge
    score = pdp.confidence_score
    color = "green" if score > 0.75 else "orange" if score > 0.5 else "red"
    st.markdown(f"**Confidence:** :{color}[{score:.0%}]")

    if pdp.refused_fields:
        st.warning(f"⚠️ Uncertain fields (returned null): {', '.join(pdp.refused_fields)}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🇬🇧 English")
        st.markdown(f"### {pdp.title_en}")
        st.write(pdp.description_en)
        for b in pdp.bullets_en:
            st.markdown(f"- {b}")

    with col2:
        st.subheader("🇸🇦 العربية")
        st.markdown(f"### {pdp.title_ar}")
        st.write(pdp.description_ar)
        for b in pdp.bullets_ar:
            st.markdown(f"- {b}")

    st.divider()
    st.download_button(
        "⬇️ Download PDP as JSON",
        data=pdp.model_dump_json(indent=2),
        file_name="pdp_output.json",
        mime="application/json"
    )