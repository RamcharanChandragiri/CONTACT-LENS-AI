import os
import cv2
import re
import tempfile
import streamlit as st

from contact_model import create_contact
from image_module.contact_extractor import extract_contact
from image_module.address_extractor import extract_address
from image_module.validator import validate_contact
from image_module.context_classifier import classify_context
from image_module.duplicate_detector import update_or_create_contact
from image_module.vcf_generator import create_vcf

from streamlit_mic_recorder import mic_recorder
from modules.voice_processing.speech_to_text import transcribe_audio
from modules.extraction.voice_contact_extractor import extract_contact as extract_voice_contact


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ContactLens AI",
    page_icon="📇",
    layout="centered"
)

st.title("📇 ContactLens AI")

st.write(
    "Scan a contact card and convert its information "
    "into a validated digital contact."
)

st.divider()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_text(text):

    if not text:
        return None

    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)

    return text if text else None


def normalize_phone(phone):

    digits = re.sub(
        r"\D",
        "",
        str(phone)
    )

    if len(digits) >= 10:
        return digits[-10:]

    return None


def collect_phone_numbers(results):

    phones = []

    for result in results:

        for phone in result.get(
            "phone_numbers",
            []
        ):

            phone = normalize_phone(phone)

            if phone and phone not in phones:
                phones.append(phone)

    return phones


def collect_emails(results):

    emails = []

    for result in results:

        for email in result.get(
            "email_addresses",
            []
        ):

            email = clean_text(email)

            if email and email not in emails:
                emails.append(email)

    return emails


def collect_websites(results):

    websites = []

    for result in results:

        website = clean_text(
            result.get("website")
        )

        if website and website not in websites:
            websites.append(website)

    return websites


def organization_score(text):

    if not text:
        return -100

    text_lower = text.lower()

    score = 0

    keywords = [
        "jeweller",
        "jewellers",
        "jewellery",
        "jewelry",
        "company",
        "technology",
        "technologies",
        "enterprise",
        "enterprises",
        "solutions",
        "industries",
        "store",
        "shop",
        "traders",
        "services"
    ]

    for keyword in keywords:

        if keyword in text_lower:
            score += 5

    if len(text.split()) >= 2:
        score += 2

    if text_lower in [
        "3",
        "ipi",
        "cz",
        "ci"
    ]:
        score -= 10

    return score


def choose_organization(results):

    candidates = []

    for result in results:

        organization = clean_text(
            result.get("organization")
        )

        if (
            organization
            and organization not in candidates
        ):

            candidates.append(
                organization
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            organization_score(item),
            len(item)
        ),
        reverse=True
    )

    return candidates[0]


# =========================================================
# VOICE FUNCTIONS
# =========================================================

def transcribe_voice(audio_bytes):

    if not audio_bytes:
        return ""

    temp_audio = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    try:

        temp_audio.write(audio_bytes)
        temp_audio.close()

        # IMPORTANT:
        # Existing speech_to_text.py provides
        # transcribe_audio(), not speech_to_text()

        transcript = transcribe_audio(
            temp_audio.name
        )

        return clean_text(
            transcript
        ) or ""

    finally:

        if os.path.exists(
            temp_audio.name
        ):

            try:
                os.remove(
                    temp_audio.name
                )

            except Exception:
                pass


def convert_spoken_phone_numbers(text):

    if not text:
        return []

    text = text.lower()

    replacements = {
        "zero": "0",
        "oh": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9"
    }

    for word, digit in replacements.items():

        text = re.sub(
            r"\b" + word + r"\b",
            digit,
            text
        )

    # First check whether Whisper already returned
    # one or more 10-digit numbers.
    number_groups = re.findall(
        r"\b\d{10}\b",
        text
    )

    if number_groups:

        unique_numbers = []

        for number in number_groups:

            if number not in unique_numbers:
                unique_numbers.append(number)

        return unique_numbers

    digits = re.sub(
        r"\D",
        "",
        text
    )

    if len(digits) >= 10:

        return [
            digits[-10:]
        ]

    return []


def convert_spoken_email(text):

    if not text:
        return ""

    text = text.lower().strip()

    text = text.replace(
        " at ",
        "@"
    )

    text = text.replace(
        " dot ",
        "."
    )

    text = text.replace(
        " underscore ",
        "_"
    )

    text = text.replace(
        " dash ",
        "-"
    )

    text = text.replace(
        " hyphen ",
        "-"
    )

    text = text.replace(
        " ",
        ""
    )

    return text


