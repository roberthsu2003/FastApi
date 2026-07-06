from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允許的跨域來源網域列表
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://example.com",
]

# 設定 CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 允許跨域的來源
    allow_credentials=True,           # 支援 cookie 與驗證憑證
    allow_methods=["*"],              # 允許所有 HTTP Method
    allow_headers=["*"],              # 允許所有 Headers
)

@app.get("/")
def read_root():
    return {"message": "CORS 設定成功，已被授權的網域可直接進行 fetch/axios 請求！"}
