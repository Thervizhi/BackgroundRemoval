import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
import os
import traceback
import time

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Image Background Remover")

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 2000  # pixels

# --- HELPER FUNCTIONS ---

def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def resize_image(image, max_size):
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image
    
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    return image.resize((new_width, new_height), Image.LANCZOS)

@st.cache_data
def process_image(image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes))
        resized = resize_image(image, MAX_IMAGE_SIZE)
        fixed = remove(resized)
        return image, fixed
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None

# --- UI HEADER ---
st.write("## 🪄 Remove background from your image")
st.write(
    ":dog: Drag and drop your image below to watch the magic happen. High-quality results will appear instantly."
)

# --- SIDEBAR ---
st.sidebar.header("Settings & Download :gear:")
with st.sidebar.expander("ℹ️ Image Guidelines"):
    st.write("- Max size: 10MB\n- Format: PNG, JPG, JPEG")

# --- MAIN UPLOAD AREA ---
# Placing the uploader in the main body makes drag-and-drop much more accessible
uploaded_file = st.file_uploader(
    "Drag and drop an image here", 
    type=["png", "jpg", "jpeg"],
    help="Limit 10MB per file • PNG, JPG, JPEG"
)

# Layout for results
col1, col2 = st.columns(2)

def handle_processing(source):
    """Encapsulated logic to process and display images"""
    start_time = time.time()
    
    # Progress feedback
    with st.status("Treating image...", expanded=True) as status:
        st.write("Reading file...")
        if isinstance(source, str): # Handle default path
            with open(source, "rb") as f:
                image_bytes = f.read()
        else: # Handle UploadedFile object
            image_bytes = source.getvalue()
        
        st.write("Analyzing and removing background...")
        image, fixed = process_image(image_bytes)
        
        if image and fixed:
            status.update(label="Healing complete!", state="complete", expanded=False)
            
            col1.subheader("Original :camera:")
            col1.image(image, use_container_width=True)
            
            col2.subheader("Result :wrench:")
            col2.image(fixed, use_container_width=True)
            
            # Download Button in Sidebar
            st.sidebar.success("Processing Successful!")
            st.sidebar.download_button(
                label="Download Result",
                data=convert_image(fixed),
                file_name="background_removed.png",
                mime="image/png",
                use_container_width=True
            )
            
            processing_time = time.time() - start_time
            st.toast(f"Finished in {processing_time:.2f}s", icon='✅')

# --- LOGIC CONTROL ---
if uploaded_file is not None:
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error(f"File too large! Please keep it under 10MB.")
    else:
        handle_processing(uploaded_file)
else:
    # Default image logic
    default_path = "./zebra.jpg"
    if os.path.exists(default_path):
        st.info("Showing example below. Upload your own to change it!")
        handle_processing(default_path)
    else:
        st.info("💡 Clinical Tip: Drag an image file directly onto the box above to begin.")