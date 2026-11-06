from fastapi import FastAPI

app = FastAPI(title="ARASH RAVEN HOST")


@app.get("/")
def home():
    return {"status": "ok", "name": "ARASH RAVEN HOST"}
