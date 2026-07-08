# 跨來源資源共用 (CORS - Cross-Origin Resource Sharing)

當您開發前後端分離的專案時（例如：前端使用 React/Vue 運行在 `http://localhost:3000`，而 FastAPI 運行在 `http://localhost:8000`），前端發送 API 請求時會因為瀏覽器的安全策略而被攔截，這就是著名的 **CORS 跨來源限制**。

為了允許前端跨域存取 API，我們必須在 FastAPI 中配置 **CORS 中介軟體 (Middleware)**。

---

## 🛠️ 配置 CORS

FastAPI 提供了內建的 `CORSMiddleware` 來快速完成設定。

### 範例代碼

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 1. 定義允許跨域請求的來源來源列表 (Origins)
origins = [
    "http://localhost:3000",      # 允許前端 React 測試來源
    "https://myfrontend.com",     # 允許生產環境前端網域
]

# 2. 加入 CORSMiddleware 到應用程式中
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 允許的網域列表，若要全部允許可用 ["*"] (不建議於生產環境)
    allow_credentials=True,           # 允許傳遞 Cookie 或憑證
    allow_methods=["*"],              # 允許的 HTTP 方法 (GET, POST, PUT, DELETE 等)
    allow_headers=["*"],              # 允許的 Request Headers
)

@app.get("/")
def read_root():
    return {"message": "這個 API 支援 CORS 跨網域請求！"}
```

---

## ⚠️ 生產環境的安全建議
- **避免使用萬用字元 `"*"`**：在生產環境（Production）中，將 `allow_origins` 設定為 `["*"]` 會帶來安全性風險，應明確列出允許的前端域名。
- **認證與 Cookie**：如果開啟了 `allow_credentials=True`，則 `allow_origins` **不能**設定為 `["*"]`，必須指定具體的域名列表。

---

## 🖥️ 互動式本機 CORS 測試方法

本單元特別提供了一個極簡的互動式測試前端網頁：[index.html](./index.html)，供您在本機親自體驗瀏覽器阻擋與放行跨網域 API 的視覺化流程。

### 測試步驟：

1. **雙擊打開測試網頁**：直接在檔案總管/Finder 雙擊 [index.html](./index.html)，在瀏覽器中開啟它。由於這是一個本地的 HTML 檔案，它的來源（Origin）通常為 `null` 或以 `file://` 開頭，這會被視為獨立的來源。
2. **測試未配置 CORS 的狀況**：
   - 啟動一個尚未啟用 CORS 的 FastAPI 服務（例如執行第 1 章的 `main.py`）。
   - 在網頁輸入網址為 `http://127.0.0.1:8000`，點擊 **「發送 Fetch 請求」**。
   - 網頁會亮起紅色警告 **「連線失敗 (CORS 攔截)」**。開啟 F12 開發者工具，您能清楚看到紅色字型的跨網域安全性攔截提示。
3. **測試啟用 CORS 之後的狀況**：
   - 啟動配置了 `allow_origins=["*"]` 的 FastAPI 服務。
   - 再次點擊網頁上的按鈕，您會發現綠色燈號亮起 **「連線成功 (CORS 通過)」**，並且能順利印出從 API 獲取的 JSON 回應！

