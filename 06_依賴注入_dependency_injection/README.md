# 依賴注入 (Dependency Injection - Depends)

在 FastAPI 中，**依賴注入 (Dependency Injection)** 是一個極為強大且核心的設計。它允許我們宣告路徑運算函式（Path Operator Function）所需要「依賴」的資源或邏輯，並由 FastAPI 自動在請求進來時解析並注入進去。

## 💡 為什麼需要依賴注入？
- **程式碼重用**：將重複的邏輯（如分頁參數處理、權限校驗）抽離出來。
- **解耦與測試**：方便在測試時替換不同的依賴實作（例如將真實資料庫替換成記憶體測試資料庫）。
- **自動化處理**：FastAPI 會自動幫我們解析依賴中的 Query 參數、Path 參數、Body 參數，並將結果傳入。

---

## 🛠️ 基本用法範例：分頁參數

### 1. 宣告依賴函式
我們定義一個普通的函式，用來解析並驗證分頁參數：

```python
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}
```

### 2. 在 API 中使用 `Depends` 進行注入

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    # commons 會自動接收到 common_parameters 函式回傳的 dict 結果
    return commons

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons
```

當使用者發送請求，例如 `GET /items/?q=book&skip=10&limit=5`：
1. FastAPI 會攔截請求，先執行 `common_parameters(q="book", skip=10, limit=5)`。
2. 將該函式的回傳值注入到 `read_items` 函式的 `commons` 參數中。
3. 自動在 Swagger UI 產生對應的 `q`、`skip` 與 `limit` 查詢欄位。

---

## 🔑 進階用法：資料庫連線管理

依賴注入的另一個重要用途是管理生命週期（例如資料庫連線），我們可以使用 `yield` 來確保連線在使用完畢後自動關閉：

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# 模擬資料庫連線的依賴
def get_db():
    db = "Database_Connection_Opened"
    try:
        # yield 前的代碼會在執行 API 邏輯前運行
        yield db
    finally:
        # yield 後的代碼（finally）會在 API 回傳 Response 後自動運行
        print("Database_Connection_Closed")

@app.get("/data")
def get_data(db: str = Depends(get_db)):
    return {"status": "Success", "database": db}
```
