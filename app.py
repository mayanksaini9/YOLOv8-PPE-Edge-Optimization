import streamlit as st
import fitz  # PyMuPDF
import os
import base64
import re
from google import genai
from google.genai import types

# ==========================================================
# CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="DDR Report Generator",
    page_icon="🏗️",
    layout="wide",
)

API_KEY = "AIzaSyDwASo6bstu_dit7X0JtZ09aE2FjNGZZvE"

TEMP_DIR = "temp_processing_data"
IMAGES_DIR = os.path.join(TEMP_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

st.markdown("""
<style>
    .report-box { padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; background-color: #fcfcfc; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# CORE AI LOGIC (ONE-SHOT GENERATION)
# ==========================================================
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=API_KEY)


def extract_content(pdf_file_bytes, source_prefix):
    """Extracts raw text and saves images locally for HTML rendering later."""
    text_content = ""
    image_catalog = []
    
    try:
        doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")
    except Exception as e:
        return text_content, image_catalog

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_content += f"\n--- {source_prefix.upper()} Page {page_num + 1} ---\n{page.get_text()}"
        
        for img_index, img in enumerate(page.get_images(full=True)):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]
                
                # ==========================================
                # FIX: FILTER OUT JUNK / TINY PDF ARTIFACTS
                # ==========================================
                # Ignore background tiles, icons, and 1x1 pixels.
                # E.g., skip images smaller than ~10 KB.
                if len(image_bytes) < 10240: 
                    continue
                
                # Filter by dimensions (ignoring tiny lines or icons)
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                if width < 100 or height < 100: 
                    continue
                # ==========================================
                
                img_name = f"{source_prefix}_p{page_num+1}_i{img_index+1}.{ext}"
                img_path = os.path.join(IMAGES_DIR, img_name)
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                image_catalog.append({
                    "id": img_name,
                    "path": img_path,
                    "ext": ext
                })
            except Exception:
                pass
                
    return text_content, image_catalog


def generate_ddr_one_shot(client, sample_text, thermal_text, all_images):
    """
    Passes EVERYTHING at once to gemini-2.0-flash-lite to bypass Rate Limits.
    """
    ai_contents = []
    
    # 1. Add Text
    ai_contents.append(f"--- RAW INSPECTION DATA ---\n{sample_text}\n--- RAW THERMAL DATA ---\n{thermal_text}")
    
    # ==========================================
    # FIX: CAP IMAGES FOR TESTING
    # ==========================================
    # Set limit to 50 for testing. You can increase this later once successful.
    MAX_IMAGES = 10
    if len(all_images) > MAX_IMAGES:
        st.warning(f"⚠️ High image count! Sending only the first {MAX_IMAGES} images to the AI for this test run.")
        all_images = all_images[:MAX_IMAGES]

    # 2. Add Images as raw byte references
    image_ids = []
    for img in all_images:
        try:
            with open(img["path"], "rb") as f:
                image_data = f.read()
            mime_ext = "jpeg" if img["ext"].lower() == "jpg" else img["ext"].lower()
            mime_type = f"image/{mime_ext}"
            
            # Label each part for the AI
            ai_contents.append(f"\n--- IMAGE REFERENCE: {img['id']} ---\n")
            ai_contents.append(types.Part.from_bytes(data=image_data, mime_type=mime_type))
            image_ids.append(img['id'])
        except Exception:
            pass
            
    # 3. Add Instructions
    instruction = f"""
    You are an expert AI Structural and Thermal Inspector. 
    You have been provided with Site Inspection Text, Thermal Text, and a series of image files. 
    The ID for each image file in the sequence is: {', '.join(image_ids)}.

    --- OUTPUT REQUIREMENTS ---
    Generate a highly professional, well-formatted Markdown report containing EXACTLY these 7 sections:
    
    1. Property Issue Summary
    2. Area-wise Observations 
       *CRITICAL RULE:* You must embed the relevant images provided under their corresponding observation. Support your findings using this exact HTML syntax: `<img src="IMAGE_ID_PLACEHOLDER" width="500">` using the exact IDs I provided previously. Ensure images match context (e.g. thermal images for leaks). If an image is missing, write "Image Not Available".
    3. Probable Root Cause
    4. Severity Assessment
    5. Recommended Actions
    6. Additional Notes
    7. Missing or Unclear Information (explicitly call out missing data or conflicting data between the two reports).

    Do NOT hallucinate. Do not make up issue scenarios. Produce the final report cleanly.
    """
    ai_contents.append(instruction)

    try:
        # Use a model with a MASSIVE free tier quota!
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=ai_contents
        )
        return response.text, None
    except Exception as e:
        return None, str(e)


def base64_encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# ==========================================================
# STREAMLIT USER INTERFACE 
# ==========================================================
def main():
    st.title("🏢 DDR Report Generation Engine")
    st.markdown("Automated one-shot ingestion of inspection rules.")

    col1, col2 = st.columns(2)
    with col1:
        sample_pdf = st.file_uploader("Upload Inspection PDF", type=["pdf"], key="sample")
    with col2:
        thermal_pdf = st.file_uploader("Upload Thermal Report PDF", type=["pdf"], key="thermal")

    st.divider()

    if sample_pdf and thermal_pdf:
        if st.button("🚀 Execute AI Workflow & Generate DDR", use_container_width=True, type="primary"):
            client = get_gemini_client()
            
            with st.status("Initializing AI System Workflow...", expanded=True) as status:
                st.write("📄 **Stage 1: Document Parsing & Image Extraction**")
                sample_text, sample_images = extract_content(sample_pdf.read(), "inspection")
                thermal_text, thermal_images = extract_content(thermal_pdf.read(), "thermal")
                
                # Before adding them all, check how many were extracted
                all_img = sample_images + thermal_images
                st.write(f"✅ Extracted **{len(all_img)}** valid images after filtering out tiny PDF artifacts.")

                st.write("🧠 **Stage 2: Single-Shot Multimodal Synthesis**")
                st.write("Sending text and visual data to Gemini Pro simultaneously...")
                
                raw_report, error_msg = generate_ddr_one_shot(client, sample_text, thermal_text, all_img)
                
                if not raw_report:
                    status.update(label="❌ Google API Error.", state="error", expanded=True)
                    st.error(f"Fatal Error from Gemini API: {error_msg}")
                    st.stop()
                else:
                    status.update(label="✅ DDR Report Generated Successfully!", state="complete", expanded=False)

            # Render
            st.subheader("📑 Final Detailed Diagnostic Report (DDR)")
            
            final_md = raw_report
            
            # Using regex to elegantly replace the image tags in case the model used slightly different formatting
            for img in all_img:
                img_id = img["id"]
                # Match various possible forms of <img src="IMG_ID" ...> the AI might output
                pattern = rf'<img\s+[^>]*src=[\'"]{img_id}[\'"][^>]*>'
                
                if re.search(pattern, final_md):
                    try:
                        b64_str = base64_encode_image(img['path'])
                        uri = f"data:image/{img['ext']};base64,{b64_str}"
                        styled_tag = f'<img src="{uri}" width="100%" style="max-width: 600px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 15px 0;">'
                        final_md = re.sub(pattern, styled_tag, final_md)
                    except Exception as e:
                        pass # if there is an issue reading back the file, ignore

            st.markdown('<div class="report-box">', unsafe_allow_html=True)
            st.markdown(final_md, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download Button
            st.divider()
            safe_download_md = raw_report
            for img in all_img:
                img_id = img['id']
                pattern = rf'<img\s+[^>]*src=[\'"]{img_id}[\'"][^>]*>'
                safe_download_md = re.sub(pattern, f"![Image](./images/{img_id})", safe_download_md)

            st.download_button(
                label="📥 Download Exported DDR Report (.md)",
                data=safe_download_md,
                file_name="Final_DDR_Report.md",
                mime="text/markdown",
                use_container_width=True
            )


if __name__ == "__main__":
    main()
