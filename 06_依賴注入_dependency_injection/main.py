from fastapi import FastAPI, Depends

app = FastAPI()

# 範例 1：共用參數依賴
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return {"message": "讀取商品列表", "params": commons}

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return {"message": "讀取使用者列表", "params": commons}

# 範例 2：利用 yield 模擬管理資源生命週期
def get_db():
    db_session = "Active_Database_Session"
    print("-> 建立資料庫連線")
    try:
        yield db_session
    finally:
        print("-> 關閉資料庫連線 (清理資源)")

@app.get("/db-query")
def query_database(db: str = Depends(get_db)):
    return {"status": "Success", "db_session": db}


# 範例 3：實務案例重構 — 結合 SQLite 資料庫依賴注入 (對照第 5 章)
import sqlite3
from datetime import datetime
from pydantic import BaseModel, Field

class SensorData(BaseModel):
    time: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d %H:%M:%S"))
    light: float = 0.0
    temperature: float = 0.0

# 建立實務資料庫連接依賴
def get_sqlite_conn():
    conn = sqlite3.connect("data.db")
    try:
        yield conn  # 將連線租借給 API 路由
    finally:
        conn.close()  # 回應發送後自動關閉，避免洩漏
        print("-> SQLite 連線已被 Depends 全自動安全關閉")

@app.post("/iot-di", status_code=201)
def upload_sensor_data_di(data: SensorData, conn: sqlite3.Connection = Depends(get_sqlite_conn)):
    # 1. 建立資料表
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS iot2(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        light REAL NOT NULL,
        temperature REAL NOT NULL
    );
    """)
    # 2. 寫入資料 (直接使用 conn，不操心關閉問題)
    cursor.execute("""
    INSERT INTO iot2(date, light, temperature)
    VALUES(?,?,?)
    """, (data.time, data.light, data.temperature))
    conn.commit()
    return {"message": "資料成功寫入 (DI 託管)", "inserted_data": data}

