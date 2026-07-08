# 08. Pydantic 與 FastAPI 整合實務

本章節介紹如何將 **Pydantic V2** 的進階功能與 **FastAPI** 深度整合。我們將透過解析「學生分數 CSV」、「空氣品質 JSON」、「空氣品質 CSV」與「個股日成交 CSV」等實務髒資料清理與結構化對照案例，學習如何設計高效能、型別安全且符合 OpenAPI 規格的 Web API。

---

## 🚀 學習目標

1. **別名對照與英文化 (`validation_alias`)**：了解如何以中文/不規則欄位進行輸入驗證，並在回傳 API 回應時標準化為符合 PEP 8 的英文 `snake_case` 屬性。
2. **計算欄位自動序列化 (`@computed_field`)**：學會如何將 Model 中的 `@property` 計算屬性自動包含在 API 的 JSON 輸出中。
3. **前置資料清洗 (`@field_validator(mode='before')`)**：掌握在型別校驗前攔截空字串等髒資料並將其合理化的技術。
4. **複用自訂型別 (`typing.Annotated` + `BeforeValidator`)**：學會將繁瑣的清理邏輯（如移除千分位逗號）抽離並宣告為全域自訂型別。
5. **非阻塞執行緒管理 (同步 `def` 路由的藝術)**：深入理解為何讀取伺服器本地檔案（Disk I/O）時應使用 `def` 而非 `async def`，以及 FastAPI 如何透過 Thread Pool 避免主 Event Loop 被阻塞。
6. **例外處理與 HTTP 狀態碼**：結合 `raise HTTPException` 回傳明確且符合語意規律的錯誤 (如 `404`, `422`, `500`)。

---

## 📖 核心觀念解析

### 1. 別名與輸出英文化 (`validation_alias` & `populate_by_name`)

在實務中，資料源（如 CSV、外部 API）的欄位可能是中文（例如 `姓名`, `科目1`）或不規則格式（例如 `pm2.5`）。但在 Python 代碼和我們自己對外的 API 設計中，應該遵循 PEP 8 命名規範並提供標準的英文欄位。

* **`validation_alias`**：指定僅在**輸入驗證 (Deserialization)** 時對應的欄位名稱。
* **`ConfigDict(populate_by_name=True)`**：允許在手動初始化 Model 時，同時使用變數名 (如 `chinese`) 或別名 (如 `科目1`)，提升單元測試與彈性。

```python
from pydantic import BaseModel, Field, ConfigDict

class Student(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(validation_alias="姓名")
    chinese: int = Field(validation_alias="科目1")
```

### 2. 動態計算欄位序列化 (`@computed_field`)

原生的 Python `@property`（屬性方法）在 model 被轉為 JSON 時**不會**包含在輸出中。
Pydantic V2 提供了 `@computed_field` 裝飾器，只要加在 `@property` 上方，FastAPI 輸出 JSON 回應時便會自動將其序列化輸出：

```python
from pydantic import BaseModel, computed_field

class Student(BaseModel):
    chinese: int
    english: int

    @computed_field
    @property
    def total_score(self) -> int:
        return self.chinese + self.english
```

### 3. 前置驗證清洗 (`@field_validator(mode='before')`)

當外部資料某個欄位可能為空字串 `""`，但定義型別是 `float` 時，直接進行驗證會拋出轉型失敗錯誤。
設定 `mode='before'` 裝飾器可在 Pydantic 進行型別轉換**之前**，先對原始輸入資料進行預處理：

```python
from pydantic import BaseModel, field_validator

class SiteAQI(BaseModel):
    pm25: float

    @field_validator("pm25", mode='before')
    @classmethod
    def whitespace_to_zero(cls, value):
        if value == '':
            return '0.0'  # 轉為可成功解析為 float 的字串
        return value
```

### 4. 複用自訂清洗型別 (`Annotated` + `BeforeValidator`)

當多個欄位都需要相同的清洗邏輯（如個股成交資訊中的「成交量」、「成交金額」都有千分位逗號），如果對每個欄位都寫一個 `@field_validator` 會導致代碼極其冗長。
我們可以使用 `typing.Annotated` 與 `BeforeValidator` 封裝清洗邏輯，建立可重複使用的型別：

