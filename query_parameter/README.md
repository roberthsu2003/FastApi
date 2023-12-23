# 詢問參數(Query Parameter)
- 當定義一個function 的參數時,並沒有對應的路徑參數,將自動解析query parameter

```
#在?之後,key=value,使用&連結多個key=value
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

