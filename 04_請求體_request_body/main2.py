from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name:str
    desccription: str | None = None
    price:float
    tax:float

app = FastAPI()

@app.put("/items/{item_id}")
async def create_item(item_id:int, item:Item):    
    return {"itme_id":item_id, **item.model_dump()}

