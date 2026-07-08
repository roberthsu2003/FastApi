# 詢問參數 (Query Parameter)

## 💡 什麼是詢問參數？與路徑參數有何不同？
* **路徑參數 (Path Parameter)**：主要用於**定位**特定的資源（例如：「我要找 ID 為 10 的商品」 $\rightarrow$ `/items/10`）。
* **詢問參數 (Query Parameter)**：主要用於**篩選、搜尋、排序或分頁**（例如：「搜尋包含字串 phone 的商品，並限制回傳 5 筆」 $\rightarrow$ `/items/?q=phone&limit=5`）。

在 FastAPI 中，當您宣告一個函式參數，且該參數**沒有出現在路由路徑定義中**時，FastAPI 會自動將其視為「詢問參數」。

---

## 🛠️ 基本用法

```
# 在 ? 之後以 key=value 帶入，並用 & 符號連結多個參數
http://127.0.0.1:8000/items/?skip=0&limit=10
```

### 範例1

```
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [
    {"item_name":"Foo"},
    {"item_name":"Bar"},
    {"item_name":"Baz"}
    ]

@app.get("/items/")
async def read_item(skip:int=0, limit:int=10):
    return fake_items_db[skip: skip+limit]
    




```

### 呼叫方式1

```
curl -X 'GET' 'http://127.0.0.1:8000/items/?skip=0&limit=10'

#==============結果
[{"item_name":"Foo"},{"item_name":"Bar"},{"item_name":"Baz"}]

```

### 呼叫方式2

```
curl -X 'GET' 'http://127.0.0.1:8000/items/'

#==============結果
[{"item_name":"Foo"},{"item_name":"Bar"},{"item_name":"Baz"}]
```

### 呼叫方式3

```
curl -X 'GET' 'http://127.0.0.1:8000/items/?limit=2' 
[{"item_name":"Foo"},{"item_name":"Bar"}]
```

---
### 設定可有可無的詢問參數(Optional Query Parameter)

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id:str, q:str | None = None):
    if q:
        return {'item_id': item_id, 'q':q}
    return {'item_id': item_id} 
```

> 注意 @app.get("/items/{item_id}") --> 後面沒有(/)斜線

> 呼叫要用 curl -X 'GET' 'http://127.0.0.1:8000/items/robert?q=nice'

> @app.get("/items/{item_id}/") --> 後面有(/)斜線

> 呼叫要用 curl -X 'GET' 'http://127.0.0.1:8000/items/robert/?q=nice'

### 呼叫1

```
curl -X 'GET' 'http://127.0.0.1:8000/items/robert?q=nice

{"item_id":"robert","q":"nice"}
```

### 呼叫2

```
curl -X 'GET' 'http://127.0.0.1:8000/items/robert

{"item_id":"robert"}
```

---
## 詢目參數的型別轉換
- 可以定義bool型別,將會自動轉換

### 範例:

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id:str, q:str | None = None, short:bool = False):
    item = {"item_id":item_id}
    if q:
        item.update({'q':q})
    if not short:
        item.update({'description': "This is an amazing item that has a long description"})
    return item
```

### 呼叫方法:

```
http://127.0.0.1:8000/items/foo?short=1
```

### or

```
http://127.0.0.1:8000/items/foo?short=True
```

### or

```
http://127.0.0.1:8000/items/foo?short=true
```

### or

```
http://127.0.0.1:8000/items/foo?short=on
```

### or

```
http://127.0.0.1:8000/items/foo?short=yes
```

---

## 多個路徑和詢問

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None, short: bool = False
):
    item = {"item_id":item_id, "owner_id": user_id}

    if q:
        item.update({"q":q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )    
    return item
```

---

## 一定要有的詢問參數

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/item/{item_id}")
async def read_user_item(item_id:str, needy:str):
    item = {"item_id":item_id, "needy":needy}
    return item
```

### 錯誤呼叫(一定要有的詢問參數)

```
http://127.0.0.1:8000/items/foo-item

#===================結果

錯誤
```

### 正確呼叫

```
http://127.0.0.1:8000/items/foo-item?needy=sooooneedy

#===================結果
{"item_id":"foo-item","needy":"sooooneedy"}
```

---

## 🛡️ 詢問參數的進階驗證與元數據 (`Query`)

與路徑參數類似，FastAPI 提供了 `Query` 類別，讓我們能夠對詢問參數設定預設值、字串長度限制，以及加入 Swagger 文件描述。

### 1. 限制字串長度與加入文件描述

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(
    q: str | None = Query(
        None, 
        min_length=3, 
        max_length=50, 
        title="搜尋關鍵字", 
        description="搜尋字串，最少需輸入 3 個字，最多 50 個字"
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

* **`min_length=3` & `max_length=50`**：使用者傳入的字串長度若不在此區間內（例如 `?q=a`），FastAPI 會自動攔截並回傳 `422 Unprocessable Entity` 錯誤。
* **`title` 與 `description`**：會自動呈現在 Swagger UI，方便 API 使用者閱讀。

### 2. 宣告必填的詢問參數 (並套用 Query 限制)

如果您希望某個參數是**必填**的，但又想使用 `Query` 的約束條件，可以將預設值設定為 `...` (Pydantic 的 Required 指示符)：

```python
@app.get("/items/required")
async def read_required_items(
    needy: str = Query(..., min_length=3, description="此參數為必填項目，且長度必須大於 3")
):
    return {"needy": needy}
```

### 3. 接收多值列表的詢問參數 (Query Parameter List)

若希望一個參數名稱能接收多個值（例如 `?q=foo&q=bar`），可將其型別宣告為 `list[str]`，並在 `Query` 中配置預設值：

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/multiple")
async def read_multiple_items(
    q: list[str] | None = Query(None, description="可以帶入多個 q 參數進行篩選")
):
    return {"q": q}
```

* **呼叫網址範例**：`http://127.0.0.1:8000/items/multiple?q=apple&q=banana`
* **回應結果**：`{"q": ["apple", "banana"]}`