def convert_spoken_website(text):

    if not text:
        return ""

    text = text.lower().strip()

    text = text.replace(
        "https colon slash slash",
        "https://"
    )

    text = text.replace(
        "http colon slash slash",
        "http://"
    )

    text = text.replace(
        " dot ",
        "."
    )

    text = text.replace(
        " slash ",
        "/"
    )

    text = text.replace(
        " colon ",
        ":"
    )

    text = text.replace(
        " ",
        ""
    )

    return text


# =========================================================
# SESSION STATE
# =========================================================

if "extracted_contact" not in st.session_state:
    st.session_state.extracted_contact = None

if "scan_completed" not in st.session_state:
    st.session_state.scan_completed = False

if "save_completed" not in st.session_state:
    st.session_state.save_completed = False

if "vcf_file" not in st.session_state:
    st.session_state.vcf_file = None

if "scan_id" not in st.session_state:
    st.session_state.scan_id = 0

# Voice-updated field values
if "voice_name" not in st.session_state:
    st.session_state.voice_name = ""

if "voice_organization" not in st.session_state:
    st.session_state.voice_organization = ""

if "voice_designation" not in st.session_state:
    st.session_state.voice_designation = ""

if "voice_phones" not in st.session_state:
    st.session_state.voice_phones = ""

if "voice_email" not in st.session_state:
    st.session_state.voice_email = ""

if "voice_website" not in st.session_state:
    st.session_state.voice_website = ""

if "voice_address" not in st.session_state:
    st.session_state.voice_address = ""


# =========================================================
# CAMERA
# =========================================================

st.subheader("📷 Scan Contact")

camera_image = st.camera_input(
    "Point your camera at the contact card and capture it"
)


# =========================================================
# PROCESS CAMERA IMAGE
# =========================================================

