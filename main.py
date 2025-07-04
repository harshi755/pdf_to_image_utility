import streamlit as st
import os
import tempfile
import zipfile
from pdf2image import convert_from_path
from PIL import Image

st.set_page_config(page_title=" PDF to Images Converter", layout="wide")
st.title(" Upload ZIP of PDFs ➜ Get ZIP of Images")

uploaded_zip = st.file_uploader("Upload a ZIP file containing PDFs", type=["zip"])

if uploaded_zip:
    if st.button("🚀 Convert PDFs"):
        with st.spinner("🔄 Processing ZIP..."):
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_path = os.path.join(tmp_dir, "input.zip")
                with open(zip_path, "wb") as f:
                    f.write(uploaded_zip.read())

                # Extract ZIP
                extract_path = os.path.join(tmp_dir, "pdfs")
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)

                image_folder = os.path.join(tmp_dir, "images")
                os.makedirs(image_folder, exist_ok=True)

                def convert_pdfs(pdf_folder, output_folder):
                    pdf_count = 0
                    img_count = 0
                    for root, _, files in os.walk(pdf_folder):
                        for file in files:
                            if file.lower().endswith(".pdf") and not file.startswith("._"):
                                pdf_count += 1
                                pdf_path = os.path.join(root, file)
                                try:
                                    images = convert_from_path(pdf_path)
                                    for i, img in enumerate(images):
                                        base = os.path.splitext(file)[0]
                                        img_name = f"{base}_page_{i+1}.png"
                                        img.save(os.path.join(output_folder, img_name), "PNG")
                                        img_count += 1
                                except Exception as e:
                                    st.error(f"❌ Failed to convert {file}: {e}")
                    return pdf_count, img_count

                pdfs, imgs = convert_pdfs(extract_path, image_folder)

                result_zip_path = os.path.join(tmp_dir, "converted_images.zip")
                with zipfile.ZipFile(result_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(image_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, image_folder)
                            zipf.write(file_path, arcname=arcname)

                #load before deletion of temp directory
                with open(result_zip_path, "rb") as f:
                    zip_bytes = f.read()

        st.success(f"✅ Converted {pdfs} PDFs into {imgs} images!")

        st.download_button(
            label="📥 Download ZIP of Images",
            data=zip_bytes,
            file_name="converted_images.zip",
            mime="application/zip"
        )
