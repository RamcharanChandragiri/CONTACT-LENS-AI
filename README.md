# CONTACT-LENS-AI

ContactLens AI converts contact information from a camera image into a validated,
context-aware, duplicate-free digital contact. It also supports voice-assisted
contact completion and complete contact capture by voice.

## Main workflow

CAMERA → OCR → EXTRACTION → VALIDATION → CONTEXT CLASSIFICATION
→ DUPLICATE DETECTION / SMART UPDATE → VCF

VOICE → FASTER-WHISPER → VOICE EXTRACTION → VALIDATION
→ CONTEXT CLASSIFICATION → DUPLICATE DETECTION / SMART UPDATE → VCF

## Run the Streamlit interface

Activate the virtual environment and install dependencies:

```powershell
pip install -r requirements.txt
```

Start the application:

```powershell
streamlit run app.py
```

Then open the Local URL shown by Streamlit, normally:

```text
http://localhost:8501
```

## UI workflow

1. Capture a contact card with the camera.
2. Click **Scan & Process Contact**.
3. Review the extracted fields.
4. Either type corrections, use the microphone beside an individual field,
   or use **Speak Complete Contact**.
5. Click **Confirm & Save Contact**.
6. The system validates the contact, classifies context, checks for duplicates,
   updates an existing contact or creates a new one, and generates a VCF file.
7. Use **Save Contact** to download the generated VCF.

## Notes

- `data/generated_contacts/` is created automatically when a VCF is generated.
- The Faster-Whisper `small` model runs on CPU with INT8 in the current setup.
- The project is designed around Indian 10-digit mobile numbers.