if camera_image is not None:

    if st.button(
        "🔍 Scan & Process Contact",
        use_container_width=True
    ):

        temp_paths = []

        with st.spinner(
            "AI is scanning the contact card..."
        ):

            try:

                # =================================================
                # SAVE ORIGINAL IMAGE
                # =================================================

                original_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".png"
                )

                original_file.write(
                    camera_image.getbuffer()
                )

                original_file.close()

                original_path = original_file.name

                temp_paths.append(
                    original_path
                )


                # =================================================
                # READ IMAGE
                # =================================================

                image = cv2.imread(
                    original_path
                )

                if image is None:

                    st.error(
                        "❌ Unable to read the camera image."
                    )

                    st.stop()


                height, width = image.shape[:2]


                # =================================================
                # ENHANCE IMAGE
                # =================================================

                enhanced = cv2.resize(
                    image,
                    None,
                    fx=2,
                    fy=2,
                    interpolation=cv2.INTER_CUBIC
                )

                lab = cv2.cvtColor(
                    enhanced,
                    cv2.COLOR_BGR2LAB
                )

                l_channel, a_channel, b_channel = (
                    cv2.split(lab)
                )

                clahe = cv2.createCLAHE(
                    clipLimit=2.0,
                    tileGridSize=(8, 8)
                )

                l_channel = clahe.apply(
                    l_channel
                )

                enhanced = cv2.merge(
                    (
                        l_channel,
                        a_channel,
                        b_channel
                    )
                )

                enhanced = cv2.cvtColor(
                    enhanced,
                    cv2.COLOR_LAB2BGR
                )


                # =================================================
                # SAVE ENHANCED IMAGE
                # =================================================

                enhanced_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".png"
                )

                enhanced_file.close()

                enhanced_path = enhanced_file.name

                cv2.imwrite(
                    enhanced_path,
                    enhanced
                )

                temp_paths.append(
                    enhanced_path
                )


                # =================================================
                # OCR - ORIGINAL
                # =================================================

                original_result = extract_contact(
                    original_path
                )


                # =================================================
                # OCR - ENHANCED
                # =================================================

                enhanced_result = extract_contact(
                    enhanced_path
                )


                # =================================================
                # PHONE-FOCUSED CROP
                # =================================================

                phone_crop = image[
                    int(height * 0.60):height,
                    0:width
                ]

                phone_crop = cv2.resize(
                    phone_crop,
                    None,
                    fx=4,
                    fy=4,
                    interpolation=cv2.INTER_CUBIC
                )

                phone_crop_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".png"
                )

                phone_crop_file.close()

                phone_crop_path = phone_crop_file.name

                cv2.imwrite(
                    phone_crop_path,
                    phone_crop
                )

                temp_paths.append(
                    phone_crop_path
                )


                # =================================================
                # OCR - PHONE CROP
                # =================================================

                phone_result = extract_contact(
                    phone_crop_path
                )


                # =================================================
                # COMBINE OCR RESULTS
                # =================================================

                ocr_results = [
                    original_result,
                    enhanced_result,
                    phone_result
                ]


                # =================================================
                # ORGANIZATION
                # =================================================

                organization = choose_organization(
                    ocr_results
                )


                # =================================================
                # PHONE NUMBERS
                # =================================================

                phone_numbers = collect_phone_numbers(
                    ocr_results
                )


                # =================================================
                # EMAIL
                # =================================================

                emails = collect_emails(
                    ocr_results
                )

                email = (
                    emails[0]
                    if emails
                    else None
                )


                # =================================================
                # WEBSITE
                # =================================================

                websites = collect_websites(
                    ocr_results
                )

                website = (
                    websites[0]
                    if websites
                    else None
                )


                # =================================================
                # ADDRESS
                # =================================================

                address = extract_address(
                    original_path
                )

                address = clean_text(
                    address
                )


                # =================================================
                # CONTACT DETECTION CHECK
                # =================================================

                if (
                    not organization
                    and not phone_numbers
                    and not email
                    and not website
                    and not address
                ):

                    st.error(
                        "❌ No contact information detected."
                    )

                    st.info(
                        "Move closer to the card, keep it steady, "
                        "and scan again."
                    )

                    st.stop()


                # =================================================
                # CREATE CONTACT
                # =================================================

                raw_contact = create_contact(

                    name=None,

                    organization=organization,

                    designation=None,

                    phone_numbers=phone_numbers,

                    email=email,

                    website=website,

                    address=address,

                    source="camera",

                    confidence=1.0,

                    context=None
                )


                # =================================================
                # VALIDATE
                # =================================================

                validated_contact = validate_contact(
                    raw_contact
                )


                # =================================================
                # PHONE VALIDATION
                # =================================================

                if not validated_contact.get(
                    "phone_numbers"
                ):

                    st.warning(
                        "⚠️ No valid phone number was recognized."
                    )

                    st.info(
                        "Move closer to the phone-number section "
                        "and scan again."
                    )

                    st.stop()


                # =================================================
                # CONTEXT CLASSIFICATION
                # =================================================

                (
                    context,
                    business_score,
                    personal_score
                ) = classify_context(
                    validated_contact
                )

                validated_contact["context"] = context


                # =================================================
                # STORE EXTRACTED CONTACT
                # =================================================

                st.session_state.extracted_contact = (
                    validated_contact
                )

                st.session_state.scan_completed = True

                st.session_state.save_completed = False

                st.session_state.vcf_file = None

                st.session_state.scan_id += 1

                # Reset previous voice edits
                st.session_state.voice_name = ""
                st.session_state.voice_organization = ""
                st.session_state.voice_designation = ""
                st.session_state.voice_phones = ""
                st.session_state.voice_email = ""
                st.session_state.voice_website = ""
                st.session_state.voice_address = ""


                st.success(
                    "✅ Contact information extracted successfully!"
                )


            except Exception as error:

                st.error(
                    "❌ Error while processing contact: "
                    + str(error)
                )


            finally:

                for path in temp_paths:

                    if os.path.exists(path):

                        try:
                            os.remove(path)

                        except Exception:
                            pass


# =========================================================
# REVIEW SECTION
# =========================================================

