import sqlite3


DB_PATH = "database/contacts.db"


# --------------------------------------------------
# CREATE TABLE
# --------------------------------------------------

def create_table():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            organization TEXT,
            designation TEXT,
            phone_numbers TEXT,
            email TEXT,
            website TEXT,
            address TEXT,
            context TEXT,
            source TEXT,
            confidence REAL
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# INSERT CONTACT
# --------------------------------------------------

def insert_contact(contact):

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    phone_numbers = ",".join(
        contact.get("phone_numbers", [])
    )

    cursor.execute("""
        INSERT INTO contacts
        (
            name,
            organization,
            designation,
            phone_numbers,
            email,
            website,
            address,
            context,
            source,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        contact.get("name"),
        contact.get("organization"),
        contact.get("designation"),
        phone_numbers,
        contact.get("email"),
        contact.get("website"),
        contact.get("address"),
        contact.get("context"),
        contact.get("source"),
        contact.get("confidence", 0.0)
    ))

    connection.commit()

    contact_id = cursor.lastrowid

    connection.close()

    return contact_id


# --------------------------------------------------
# GET ALL CONTACTS
# --------------------------------------------------

def get_all_contacts():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM contacts")

    rows = cursor.fetchall()

    connection.close()

    contacts = []

    for row in rows:

        phone_numbers = []

        if row[4]:
            phone_numbers = row[4].split(",")

        contacts.append({
            "id": row[0],
            "name": row[1],
            "organization": row[2],
            "designation": row[3],
            "phone_numbers": phone_numbers,
            "email": row[5],
            "website": row[6],
            "address": row[7],
            "context": row[8],
            "source": row[9],
            "confidence": row[10]
        })

    return contacts


# --------------------------------------------------
# GET CONTACT BY ID
# --------------------------------------------------

def get_contact_by_id(contact_id):

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM contacts WHERE id = ?",
        (contact_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    phone_numbers = []

    if row[4]:
        phone_numbers = row[4].split(",")

    return {
        "id": row[0],
        "name": row[1],
        "organization": row[2],
        "designation": row[3],
        "phone_numbers": phone_numbers,
        "email": row[5],
        "website": row[6],
        "address": row[7],
        "context": row[8],
        "source": row[9],
        "confidence": row[10]
    }


# --------------------------------------------------
# UPDATE CONTACT
# --------------------------------------------------

def update_contact(contact_id, contact):

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    phone_numbers = ",".join(
        contact.get("phone_numbers", [])
    )

    cursor.execute("""
        UPDATE contacts
        SET
            name = ?,
            organization = ?,
            designation = ?,
            phone_numbers = ?,
            email = ?,
            website = ?,
            address = ?,
            context = ?,
            source = ?,
            confidence = ?
        WHERE id = ?
    """, (
        contact.get("name"),
        contact.get("organization"),
        contact.get("designation"),
        phone_numbers,
        contact.get("email"),
        contact.get("website"),
        contact.get("address"),
        contact.get("context"),
        contact.get("source"),
        contact.get("confidence", 0.0),
        contact_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


# --------------------------------------------------
# DATABASE TEST
# --------------------------------------------------

if __name__ == "__main__":

    create_table()

    print("Contacts table created successfully.")