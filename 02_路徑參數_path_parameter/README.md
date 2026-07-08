# 路徑參數 (Path Parameter)

## 💡 什麼是路徑參數？
在 RESTful API 設計中，**路徑參數 (Path Parameter)** 主要用於**定位特定的資源**（例如某個特定的使用者、商品或文章）。例如，當您想要獲取特定 ID 的使用者資料時，網址路徑會被設計為 `/users/{user_id}`，這裡的 `{user_id}` 就是路徑參數。

---

## 🛠️ 基本用法：將路徑參數對照為函式參數

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id":item_id}
    
#===============結果
curl -X 'GET' 'http://127.0.0.1:8000/items/foo'

{"item_id":"foo"}
    
```

- @app.get("/items/**{item_id}**") - 路徑參數
- async def read_item(**item_id**): - function 參數

### 將路徑參數傳換為限制型別的參數
- 利用typehint

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id:int):
    return {"item_id":item_id}
    
#===============結果
curl -X 'GET' 'http://127.0.0.1:8000/items/3'

{"item_id":3}  

#================結果
curl -X 'GET' 'http://127.0.0.1:8000/items/foo'

Input:"foo"
錯誤訊息:"Input should be a valid integer, unable to parse string as an integer"
```

> 注意 {"item_id":**3**} --> 3是int

### 順序
- 由上而下的順序，符合條件的先執行

```
from fastapi import FastAPI

app = FastAPI()
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "現在使用者"}

@app.get("/users/{user_id}")
async def read_item(user_id):
    return {"item_id":user_id}

#================結果
curl -X 'GET' 'http://127.0.0.1:8000/users/me'

{"user_id":"現在使用者"}
```

```
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{user_id}")
async def read_item(user_id):
    return {"item_id":user_id}

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "現在使用者"}

#================結果
curl -X 'GET' 'http://127.0.0.1:8000/users/me'

{"item_id":"me"}   

```

### 路徑參數預先設定限定值

```
from fastapi import FastAPI
from enum import Enum

class ModelName(str,Enum):
    '''
    下面3個是machine learning models名稱
    python3.4以後可以使用Enum
    '''
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name:ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name":model_name, "message":"Deep Learing FTW!"}
    if model_name.value  == "lenet":
        return {"model_name":model_name, "message":"LeCNN all the images"}
    return {"model_name":model_name, "message":"Have some residuals"}
    
#================結果
curl -X 'GET' 'http://127.0.0.1:8000/models/alexnet'

{"model_name":"alexnet","message":"Deep Learing FTW!"}

#================結果
curl -X 'GET' 'http://127.0.0.1:8000/models/lenet'

{"model_name":"lenet","message":"LeCNN all the images"}

#================結果
curl -X 'GET' 'http://127.0.0.1:8000/models/resnet'

{"model_name":"resnet","message":"Have some residuals"}

#================結果

curl -X 'GET' 'http://127.0.0.1:8000/models/abc' 

錯誤訊息:
"msg":"Input should be 'alexnet', 'resnet' or 'lenet'"    

```

---

## 🛡️ 路徑參數的進階驗證與元數據 (`Path`)

除了型別限制（如 `int`），FastAPI 還允許我們使用 `Path` 來針對路徑參數進行更嚴格的數值或字串限制，並直接在自動產生的 API 文件中呈現這些約束。

### 範例：限制 ID 必須大於 0

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., title="商品的 ID 識別碼", description="此 ID 必須是大於 0 的整數", gt=0)
):
    return {"item_id": item_id}
```

### 說明：
* **`...`**：代表此參數是**必填項目**（因為是路徑的一部分，路徑參數本來就不可省略）。
* **`title` 與 `description`**：會自動呈現在 Swagger UI 中，作為 API 的使用說明。
* **`gt=0` (Greater Than)**：限制傳入的值必須大於 0。若使用者嘗試讀取 `/items/0`，FastAPI 會直接回傳 `422 Unprocessable Entity` 並給出詳細錯誤說明，保護後端不受非法請求侵害。

### 常見的數值限制條件：
* `gt`：大於 (Greater Than)
* `ge`：大於等於 (Greater Than or Equal to)
* `lt`：小於 (Less Than)
* `le`：小於等於 (Less Than or Equal to)