if (
    st.session_state.scan_completed
    and st.session_state.extracted_contact
):

    contact = st.session_state.extracted_contact

    st.divider()

    st.subheader(
        "👀 Review Extracted Information"
    )

    st.info(
        "Review or correct the extracted information "
        "before saving."
    )


    # =====================================================
    # SAVE METHOD
    # =====================================================

    st.markdown(
        "### 📱 How do you want to save this contact?"
    )

    st.caption(
        "Type the information, use the microphone beside a field, "
        "or speak the complete contact once."
    )

    # =====================================================
    # COMPLETE CONTACT BY VOICE
    # =====================================================

    st.markdown("#### 🎙️ Speak Complete Contact")

    st.caption(
        "Example: My name is Rahul Kumar. I am a software engineer "
        "at ABC Technologies. My phone number is 9876543210. "
        "My email is rahul at gmail dot com."
    )

    full_contact_audio = mic_recorder(
        start_prompt="🎙️ Start speaking",
        stop_prompt="⏹️ Stop",
        just_once=True,
        use_container_width=True,
        key=f"full_contact_voice_{st.session_state.scan_id}"
    )

    if full_contact_audio:
        try:
            spoken_transcript = transcribe_voice(
                full_contact_audio["bytes"]
            )

            if spoken_transcript:
                spoken_contact = extract_voice_contact(
                    spoken_transcript
                )

                if spoken_contact.get("name"):
                    st.session_state.voice_name = spoken_contact["name"]

                if spoken_contact.get("company"):
                    st.session_state.voice_organization = spoken_contact["company"]

                if spoken_contact.get("designation"):
                    st.session_state.voice_designation = spoken_contact["designation"]

                if spoken_contact.get("phone"):
                    st.session_state.voice_phones = spoken_contact["phone"]

                if spoken_contact.get("email"):
                    st.session_state.voice_email = spoken_contact["email"]

                st.success("🎙️ Contact details captured from voice.")
                st.rerun()

            else:
                st.warning("⚠️ No speech was detected. Please try again.")

        except Exception as error:
            st.error("❌ Voice recognition failed: " + str(error))


    # =====================================================
    # CONTACT NAME
    # =====================================================

    st.markdown(
        "#### ✍️ Contact Name"
    )

    name_col1, name_col2 = st.columns(
        [6, 1]
    )

    name_key = f"name_{st.session_state.scan_id}"

    default_name = (
        st.session_state.voice_name
        or contact.get("name")
        or ""
    )

    with name_col1:

        edited_name = st.text_input(
            "Contact Name",
            value=default_name,
            placeholder="Example: Brindavan Jewellers",
            label_visibility="collapsed",
            key=name_key
        )

    with name_col2:

        name_audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key=f"name_voice_{st.session_state.scan_id}"
        )

    if name_audio:

        try:

            spoken_name = transcribe_voice(
                name_audio["bytes"]
            )

            if spoken_name:

                st.session_state.voice_name = (
                    spoken_name
                )

                st.success(
                    "🎙️ Contact name captured."
                )

                st.rerun()

        except Exception as error:

            st.error(
                "❌ Voice recognition failed: "
                + str(error)
            )


    # =====================================================
    # ORGANIZATION
    # =====================================================

    st.markdown(
        "#### 🏢 Organization"
    )

    organization_col1, organization_col2 = st.columns(
        [6, 1]
    )

    organization_key = (
        f"organization_{st.session_state.scan_id}"
    )

    default_organization = (
        st.session_state.voice_organization
        or contact.get("organization")
        or ""
    )

    with organization_col1:

        edited_organization = st.text_input(
            "Organization",
            value=default_organization,
            label_visibility="collapsed",
            key=organization_key
        )

    with organization_col2:

        organization_audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key=(
                f"organization_voice_"
                f"{st.session_state.scan_id}"
            )
        )

    if organization_audio:

        try:

            spoken_organization = transcribe_voice(
                organization_audio["bytes"]
            )

            if spoken_organization:

                st.session_state.voice_organization = (
                    spoken_organization
                )

                st.success(
                    "🎙️ Organization captured."
                )

                st.rerun()

        except Exception as error:

            st.error(
                "❌ Voice recognition failed: "
                + str(error)
            )


    # =====================================================
    # DESIGNATION
    # =====================================================

    st.markdown("#### 💼 Designation")

    designation_col1, designation_col2 = st.columns([6, 1])

    designation_key = f"designation_{st.session_state.scan_id}"

    default_designation = (
        st.session_state.voice_designation
        or contact.get("designation")
        or ""
    )

    with designation_col1:
        edited_designation = st.text_input(
            "Designation",
            value=default_designation,
            placeholder="Example: Software Engineer",
            label_visibility="collapsed",
            key=designation_key
        )

    with designation_col2:
        designation_audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key=f"designation_voice_{st.session_state.scan_id}"
        )

    if designation_audio:
        try:
            spoken_designation = transcribe_voice(
                designation_audio["bytes"]
            )

            if spoken_designation:
                st.session_state.voice_designation = spoken_designation
                st.success("🎙️ Designation captured.")
                st.rerun()

        except Exception as error:
            st.error("❌ Voice recognition failed: " + str(error))

    # =====================================================
    # PHONE NUMBERS
    # =====================================================

    st.markdown(
        "#### 📞 Phone Numbers"
    )

    phone_col1, phone_col2 = st.columns(
        [6, 1]
    )

    phone_key = (
        f"phones_{st.session_state.scan_id}"
    )

    default_phones = (
        st.session_state.voice_phones
        or ", ".join(
            contact.get(
                "phone_numbers",
                []
            )
        )
    )

    with phone_col1:

        edited_phones = st.text_input(
            "Phone Numbers",
            value=default_phones,
            label_visibility="collapsed",
            key=phone_key
        )

    with phone_col2:

        phone_audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key=(
                f"phones_voice_"
                f"{st.session_state.scan_id}"
            )
        )

    if phone_audio:

        try:

            spoken_phone_text = transcribe_voice(
                phone_audio["bytes"]
            )

            spoken_phones = (
                convert_spoken_phone_numbers(
                    spoken_phone_text
                )
            )

            if spoken_phones:

                st.session_state.voice_phones = (
                    ", ".join(spoken_phones)
                )

                st.success(
                    "🎙️ Phone number captured."
                )

                st.rerun()

            else:

                st.warning(
                    "⚠️ Could not recognize a valid "
                    "10-digit phone number."
                )

        except Exception as error:

            st.error(
                "❌ Voice recognition failed: "
                + str(error)
            )


    # =====================================================
    # EMAIL
    # =====================================================

    st.markdown(
        "#### 📧 Email"
    )

    email_col1, email_col2 = st.columns(
        [6, 1]
    )

    email_key = (
        f"email_{st.session_state.scan_id}"
    )

    default_email = (
        st.session_state.voice_email
        or contact.get("email")
        or ""
    )

    with email_col1:

        edited_email = st.text_input(
            "Email",
            value=default_email,
            label_visibility="collapsed",
            key=email_key
        )

    with email_col2:

        email_audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key=(
                f"email_voice_"
                f"{st.session_state.scan_id}"
            )
        )

    if email_audio:

        try:

            spoken_email = transcribe_voice(
                email_audio["bytes"]
            )

            spoken_email = (
                convert_spoken_email(
                    spoken_email
                )
            )

            if spoken_email:

                st.session_state.voice_email = (
                    spoken_email
                )

                st.success(
                    "🎙️ Email captured."
                )

                st.rerun()

        except Exception as error:

            st.error(
                "❌ Voice recognition failed: "
                + str(error)
            )


    # =====================================================
    # WEBSITE
    # =====================================================

    st.markdown(
        "#### 🌐 Website / Social Media"
    )

    website_col1, website_col2 = st.columns(
        [6, 1]
    )

    website_key = (
        f"website_{st.session_state.scan_id}"
    )

    default_website = (
        st.session_state.voice_website
        or contact.get("website")
        or ""
    )

    with website_col1:

        edited_website = st.text_input(
            "Website / Social Media",
            value=default_website,
            label_visibility="collapsed",
            key=website_key
        )

    with website_col2:

        website_audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key=(
                f"website_voice_"
                f"{st.session_state.scan_id}"
            )
        )

    if website_audio:

        try:

            spoken_website = transcribe_voice(
                website_audio["bytes"]
            )

            spoken_website = (
                convert_spoken_website(
                    spoken_website
                )
            )

            if spoken_website:

                st.session_state.voice_website = (
                    spoken_website
                )

                st.success(
                    "🎙️ Website captured."
                )

                st.rerun()

        except Exception as error:

            st.error(
                "❌ Voice recognition failed: "
                + str(error)
            )


    # =====================================================
    # ADDRESS
    # =====================================================

    st.markdown(
        "#### 📍 Address"
    )

    address_col1, address_col2 = st.columns(
        [6, 1]
    )

    address_key = (
        f"address_{st.session_state.scan_id}"
    )

    default_address = (
        st.session_state.voice_address
        or contact.get("address")
        or ""
    )

    with address_col1:

        edited_address = st.text_area(
            "Address",
            value=default_address,
            label_visibility="collapsed",
            key=address_key
        )

    with address_col2:

        address_audio = mic_recorder(
            start_prompt="🎙️",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key=(
                f"address_voice_"
                f"{st.session_state.scan_id}"
            )
        )

    if address_audio:

        try:

            spoken_address = transcribe_voice(
                address_audio["bytes"]
            )

            if spoken_address:

                st.session_state.voice_address = (
                    spoken_address
                )

                st.success(
                    "🎙️ Address captured."
                )

                st.rerun()

        except Exception as error:

            st.error(
                "❌ Voice recognition failed: "
                + str(error)
            )


    # =====================================================
    # CONFIRM & SAVE
    # =====================================================

    st.divider()

    if st.button(
        "💾 Confirm & Save Contact",
        type="primary",
        use_container_width=True
    ):

        # =================================================
        # NAME CHECK
        # =================================================

        if not edited_name.strip():

            st.error(
                "❌ Please enter a name for this contact."
            )

            st.stop()


        # =================================================
        # PROCESS PHONE NUMBERS
        # =================================================

        final_phones = []

        for phone in edited_phones.split(","):

            normalized = normalize_phone(
                phone
            )

            if normalized:

                if normalized not in final_phones:

                    final_phones.append(
                        normalized
                    )


        # =================================================
        # CREATE FINAL CONTACT
        # =================================================

        final_contact = create_contact(

            name=edited_name.strip(),

            organization=(
                edited_organization.strip()
                or None
            ),

            designation=(
                edited_designation.strip()
                or None
            ),

            phone_numbers=final_phones,

            email=(
                edited_email.strip()
                or None
            ),

            website=(
                edited_website.strip()
                or None
            ),

            address=(
                edited_address.strip()
                or None
            ),

            source=(
                "camera+voice"
                if (
                    st.session_state.voice_name
                    or st.session_state.voice_organization
                    or st.session_state.voice_designation
                    or st.session_state.voice_phones
                    or st.session_state.voice_email
                    or st.session_state.voice_website
                    or st.session_state.voice_address
                )
                else "camera"
            ),

            confidence=1.0,

            context=None
        )


        # =================================================
        # FINAL VALIDATION
        # =================================================

        final_contact = validate_contact(
            final_contact
        )


        if not final_contact.get(
            "name"
        ):

            st.error(
                "❌ Please enter a valid contact name."
            )

            st.stop()


        if not final_contact.get(
            "phone_numbers"
        ):

            st.error(
                "❌ Please enter at least one valid "
                "10-digit phone number."
            )

            st.stop()


        # =================================================
        # FINAL CONTEXT CLASSIFICATION
        # =================================================

        (
            final_context,
            final_business_score,
            final_personal_score
        ) = classify_context(
            final_contact
        )

        final_contact["context"] = final_context


        # =================================================
        # CONTEXT DISPLAY
        # =================================================

        st.subheader(
            "🧠 Context Classification"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Business Score",
                final_business_score
            )

        with col2:

            st.metric(
                "Personal Score",
                final_personal_score
            )

        st.write(
            "**Detected Context:** "
            + final_context
        )


        # =================================================
        # DUPLICATE DETECTION
        # =================================================

        st.subheader(
            "🔍 Duplicate Detection"
        )

        duplicate_result = (
            update_or_create_contact(
                final_contact
            )
        )


        if (
            duplicate_result["action"]
            == "updated"
        ):

            st.warning(
                "⚠️ Duplicate contact detected."
            )

            st.write(
                "**Action:** Existing contact updated"
            )

            st.write(
                "**Existing Contact ID:** "
                + str(
                    duplicate_result[
                        "contact_id"
                    ]
                )
            )

            st.write(
                "**Similarity Score:** "
                + str(
                    duplicate_result[
                        "score"
                    ]
                )
            )

            if duplicate_result.get(
                "reasons"
            ):

                st.write(
                    "**Matching fields:**"
                )

                for reason in (
                    duplicate_result[
                        "reasons"
                    ]
                ):

                    st.write(
                        f"- {reason}"
                    )


        else:

            st.success(
                "🆕 New contact created."
            )

            st.write(
                "**New Contact ID:** "
                + str(
                    duplicate_result[
                        "contact_id"
                    ]
                )
            )


        # =================================================
        # VCF
        # =================================================

        st.subheader(
            "📱 Digital Contact"
        )

        vcf_file = create_vcf(
            final_contact
        )

        st.session_state.vcf_file = (
            vcf_file
        )

        st.session_state.save_completed = True

        st.success(
            "✅ Digital contact created successfully!"
        )


# =========================================================
# DOWNLOAD VCF
# =========================================================

if (
    st.session_state.save_completed
    and st.session_state.vcf_file
):

    vcf_file = st.session_state.vcf_file

    if os.path.exists(vcf_file):

        with open(
            vcf_file,
            "rb"
        ) as file:

            st.download_button(
                label="📥 Save Contact",
                data=file,
                file_name=os.path.basename(
                    vcf_file
                ),
                mime="text/vcard",
                use_container_width=True
            )