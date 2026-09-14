from modules.voice_processing.speech_to_text import transcribe_audio
from modules.extraction.voice_contact_extractor import extract_contact
from modules.extraction.voice_adapter import convert_voice_contact

from image_module.context_classifier import classify_context
from image_module.duplicate_detector import update_or_create_contact
from image_module.vcf_generator import create_vcf


# --------------------------------------------------
# AUDIO FILE
# --------------------------------------------------

audio_file = "data/audio/contact_001.wav"


# --------------------------------------------------
# 1. SPEECH TO TEXT
# --------------------------------------------------

print("\n" + "=" * 40)
print("          VOICE TRANSCRIPT")
print("=" * 40)

transcript = transcribe_audio(audio_file)

print(transcript)


# --------------------------------------------------
# 2. VOICE CONTACT EXTRACTION
# --------------------------------------------------

voice_contact = extract_contact(transcript)

print("\n" + "=" * 40)
print("          VOICE CONTACT")
print("=" * 40)

for key, value in voice_contact.items():

    print(f"{key}: {value}")


# --------------------------------------------------
# 3. CONVERT TO UNIFIED CONTACT
# --------------------------------------------------

unified_contact = convert_voice_contact(
    voice_contact
)


# --------------------------------------------------
# 4. CONTEXT CLASSIFICATION
# --------------------------------------------------

context, business_score, personal_score = classify_context(
    unified_contact
)

unified_contact["context"] = context


print("\n" + "=" * 40)
print("         UNIFIED CONTACT")
print("=" * 40)

for key, value in unified_contact.items():

    print(f"{key}: {value}")


print("\n" + "=" * 40)
print("      CONTEXT CLASSIFICATION")
print("=" * 40)

print(f"\nBusiness Score: {business_score}")
print(f"Personal Score: {personal_score}")

print(f"\nDetected Context: {context}")


# --------------------------------------------------
# 5. DUPLICATE DETECTION
# --------------------------------------------------

result = update_or_create_contact(
    unified_contact
)


print("\n" + "=" * 40)
print("       DATABASE ACTION")
print("=" * 40)


if result["action"] == "updated":

    print("\nSTATUS: DUPLICATE")
    print("ACTION: EXISTING CONTACT UPDATED")

    print(
        f"\nExisting Contact ID: "
        f"{result['contact_id']}"
    )

    print(
        f"Similarity Score: "
        f"{result['score']}"
    )

    print("\nReasons:")

    for reason in result["reasons"]:

        print(f"- {reason}")


else:

    print("\nSTATUS: NEW CONTACT")
    print("ACTION: NEW CONTACT CREATED")

    print(
        f"\nNew Contact ID: "
        f"{result['contact_id']}"
    )

    print(
        f"Similarity Score: "
        f"{result['score']}"
    )


# --------------------------------------------------
# 6. VCF GENERATION
# --------------------------------------------------

print("\n" + "=" * 40)
print("          VCF GENERATION")
print("=" * 40)


vcf_file = create_vcf(
    unified_contact
)


print("\nVCF file created successfully!")

print("\nFile location:")
print(vcf_file)


# --------------------------------------------------
# 7. PIPELINE COMPLETED
# --------------------------------------------------

print("\n" + "=" * 40)
print("       VOICE PIPELINE COMPLETED")
print("=" * 40)