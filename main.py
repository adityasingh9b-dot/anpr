from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import os

app = FastAPI()

# 1. FIX: Tumhare db_manager.py mein jo path tha, wahi yahan hona chahiye
DB_PATH = "/home/aditya/Desktop/anpr/database/anpr_system.db"

# Static files mount karna
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/api/latest")
async def get_latest_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 2. FIX: JOIN Query taaki vehicles aur passes dono ka data mile
        query = '''
            SELECT p.id, v.plate_number, p.pass_type 
            FROM passes p
            JOIN vehicles v ON p.vehicle_id = v.id
            ORDER BY p.id DESC LIMIT 5
        '''
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        
        return {"records": data}
    except Exception as e:
        return {"error": str(e)}
