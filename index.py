from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from mysql import connector
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import bcrypt


load_dotenv()

app = FastAPI()
mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")

conn = connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)

def get_db_connection():
    return connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )

class UserCredentials(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: UserCredentials):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM User WHERE name = %s", (data.username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(data.password.encode('utf-8'), user["pass"].encode('utf-8')):
            return {"message": "Login successful", "user": user}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/create_user")
def create_user(data: UserCredentials):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO User (name, pass, email) VALUES (%s, %s, %s)", (data.username, hashed_password.decode(), ""))
        conn.commit()
        return {"message": "User created"}
    except connector.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/load_data/{uid}",)
def load_data(uid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT entry,amount FROM entrys WHERE user_id = %s;", (uid,))
        entries = cursor.fetchall()
        return entries
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.post("/add_data/{uid}")
def add_data(uid: int, entry: str, amount: float):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entrys (user_id, entry, amount) VALUES (%s, %s, %s)", (uid,entry, amount))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/add_data_multiple/{uid}")
def add_data_multiple(uid,a):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for entry in a:
            cursor.execute("INSERT INTO entrys (user_id, entry, amount) VALUES (%s, %s, %s)", (uid,entry['entry'], entry['amount']))
        conn.commit()
        return {"message": "Data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/delet_data/{uid}")
def delet_data(uid,entry):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entrys WHERE user_id = %s AND entry = %s", (uid,entry))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/delete_user/{uid}")
def delete_user(uid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE id = %s", (uid,))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()