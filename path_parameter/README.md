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