```python
from typing import Annotated
from pydantic import BeforeValidator

def _remove_commas(value: str | int) -> str | int:
    if isinstance(value, str):
        return value.replace(",", "")
    return value

# 宣告自訂清洗型別
CommaSeperatedInt = Annotated[int, BeforeValidator(_remove_commas)]

class StockInfo(BaseModel):
    trade_volume: CommaSeperatedInt  # 自動套用去除逗號後轉為整數的邏輯
    trade_value: CommaSeperatedInt
```

### 5. 同步 `def` 路由與 Event Loop 效能

在 FastAPI 中，路由的定義方式（`async def` 或 `def`）對伺服器整體吞吐量與回應速度有著決定性的影響。初學者常常會陷入「全部都寫 `async def`」的誤區。

#### 💡 運行機制對照圖：

```text
  【當請求進來時 (Request Incoming)】
             │
             ├─► [ 路由為 `async def` ] ──► 在「主事件循環 (Main Event Loop)」單一執行緒中直接執行
             │                                 ⚠️ 警示：若內含磁碟讀寫 (open) 或 CPU 密集運算等阻塞操作，
             │                                         會直接卡死事件循環，使伺服器在此期間無法響應任何其他請求！
             │
             └─► [ 路由為 `def` ] ────────► 指派給「外部執行緒池 (Thread Pool)」平行執行
                                               ✅ 優點：阻塞操作（如讀取 CSV/JSON 檔案）在獨立執行緒運行，
                                                       不會影響主事件循環，伺服器依然能順暢接收其他請求！
```

* **`async def` 路由**：僅適用於**非阻塞 I/O** 的情境（例如：使用支援非同步的資料庫驅動如 `databases` 或 `motor`、或是呼叫 `httpx.AsyncClient()` 請求外部 API）。
* **同步 `def` 路由**：**只要您的 API 需要讀取伺服器本機的檔案（Disk I/O，如 `open()` 讀寫 CSV/JSON），或者要進行大量數據的清洗運算，請務必宣告為同步 `def`**。FastAPI 會妥善安排執行緒池來託管它，這是最安全的設計。

```python
# 正確示範：讀取本地 CSV 檔案，使用同步 def 路由
@app.get("/students/scores")
def get_student_scores():
    with open("學生分數.csv", encoding='utf-8-sig') as f:
        ...
```

---

## 💻 專案運行指令

請進入本章節目錄後啟動服務：

```bash
cd 08_Pydantic與FastAPI整合實務
uvicorn main:app --reload
```

啟動後，請於瀏覽器開啟互動式 API 文件進行測試與驗證：
* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🗂️ 實務案例端點說明

> [實際範例連結](https://github.com/roberthsu2003/python/blob/master/pydantic/README.md)

### 1. 學生分數 CSV 解析 (`GET /students/scores`)
* **重點**：讀取 `data/學生分數.csv`。對外 API 將中文科目欄位英文化（例如 `科目1` $\rightarrow$ `chinese`），並使用 `@computed_field` 自動計算總分 `total_score` 呈現於 JSON 回應中。

### 2. 空氣品質 JSON 解析 (`GET /aqi/json-records`)
* **重點**：解析 `data/空氣品質aqi.json` 的巢狀資料。使用 `mode='before'` 驗證器，將空字串 `""` 髒資料清洗為 `0.0`，防範型別轉換錯誤。

### 3. 空氣品質 CSV 解析 (`GET /aqi/csv-records`)
* **重點**：讀取並批次解析 `data/空氣品質aqi.csv`，與 JSON 格式進行對照練習，加深對結構化驗證的理解。

### 4. 個股日成交複雜資料清理 (`GET /stocks/records`)
* **重點**：讀取 `data/個股日成交資訊.csv`。使用 `Annotated` + `BeforeValidator` 自訂型別，一次性自動清除數值字串中的千分位逗號與特殊的 `X` 符號，完成高品質的資料清洗。
