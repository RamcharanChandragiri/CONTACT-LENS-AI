def classify_context(contact):

    business_score = 0
    personal_score = 0

    # Combine all contact information into one text
    text_parts = [
        contact.get("name"),
        contact.get("organization"),
        contact.get("designation"),
        contact.get("email"),
        contact.get("website"),
        contact.get("address")
    ]

    text = " ".join(
        str(part) for part in text_parts
        if part
    ).lower()

    # Business-related keywords
    business_keywords = [
        "jeweller",
        "jewellers",
        "jewelry",
        "jewellery",
        "store",
        "shop",
        "enterprise",
        "enterprises",
        "solutions",
        "technologies",
        "technology",
        "company",
        "industries",
        "services",
        "traders",
        "restaurant",
        "hotel",
        "hospital",
        "clinic",
        "school",
        "college",
        "engineer",
        "developer",
        "manager",
        "director",
        "employee",
        "professor",
        "teacher",
        "doctor",
        "lawyer",
        "consultant",
        "analyst",
        "designer",
        "architect",
        "executive",
        "officer"
    ]

    # Personal-related keywords
    personal_keywords = [
        "father",
        "mother",
        "brother",
        "sister",
        "friend",
        "home",
        "personal"
    ]

    # Count business keywords
    for keyword in business_keywords:
        if keyword in text:
            business_score += 1

    # Count personal keywords
    for keyword in personal_keywords:
        if keyword in text:
            personal_score += 1

    # Multiple phone numbers often indicate a business contact
    phone_numbers = contact.get("phone_numbers", [])

    if len(phone_numbers) >= 2:
        business_score += 2

    # Address indicators
    address = contact.get("address")

    if address:
        address_keywords = [
            "plaza",
            "road",
            "street",
            "nagar",
            "colony",
            "building",
            "market",
            "hyderabad",
            "warangal"
        ]

        address_text = address.lower()

        for keyword in address_keywords:
            if keyword in address_text:
                business_score += 1

    # Website indicates possible business contact
    if contact.get("website"):
        business_score += 1

    # Email indicates a more complete contact
    if contact.get("email"):
        business_score += 1

    # Final classification
    if business_score > personal_score and business_score >= 2:
        context = "Business Contact"

    elif personal_score > business_score:
        context = "Personal Contact"

    else:
        context = "Unknown"

    return context, business_score, personal_score


if __name__ == "__main__":

    test_contact = {
        "name": "Rahul Kumar",
        "organization": "ABC Technologies",
        "designation": "software engineer",
        "phone_numbers": ["+919876543210"],
        "email": "rahul@gmail.com",
        "website": None,
        "address": None
    }

    context, business_score, personal_score = classify_context(
        test_contact
    )

    print("\n" + "=" * 40)
    print("       CONTEXT CLASSIFICATION")
    print("=" * 40)

    print(f"\nBusiness Score: {business_score}")
    print(f"Personal Score: {personal_score}")

    print("\nDetected Context:")
    print(context)

    print("\n" + "=" * 40)