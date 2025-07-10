import streamlit as st
import base64
import requests
import json
import pytesseract
from PIL import Image

def extract_text_from_image(image):
    """
    Extract text from an image using Tesseract OCR.
    """
    try:
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text
    except Exception as e:
        st.error(f"Error extracting text from image: {e}")
        return None

# API URL input
api_url = st.text_input(
    "API Endpoint URL",
    value="http://localhost:1234/v1/chat/completions",
    help="Enter the URI of your LLM API endpoint."
)
MODEL = "gemma-3-12b-it"

st.set_page_config(page_title="Handwritten Note to JSON", layout="centered")
st.title("📝 Handwritten Note to Structured JSON")

# File uploader
uploaded_file = st.file_uploader("Upload a handwritten note image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Display uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)  # updated parameter

    # Convert uploaded file to PIL Image for pytesseract
    image = Image.open(uploaded_file)

    # need to use pytesseract to extract text from the image
    extracted_text = extract_text_from_image(image)

    # Show extracted text in the UI
    st.subheader("🔍 Extracted Text (OCR)")
    st.code(extracted_text if extracted_text else "[No text extracted]", language="text")

    # Convert image to base64
    uploaded_file.seek(0)  # Reset file pointer after PIL read
    base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
    mime_type = uploaded_file.type  # e.g., "image/jpeg"

    # Payload
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an intelligent assistant that reads handwritten notes and converts them into JSON format. Prioritize accuracy, interpret messy handwriting when needed, and preserve the intent and structure of the note. If a list is found, output it as an array. If headings or subheadings are detected, represent them hierarchically. When in doubt, make a best guess and flag uncertain interpretations."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please analyze the attached handwritten note and convert its content into JSON. Maintain a clean structure with keys like 'title', 'body', etc.\n\nAdditionally, here is the text extracted from the image using OCR (pytesseract). Use this as context to improve your understanding:\n\n" + (extracted_text if extracted_text else "[No text extracted]")
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.3,
        "stream": False
    }

    if st.button("Convert to JSON"):
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(api_url, json=payload)
                response.raise_for_status()
                result = response.json()

                # Display structured output
                # st.subheader("📋 Structured JSON Output")
                # st.code(json.dumps(result["choices"][0]["message"]["content"], indent=2), language="json")
                raw_content = result["choices"][0]["message"]["content"]

                # Remove markdown formatting if present
                cleaned_content = raw_content.strip("`").strip()
                if cleaned_content.startswith("json"):
                    cleaned_content = cleaned_content[4:].strip()

                try:
                    # Parse JSON content
                    parsed_json = json.loads(cleaned_content)
                    
                    st.subheader("📋 Structured JSON Output")
                    st.json(parsed_json)  # Pretty rendering

                except json.JSONDecodeError:
                    st.subheader("📋 Raw Output (Not Valid JSON)")
                    st.code(cleaned_content, language="json")

            except Exception as e:
                st.error(f"❌ Error: {e}")
