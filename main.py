import streamlit as st
import base64
import requests
import json

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
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Convert image to base64
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
                        "text": "Please analyze the attached handwritten note and convert its content into JSON. Maintain a clean structure with keys like 'title', 'body', etc."
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
