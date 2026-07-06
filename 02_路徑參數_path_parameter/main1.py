from fastapi import FastAPI
from enum import Enum

class ModelName(str,Enum):
    '''
    下面3個是machine learning models名稱
    python3.4以後可以使用Enum
    '''
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name:ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name":model_name, "message":"Deep Learing FTW!"}
    if model_name.value  == "lenet":
        return {"model_name":model_name, "message":"LeCNN all the images"}
    return {"model_name":model_name, "message":"Have some residuals"}