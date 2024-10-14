import streamlit as st
import os
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
import time
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def generate_extraction_prompt(patient_notes):
    prompt = f"""
    Analyze the following patient medical notes carefully and extract all relevant information related to Sickle Cell Disease (SCD) and related conditions. Use your medical knowledge to infer information that may not be explicitly stated. Provide detailed responses for each category, including "Not mentioned" when information is absent.
    you have to go through completly and i need the response to be cery accurate , no room for mistake .
    Patient Notes:
    {patient_notes}

    Please extract and infer the following information:

    1. Diagnosis:
       - Specific type of SCD or related condition (e.g., SCD Hb S/S, Hb S/β thalassemia, Sickle cell trait, etc.)
       - Reason for diagnosis (symptomatic, screening, other)

    2. Family History:
       - Consanguinity (Yes/No/Not mentioned)
       - Other affected family members (Yes/No/Not mentioned)

    3. Initial Symptoms (list all that apply):
       - Common SCD symptoms (e.g., pain, fever, anemia, jaundice, etc.)
       - Specific manifestations (e.g., dactylitis, stroke, acute chest syndrome, etc.)

    4. Investigations:
       - HPLC results (HbA, HbA2, HbS, HbF percentages if available)
       - Blood Film findings
       - Baseline Hemoglobin level
       - Baseline Reticulocyte count percentage
       - G6PD status

    5. Treatment:
       - Hydroxyurea (Yes/No, dosage if mentioned)
       - Number of PRBC (Packed Red Blood Cell) units transfused
       - Folic acid prophylaxis (Yes/No)
       - Antibiotic prophylaxis (Yes/No, type if specified)

    6. Vaccinations:
       - Pneumococcal vaccine (Yes/No, date if available)
       - Annual influenza vaccine (Yes/No, latest date if available)

    7. Complications (For each, state Yes/No and provide details if available):
       - Vaso-occlusive crisis (VOC)
       - Stroke
       - Splenic sequestration
       - Splenectomy
       - Priapism
       - Osteomyelitis (OM)
       - Acute Chest Syndrome (ACS)
       - Aplastic crisis
       - Iron overload (include ferritin level if mentioned)
       - Hemolytic anemia
       - Cholecystitis
       - Sepsis
       - Avascular Necrosis (AVN)
       - Chronic blood transfusion (include reason if mentioned)
       - Alloimmunization

    8. Bone Marrow Transplantation (BMT):
       - Status (Done/Planned/Not mentioned)
       - Details if available

    9. Other Relevant Information:
       - Any additional findings or comments relevant to the patient's SCD management

    Provide your analysis in a structured format, clearly labeling each section and subsection. If information for a category is not available or not mentioned in the notes, explicitly state "Not mentioned" or "No information available".
    """
    return prompt

def process_with_gemini(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def type_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(0.01)  # Adjust this value to change typing speed
    container.markdown(full_text)

def main():
    st.set_page_config(page_title="SCD Medical Information Extractor", layout="wide")
    st.title("SCD Medical Information Extractor")

    uploaded_files = st.file_uploader("Upload patient medical notes (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Extract Details"):
            with st.spinner("Processing..."):
                # Extract text from all uploaded PDFs
                patient_notes = get_pdf_text(uploaded_files)
                
                # Generate prompt and process with Gemini
                prompt = generate_extraction_prompt(patient_notes)
                extracted_info = process_with_gemini(prompt)
                
                # Display extracted information with typing effect
                st.subheader("Extracted Medical Information")
                type_effect(extracted_info)
    logo = Image.open("ministry.png")  # Replace with the actual path to your logo
    st.sidebar.image(logo, use_column_width=True)            

    st.sidebar.title("About")
    st.sidebar.info(
        "This application extracts and analyzes medical information "
        "related to Sickle Cell Disease from uploaded patient notes. "
        "It uses advanced language processing to infer details that "
        "may not be explicitly stated in the notes."
    )
    

if __name__ == "__main__":
    main()