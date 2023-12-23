# request的主體(Request Body)

- 當使用者透過browser的表單送出的資料,就是儲存在Request body
- 使用者送給browser送給fastAPI,稱為Request Body
- fastAPI送給client(browser)的程為Response Body
- Response Body一定要有,Request Body不一定要有(如GET)
- POST,PUT,PATCH,DELETE,需要Request Body
- #### 使用fastAPI,定義Request Body最好的是使用 **Pydantic**

## 使用 Pydantic 的 BaseModel

```
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price:float
    tax:float | None = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    return item
```  