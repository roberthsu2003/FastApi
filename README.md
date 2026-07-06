# FastApi
- ### 快速建立ＷebApi,符合Open API規格
- ### ASGI Framework/toolkit
- ### 支援python3.7以上,建議python3.10
- ### 先了解python typehint,pydantic
- ### 架構於starlette(ASGI Framework)上
- ### uvicorn ASGI web server implementation for Python.
- ### 安裝vscode套件[Thunder Client](https://www.thunderclient.com/)

### swager UI(/docs)

![](./images/pic1.png)

### Redoc(/redoc)

![](./images/pic2.png)

### 在server上執行的指令

```
$ uvicorn index:app --host 0.0.0.0 --port 80
```

## 1. [起手式](./01_起手式)
## 2. [路徑參數(Path Parameter)](./02_路徑參數_path_parameter)
## 3. [詢問參數(Query Parameter)](./03_詢問參數_query_parameter)
## 4. [Request Body](./04_請求體_request_body)
## 5. [實際案例](./05_實際案例)
