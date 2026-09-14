from difflib import SequenceMatcher

from database.database import (
    get_all_contacts,
    update_contact,
    insert_contact
)


def text_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0

    text1 = str(text1).lower().strip()
    text2 = str(text2).lower().strip()

    return SequenceMatcher(None, text1, text2).ratio()


def normalize_phone(phone):
    if not phone:
        return ""

    digits = "".join(
        character for character in str(phone)
        if character.isdigit()
    )

    return digits[-10:]


def phone_match(phone_list1, phone_list2):
    phones1 = {
        normalize_phone(phone)
        for phone in phone_list1
        if normalize_phone(phone)
    }

    phones2 = {
        normalize_phone(phone)
        for phone in phone_list2
        if normalize_phone(phone)
    }

    return bool(phones1.intersection(phones2))


def check_duplicate(new_contact):

    existing_contacts = get_all_contacts()

    best_match = None
    best_score = 0
    best_reasons = []

    for existing in existing_contacts:

        score = 0
        reasons = []

        # -----------------------------
        # PHONE MATCH
        # -----------------------------

        if phone_match(
            new_contact.get("phone_numbers", []),
            existing.get("phone_numbers", [])
        ):
            score += 60
            reasons.append("Phone number matched")

        # -----------------------------
        # EMAIL MATCH
        # -----------------------------

        new_email = new_contact.get("email")
        old_email = existing.get("email")

        if (
            new_email
            and old_email
            and new_email.lower().strip()
            == old_email.lower().strip()
        ):
            score += 25
            reasons.append("Email matched")

        # -----------------------------
        # ORGANIZATION MATCH
        # -----------------------------

        org_similarity = text_similarity(
            new_contact.get("organization"),
            existing.get("organization")
        )

        if org_similarity >= 0.85:
            score += 10
            reasons.append("Organization name matched")

        # -----------------------------
        # NAME MATCH
        # -----------------------------

        name_similarity = text_similarity(
            new_contact.get("name"),
            existing.get("name")
        )

        if name_similarity >= 0.85:
            score += 10
            reasons.append("Name matched")

        # -----------------------------
        # ADDRESS MATCH
        # -----------------------------

        address_similarity = text_similarity(
            new_contact.get("address"),
            existing.get("address")
        )

        if address_similarity >= 0.85:
            score += 5
            reasons.append("Address matched")

        # Maximum score = 100
        score = min(score, 100)

        if score >= 60 and score > best_score:

            best_match = existing
            best_score = score
            best_reasons = reasons

    if best_match:

        return {
            "is_duplicate": True,
            "existing_contact": best_match,
            "score": best_score,
            "reasons": best_reasons
        }

    return {
        "is_duplicate": False,
        "existing_contact": None,
        "score": 0,
        "reasons": []
    }


def merge_contacts(existing_contact, new_contact):

    merged = {}

    # --------------------------------
    # TEXT FIELDS
    # --------------------------------

    text_fields = [
        "name",
        "organization",
        "designation",
        "email",
        "website",
        "address",
        "context"
    ]

    for field in text_fields:

        new_value = new_contact.get(field)
        old_value = existing_contact.get(field)

        if new_value:
            merged[field] = new_value
        else:
            merged[field] = old_value

    # --------------------------------
    # PHONE NUMBERS
    # --------------------------------

    old_phones = existing_contact.get(
        "phone_numbers", []
    )

    new_phones = new_contact.get(
        "phone_numbers", []
    )

    merged_phones = []

    for phone in old_phones + new_phones:

        if phone and phone not in merged_phones:
            merged_phones.append(phone)

    merged["phone_numbers"] = merged_phones

    # --------------------------------
    # SOURCE
    # --------------------------------

    merged["source"] = new_contact.get(
        "source"
    ) or existing_contact.get("source")

    # --------------------------------
    # CONFIDENCE
    # --------------------------------

    merged["confidence"] = max(
        existing_contact.get("confidence", 0.0),
        new_contact.get("confidence", 0.0)
    )

    return merged


def update_or_create_contact(new_contact):

    result = check_duplicate(new_contact)

    if result["is_duplicate"]:

        existing_contact = result["existing_contact"]

        # Merge old + new information
        merged_contact = merge_contacts(
            existing_contact,
            new_contact
        )

        contact_id = existing_contact["id"]

        update_contact(
            contact_id,
            merged_contact
        )

        return {
            "action": "updated",
            "contact_id": contact_id,
            "score": result["score"],
            "reasons": result["reasons"]
        }

    else:

        contact_id = insert_contact(
            new_contact
        )

        return {
            "action": "created",
            "contact_id": contact_id,
            "score": 0,
            "reasons": []
        }


if __name__ == "__main__":

    print("\nDuplicate Detector Test")

    test_contact = {
        "name": "Rahul Kumar",
        "organization": "ABC Technologies",
        "designation": "software engineer",
        "phone_numbers": ["+919876543210"],
        "email": "rahul@gmail.com",
        "website": None,
        "address": None,
        "context": "Business Contact",
        "source": "voice",
        "confidence": 1.0
    }

    result = check_duplicate(test_contact)

    if result["is_duplicate"]:

        print("\nSTATUS: DUPLICATE")
        print(
            "Similarity Score:",
            result["score"]
        )

        print("\nReasons:")

        for reason in result["reasons"]:
            print("-", reason)

    else:

        print("\nSTATUS: NEW CONTACT")