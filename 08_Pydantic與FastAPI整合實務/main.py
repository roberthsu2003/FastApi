import csv
import os
from typing import Annotated
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator, BeforeValidator, computed_field, ConfigDict

app = FastAPI(
    title="Pydantic 與 FastAPI 整合實務",
    description="本章節展示如何將 Pydantic V2 的進階驗證、清洗、別名對照及計算欄位功能與 FastAPI 路由深度整合。",
    version="1.0.0"
)

# 取得目前檔案所在目錄，確保資料檔案路徑正確
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_CSV_PATH = os.path.join(CURRENT_DIR, "data", "學生分數.csv")
AQI_JSON_PATH = os.path.join(CURRENT_DIR, "data", "空氣品質aqi.json")
AQI_CSV_PATH = os.path.join(CURRENT_DIR, "data", "空氣品質aqi.csv")
STOCKS_CSV_PATH = os.path.join(CURRENT_DIR, "data", "個股日成交資訊.csv")


# ==========================================
# 案例 1：學生分數 CSV 解析 (別名對照、計算屬性、同步 I/O)
# ==========================================

class Student(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(validation_alias="姓名")
    chinese: int = Field(validation_alias="科目1")
    english: int = Field(validation_alias="科目2")
    math: int = Field(validation_alias="科目3")
    geography: int = Field(validation_alias="科目4")
    history: int = Field(validation_alias="科目5")
    social: int = Field(validation_alias="科目6")
    morality: int = Field(validation_alias="科目7")

    # 使用 Pydantic v2 的 @computed_field，將總分序列化輸出到 JSON
    @computed_field
    @property
    def total_score(self) -> int:
        return (
            self.chinese
            + self.english
            + self.math
            + self.geography
            + self.history
            + self.social
            + self.morality
        )

class ScoreResponse(BaseModel):
    success: bool = True
    count: int
    students: list[Student]

# 使用同步 def 路由處理阻塞的 Disk I/O，由 FastAPI 的執行緒池 (Thread Pool) 執行
@app.get(
    "/students/scores",
    response_model=ScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="讀取伺服器學生分數 CSV 並計算總分",
    tags=["學生分數"]
)
def get_student_scores():
    if not os.path.exists(STUDENTS_CSV_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伺服器上找不到 CSV 檔案: {STUDENTS_CSV_PATH}"
        )
    
    try:
        students_list = []
        with open(STUDENTS_CSV_PATH, encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader, start=1):
                try:
                    student = Student.model_validate(row)
                    students_list.append(student)
                except Exception as val_error:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"CSV 檔案第 {index} 行資料驗證錯誤: {str(val_error)}"
                    )
        return ScoreResponse(
            count=len(students_list),
            students=students_list
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"伺服器讀取或解析 CSV 時發生錯誤: {str(e)}"
        )


# ==========================================
# 案例 2：AQI 空氣品質 JSON 解析 (Before Validator、Nested Model)
# ==========================================

