from fastapi import FastAPI

app = FastAPI()

@app.get("/authorize")
def authorize(client_id: str, redirect_uri: str, state: str):
    return {"client_id": client_id, "redirect_uri": redirect_uri, "state": state}