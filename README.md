# FastApi
- ### 快速建立ＷebApi,符合Open API規格
- ### 支援python3.7以上,建議python3.10
- ### 先了解python type,pydantic

## 自動產生open api docs

- 使用瀏覽器直接測試和說明

### swager UI(/docs)

![](./images/pic1.png)

### Redoc(/redoc)

![](./images/pic2.png)

## 安裝

```python
pip install "fastapi[all]"
```

## 簡單測試

```python

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

```

- main:app 代表執行main.py 內app實體
- --reload: 開發模式時使用.程式內容更改時,重新起動.

```python
#執行
uvicorn main:app --reload
```

### 建立路徑運算子(path operator)

- #### 路徑

```
https://example.com/items/foo

路徑是
/items/foo
```

- #### 運算子

```

@app.get()
@app.post()
@app.put()
@app.delete()

```

- ### ㄧ般運用

￼```
POST: 建立資料
GET: 讀取資料
PUT: 更新資料
DELETE: 刪除資料￼
￼```

```
@app.get("/")

#使用get運算子
#使用＂/"路徑
``` 

### 建立路徑運算函式（path operator function)
￼

```
@app.get("/")
asyn def root():
	return {"message": "Hello World"}

#asyn def root():
- 也可以使用一般的function 
- def root():
- function 的名稱可以隨意自定名稱

# return {"message":"Hello World"}
- 可以return dict,list,pydantic
```

## Path Parameters(路徑參數)

```python

from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

```


