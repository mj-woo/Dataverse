from typing import Union, Annotated
from fastapi import FastAPI, Query
from pydantic import BaseModel 
# tip: if I want to check if pydantic is installed, type in the terminal: pip freeze | grep pydantic
from enum import Enum

app  = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None
    description: Union[str, None] = None
    tax: Union[float, None] = None

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/")
def read_root():
    return {"Hello":"World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q":q} # http://127.0.0.1:8000/items/5?q=minji

@app.put("/items/{item_id}")
def update_item(item_id: int, item:Item):
    return {"item_name":item.name, "item_id":item_id}

# Enum
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName): # parameter will be a member of Enum
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message":"Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message":"LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

# File Path
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}] # 이후 DB와 연결 필요
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10): # 앞에 것 몇 개 스킵할지
    return fake_items_db[skip:skip+limit]

# item_id and needy are both required parameters (query할 때)
# http://127.0.0.1:8000/items/foo-item?needy=sooooneedy
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

@app.post("/items/")
async def create_item(item:Item):
    item_dict = dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
# await는 async가 끝날 때까지 기다림 (원래 같았으면 async 함수를 신경 쓰지 않고 진행. CPU 많이 사용하게 될 경우 async 사용)

@app.put("/items/{item_id}")
async def create_items(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.get("/items/")
async def read_item(
    q: Annotated[
        str | None,
        Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
        ),
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