class SiteAQI(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    site_name: str = Field(validation_alias="sitename")
    county: str = Field(validation_alias="county")
    aqi: int
    status: str = Field(validation_alias="status")
    pm25: float = Field(validation_alias="pm2.5")

    # 前置驗證器：型別檢查前，將空字串清洗為 0.0，避免轉 float 失敗
    @field_validator("pm25", mode='before')
    @classmethod
    def whitespace_to_zero(cls, value):
        if value == '':
            return '0.0'
        return value

class RecordsResponse(BaseModel):
    success: bool = True
    count: int
    records: list[SiteAQI]

@app.get(
    "/aqi/json-records",
    response_model=RecordsResponse,
    status_code=status.HTTP_200_OK,
    summary="讀取與清洗伺服器預置 AQI JSON 檔案",
    tags=["空氣品質 AQI"]
)
def get_aqi_json_records():
    if not os.path.exists(AQI_JSON_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伺服器上找不到 JSON 檔案: {AQI_JSON_PATH}"
        )
    
    try:
        with open(AQI_JSON_PATH, mode='r', encoding='utf-8') as file:
            json_str = file.read()
            
        class RecordsParser(BaseModel):
            records: list[SiteAQI]
            
        parsed_data = RecordsParser.model_validate_json(json_str)
        return RecordsResponse(
            count=len(parsed_data.records),
            records=parsed_data.records
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"伺服器讀取或解析 JSON 時發生錯誤: {str(e)}"
        )


# ==========================================
# 案例 3：AQI 空氣品質 CSV 解析與驗證 (與 JSON 做對比)
# ==========================================

@app.get(
    "/aqi/csv-records",
    response_model=RecordsResponse,
    status_code=status.HTTP_200_OK,
    summary="讀取與清洗伺服器預置 AQI CSV 檔案",
    tags=["空氣品質 AQI"]
)
def get_aqi_csv_records():
    if not os.path.exists(AQI_CSV_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伺服器上找不到 CSV 檔案: {AQI_CSV_PATH}"
        )
    
    try:
        records_list = []
        with open(AQI_CSV_PATH, encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader, start=1):
                try:
                    record = SiteAQI.model_validate(row)
                    records_list.append(record)
                except Exception as val_error:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"CSV 檔案第 {index} 行資料驗證錯誤: {str(val_error)}"
                    )
        return RecordsResponse(
            count=len(records_list),
            records=records_list
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"伺服器讀取或解析 CSV 時發生錯誤: {str(e)}"
        )


# ==========================================
# 案例 4：個股日成交複雜資料清理 (Annotated 與 BeforeValidator 複用型別)
# ==========================================

# 定義複用資料清洗函式
def _prepare_comma_seperated_int_(value: str | int) -> str | int:
    if isinstance(value, str):
        return value.replace(",", "")
    return value

def _trim_float_(value: str) -> str:
    if isinstance(value, str):
        value = value.strip()
        value = value.lstrip('X')
        return value.strip()

# 定義複用清洗型別
CommaSeperatedInt = Annotated[int, BeforeValidator(_prepare_comma_seperated_int_)]
CommaSeperatedFloat = Annotated[float, BeforeValidator(_prepare_comma_seperated_int_)]
trimFloat = Annotated[float, BeforeValidator(_trim_float_)]

class StockInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    stock_id: str = Field(validation_alias="證券代號")
    name: str = Field(validation_alias="證券名稱")
    trade_volume: CommaSeperatedInt = Field(validation_alias="成交股數")
    trade_value: CommaSeperatedInt = Field(validation_alias="成交金額")
    open_price: CommaSeperatedFloat = Field(validation_alias="開盤價")
    high_price: CommaSeperatedFloat = Field(validation_alias="最高價")
    low_price: CommaSeperatedFloat = Field(validation_alias="最低價")
    close_price: CommaSeperatedFloat = Field(validation_alias="收盤價")
    price_change: trimFloat = Field(validation_alias="漲跌價差")
    transaction_count: CommaSeperatedInt = Field(validation_alias="成交筆數")

class StockResponse(BaseModel):
    success: bool = True
    count: int
    stocks: list[StockInfo]

@app.get(
    "/stocks/records",
    response_model=StockResponse,
    status_code=status.HTTP_200_OK,
    summary="讀取個股成交 CSV 檔案並套用 Annotated 與 BeforeValidator 自動清理資料",
    tags=["個股交易資訊"]
)
def get_stock_records():
    if not os.path.exists(STOCKS_CSV_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"伺服器上找不到指定的 CSV 檔案：{STOCKS_CSV_PATH}"
        )
    
    try:
        stocks_list = []
        with open(STOCKS_CSV_PATH, encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader, start=1):
                try:
                    stock = StockInfo.model_validate(row)
                    stocks_list.append(stock)
                except Exception as val_error:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"CSV 檔案第 {index} 行資料驗證清洗錯誤: {str(val_error)}"
                    )
        
        return StockResponse(
            count=len(stocks_list),
            stocks=stocks_list
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"伺服器讀取或解析 CSV 時發生錯誤: {str(e)}"
        )
