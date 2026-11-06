import hashlib
import secrets
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ARASH RAVEN HOST")
DB = "data.db"


def db():
    con = sqlite3.connect(DB)
    con.execute(
        "CREATE TABLE IF NOT EXISTS users "
        "(username TEXT PRIMARY KEY, salt TEXT, hash TEXT, token TEXT)"
    )
    return con


def make_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 200000
    ).hex()


class Auth(BaseModel):
    username: str
    password: str


@app.get("/")
def home():
    return {"status": "ok", "name": "ARASH RAVEN HOST"}


@app.post("/register")
def register(a: Auth):
    if len(a.username) < 3 or len(a.password) < 6:
        raise HTTPException(400, "username min 3, password min 6")
    salt = secrets.token_hex(16)
    token = secrets.token_hex(32)
    con = db()
    try:
        con.execute(
            "INSERT INTO users VALUES (?,?,?,?)",
            (a.username, salt, make_hash(a.password, salt), token),
        )
        con.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "username taken")
    finally:
        con.close()
    return {"token": token}


@app.post("/login")
def login(a: Auth):
    con = db()
    row = con.execute(
        "SELECT salt, hash FROM users WHERE username=?", (a.username,)
    ).fetchone()
    if not row or not secrets.compare_digest(
        row[1], make_hash(a.password, row[0])
    ):
        con.close()
        raise HTTPException(401, "wrong username or password")
    token = secrets.token_hex(32)
    con.execute("UPDATE users SET token=? WHERE username=?", (token, a.username))
    con.commit()
    con.close()
    return {"token": token}

