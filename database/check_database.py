from database.database import get_contact_by_id


contact = get_contact_by_id(1)

print("\nContact with ID 1:\n")
print(contact)