from typing import Union
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello":"World"}

#網址的呼叫為http://網址/item/5?q=45&g=weight
@app.get("/item/{item_id}")
def read_item(item_id: int,q: int | None = None,g:str | None = None):
    return {"item_id":item_id,
             "q":q,
             "g":g,
            }