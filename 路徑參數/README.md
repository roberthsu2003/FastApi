# 路徑參數(Path Parameter)
### 將路徑參數變為function參數

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






