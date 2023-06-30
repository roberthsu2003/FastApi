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











