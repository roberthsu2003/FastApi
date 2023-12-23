from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{user_id}")
async def read_item(user_id):
    return {"item_id":user_id}

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "現在使用者"}