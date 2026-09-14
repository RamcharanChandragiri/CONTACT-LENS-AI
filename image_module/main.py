from ..contact_model import create_contact

from image_module.contact_extractor import extract_contact
from image_module.address_extractor import extract_address
from image_module.validator import validate_contact
from image_module.context_classifier import classify_context
from image_module.duplicate_detector import update_or_create_contact

from ..vcf_generator import create_vcf


# ---------------------------------------------------------
# IMAGE PATH
# ---------------------------------------------------------

image_path = r"C:\Users\sathw\OneDrive\Pictures\Screenshots\Screenshot 2026-09-07 215524.png"


# ---------------------------------------------------------
# STEP 1: IMAGE OCR EXTRACTION
# ---------------------------------------------------------

print("\n" + "=" * 40)
print("        IMAGE CONTACT EXTRACTION")
print("=" * 40)

extracted = extract_contact(image_path)


# ---------------------------------------------------------
# STEP 2: ADDRESS EXTRACTION
# ---------------------------------------------------------

address = extract_address(image_path)


# ---------------------------------------------------------
# STEP 3: CREATE UNIFIED CONTACT
# ---------------------------------------------------------

email = None

if extracted.get("email_addresses"):
    email = extracted["email_addresses"][0]


unified_contact = create_contact(
    name=None,
    organization=extracted.get("organization"),
    designation=None,
    phone_numbers=extracted.get("phone_numbers", []),
    email=email,
    website=extracted.get("website"),
    address=address,
    source="image",
    confidence=1.0,
    context=None
)


# ---------------------------------------------------------
# STEP 4: VALIDATION
# ---------------------------------------------------------

validated_contact = validate_contact({
    "name": unified_contact.get("name"),
    "organization": unified_contact.get("organization"),
    "designation": unified_contact.get("designation"),
    "phone_numbers": unified_contact.get("phone_numbers", []),
    "email_addresses": (
        [unified_contact["email"]]
        if unified_contact.get("email")
        else []
    ),
    "website": unified_contact.get("website"),
    "address": unified_contact.get("address"),
    "source": unified_contact.get("source"),
    "confidence": unified_contact.get("confidence"),
    "context": unified_contact.get("context")
})


# ---------------------------------------------------------
# STEP 5: CONTEXT CLASSIFICATION
# ---------------------------------------------------------

context, business_score, personal_score = classify_context(
    validated_contact
)

validated_contact["context"] = context


print("\n" + "=" * 40)
print("        CONTEXT CLASSIFICATION")
print("=" * 40)

print(f"\nBusiness Score: {business_score}")
print(f"Personal Score: {personal_score}")

print("\nDetected Context:")
print(context)


# ---------------------------------------------------------
# STEP 6: DISPLAY CONTACT
# ---------------------------------------------------------

print("\n" + "=" * 40)
print("        EXTRACTED CONTACT")
print("=" * 40)

print("\nOrganization:")
print(validated_contact.get("organization"))

print("\nPhone Numbers:")

for phone in validated_contact.get("phone_numbers", []):
    print(phone)

print("\nEmail:")
print(validated_contact.get("email"))

print("\nWebsite / Social Media:")
print(validated_contact.get("website"))

print("\nAddress:")
print(validated_contact.get("address"))

print("\nContext:")
print(validated_contact.get("context"))


# ---------------------------------------------------------
# STEP 7: DUPLICATE CHECK + UPDATE / CREATE
# ---------------------------------------------------------

result = update_or_create_contact(
    validated_contact
)


# ---------------------------------------------------------
# STEP 8: DATABASE ACTION
# ---------------------------------------------------------

print("\n" + "=" * 40)
print("        DATABASE ACTION")
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
        f"\nSimilarity Score: "
        f"{result['score']}"
    )


# ---------------------------------------------------------
# STEP 9: VCF GENERATION
# ---------------------------------------------------------

print("\n" + "=" * 40)
print("          VCF GENERATION")
print("=" * 40)

vcf_file = create_vcf(
    validated_contact
)

print("\nVCF file created successfully!")

print("\nFile location:")
print(vcf_file)


# ---------------------------------------------------------
# COMPLETE
# ---------------------------------------------------------

print("\n" + "=" * 40)
print("        PIPELINE COMPLETED")
print("=" * 40)