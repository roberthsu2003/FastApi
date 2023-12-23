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
