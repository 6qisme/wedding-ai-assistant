import os 
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

# 從.env 載入環境變數
load_dotenv()

# 初始化FastAPI應用
app = FastAPI()

# 根路徑，用於健康檢查（Health Check）
@app.get("/")
def read_root():
    return {"Status": "OK"}

# 本地端運行使用
if __name__  == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)