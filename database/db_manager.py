import sqlite3
import os

BASE_DIR = '/home/aditya/Desktop/anpr/database'
DB_PATH = os.path.join(BASE_DIR, 'anpr_system.db')

def connect_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles 
                        (id INTEGER PRIMARY KEY, plate_number TEXT UNIQUE, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS passes 
                        (id INTEGER PRIMARY KEY, vehicle_id INTEGER, pass_type TEXT, 
                         FOREIGN KEY(vehicle_id) REFERENCES vehicles(id))''')
    conn.commit()
    conn.close()

def add_test_data():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vehicles (plate_number, status) VALUES (?, ?)", ("UP32AX9344", "Active"))
        conn.commit()
        print("Test data inserted successfully!")
    except sqlite3.IntegrityError:
        print("Data already exists.")
    conn.close()

def check_vehicle_status(plate_number):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM vehicles WHERE plate_number = ?", (plate_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {"status": "REISSUE", "db_status": result[0]}
    else:
        return {"status": "NEW_ENTRY", "db_status": None}

def log_pass(plate_number, pass_type):
    conn = connect_db()
    cursor = conn.cursor()
    
    # 1. Pehle check karo kya vehicle exist karta hai
    cursor.execute("SELECT id FROM vehicles WHERE plate_number = ?", (plate_number,))
    row = cursor.fetchone()
    
    # 2. Agar nahi hai, toh auto-register karo (Dynamic Registration)
    if not row:
        cursor.execute("INSERT INTO vehicles (plate_number, status) VALUES (?, ?)", (plate_number, "Active"))
        conn.commit()
        vehicle_id = cursor.lastrowid # Abhi jo insert kiya, uski ID
    else:
        vehicle_id = row[0]
        
    # 3. Ab pass log karo
    cursor.execute("INSERT INTO passes (vehicle_id, pass_type) VALUES (?, ?)", (vehicle_id, pass_type))
    conn.commit()
    conn.close()
    print(f"✅ Logged {plate_number} to database.")

if __name__ == "__main__":
    test_plate = "UP32BA9999"
    print(f"Checking {test_plate}: {check_vehicle_status(test_plate)}")
