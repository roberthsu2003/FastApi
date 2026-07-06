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

# 範例 2：利用 yield 管理資源生命週期
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
