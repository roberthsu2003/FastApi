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

## 🔑 進階用法：資料庫連線生命週期管理 (配合 yield)

在 Web 開發中，管理資料庫連線的開啟與關閉（Open/Close）是個非常頻繁且關鍵的任務。若我們在每個 Endpoint 都手動呼叫連線與關閉（如第 5 章的寫法），一旦 API 在執行中發生例外錯誤，就容易漏掉關閉動作，導致資料庫連線洩漏 (Connection Leak)。

FastAPI 的依賴注入支援使用 **`yield`** 關鍵字。這能讓我們以非常優雅的方式進行生命週期管理：
1. **`yield` 之前的代碼**：會在 API Endpoint 執行**之前**執行。
2. **`yield` 回傳的資源**：會被注入到 API Endpoint 的參數中供我們使用。
3. **`yield` 之後的代碼 (通常放置在 `finally` 區塊)**：會在 API 回傳回應 (Response) **之後**自動執行，保證資源一定會被回收關閉。

---

## 🛠️ 實務對照：手動管理 vs. 依賴注入 (DI) 重構

我們拿 **第 5 章的 IoT 感測器寫入案例** 來做對比：

### ❌ 舊方式：手動管理 (容易漏掉關閉)
```python
@app.post("/iot")
async def upload_iot_data(data: SensorData):
    conn = sqlite3.connect('data.db')  # 手動開啟
    try:
        insert_project(conn, (data.time, data.light, data.temperature))
    finally:
        conn.close()  # 必須在 finally 手動確保關閉
    return {"status": "Success"}
```

###  新方式：Depends 依賴注入 (全自動託管)
```python
import sqlite3
from fastapi import FastAPI, Depends

app = FastAPI()

# 1. 宣告資料庫連接依賴 (以 yield 管理生命週期)
def get_db():
    conn = sqlite3.connect("data.db")
    try:
        yield conn  # 將連線「借給」Endpoint 使用
    finally:
        conn.close()  # 當 API 回傳後，FastAPI 會自動回到這裡執行關閉
        print("-> 資料庫連線已安全關閉")

# 2. 在 Endpoint 中直接注入
@app.post("/iot")
async def upload_iot_data(data: SensorData, conn: sqlite3.Connection = Depends(get_db)):
    # 直接使用注入的 conn，完全不用操心開啟與關閉連線的邏輯！
    insert_project(conn, (data.time, data.light, data.temperature))
    return {"status": "Success"}
```

透過 `Depends(get_db)`，Endpoint 變得更加專注於業務邏輯（Business Logic），而資源的創建與銷毀則被完美地解耦抽離了！

