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

### 上面類似定義 JSON(object)或 python dict

```
{
    "name": "Foo",
    "description": "An optional description",
    "price": 45.2,
    "tax": 3.5
}
```

### description和tax是可有可無(Optional)
 
```
{
    "name": "Foo",
    "price": 45.2
}

```

### 參數使用Pydantic BaseMode,FastAPI自動做了下列動作:
#### 1. 讀取Request body當作json
#### 2. 轉換為對應的型別
#### 3. 驗證資料:
- 如果data不是合法的,將優雅失敗,並傳出明確的錯誤(422)
#### 4. 透過參數item,可以接收到資料
#### 5. 自動產生json的schema(架構)
#### 6. json的schema也會自動產生在swagger UI內

### 使用swaggerUI,查詢,測試,驗証

#### 查詢
![](./images/pic1.png)

#### 測試
![](./images/pic2.png)

#### 驗証
![](./images/pic3.png)

### 範例

```
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name:str
    desccription: str | None = None
    price:float
    tax:float

app = FastAPI()

@app.post("/items/")
async def create_item(item:Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({'price_with_tax':price_with_tax})
    
    return item_dict
```

#### 測試

![](./images/pic4.png)

#### 驗證

![](./images/pic5.png)


#### 測試

```
curl -X 'POST' \
  'http://127.0.0.1:8000/items/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "iphone手機",
  "desccription": "中古2年",
  "price": 23500,
  "tax": 1200
}'

#===========結果
{"name":"iphone手機","desccription":"中古2年","price":23500.0,"tax":1200.0,"price_with_tax":24700.0}
```

### Request Body + 路徑參數(path parameter)

```
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
```

![](./images/pic6.png)
![](./images/pic7.png)
### Request Body + 路徑參數(Path Parameter) + 詢問參數(Query Parameter)

```
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name:str
    desccription: str | None = None
    price:float
    tax:float

app = FastAPI()

@app.put("/items/{item_id}")
async def create_item(item_id:int, item:Item,q:str | None = None):
    result = {"item_id":item_id, **item.model_dump()}
    if q:
        result.update({"q":q})
    return result
```

---

## 🛡️ Pydantic `Field` 與 API 文件描述 (`description` & `examples`)

當我們定義 Request Body 的 Pydantic Model 時，我們可以使用 `Field` 類別來限制欄位長度、數值大小，並為每個屬性加入詳細的描述（`description`）與預設範例值（`examples`）。這能讓您的 API 規格極為清晰，並能自動在 Swagger UI 中呈現。

### 範例：使用 `Field` 強化 API 文件

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(
        ..., 
        title="商品名稱", 
        description="商品的名稱，必填字串", 
        examples=["經典復古背包"]
    )
    description: str | None = Field(
        None, 
        title="商品描述", 
        description="商品的詳細描述資訊，可為空", 
        examples=["採用防潑水防磨損材質，大容量雙層收納"]
    )
    price: float = Field(
        ..., 
        gt=0, 
        title="商品價格", 
        description="商品售價，必須大於 0 元", 
        examples=[1980.5]
    )
    tax: float | None = Field(
        None, 
        ge=0, 
        title="商品稅金", 
        description="商品產生的稅金，必須大於或等於 0 元", 
        examples=[99.0]
    )

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 說明：
* **`examples=[...]`**：在 Pydantic 中，我們可以傳入一個範例清單。這些值會自動成為 Swagger UI 中測試 JSON 的**預設模板**。當使用者點選 "Try it out" 時，可以直接發送帶有該範例的請求，無須手動填寫複雜的 JSON 物件！
* **`description`**：會在 Swagger 文件中的 Schema 區塊以備註形式呈現，讓前後端串接的開發人員迅速理解每個欄位的商業定義。
* **`gt=0` / `ge=0`**：我們能在 `Field` 內直接加入數值範圍約束，發揮強大的資料驗證功能。





