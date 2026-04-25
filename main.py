from fastapi import FastAPI, Request, HTTPException, Query
from pydantic import BaseModel

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
app = FastAPI()

uri = "mongodb://localhost:27017"
client = MongoClient(uri, server_api=ServerApi('1'))

# test connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB successfully")
except Exception as e:
    print(e)

db = client["db_test"]
collection = db["employees"]

def convert(data):
    data["_id"] = str(data["_id"])
    return data
@app.get("/users")
def get_users():
    users = list(collection.find())
    return {"data": [convert(user) for user in users]}

@app.get("/user/{user_id}")
def fetch_user(user_id:int):
    user=collection.find_one({"userId":user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="data not found")
    return {"data":convert(user)}
    
@app.post("/user")
async def post_user(req: Request):
    jsonData = await req.json()
    result = collection.insert_one(jsonData)
    return {
        "message": "User created",
        "id": str(result.inserted_id)
    }

@app.put("/user/{user_id}")
async def update_user(user_id : int, req: Request):
    jsonData = await req.json()
    collection.update_one({"userId":user_id},{"$set": jsonData})
    result= collection.find_one({"userId": user_id})
    return {"message":"Updated successfully", "data":convert(result)}
    
@app.delete("/user/{user_id}")
def delete_user(user_id: int):
    result= collection.delete_one({"userId":user_id})
    if result.deleted_count==0:
        raise HTTPException(status_code=404, detail="User not found")
    return{"message":"user deleted successfully", "userId":user_id}
    
# class Item(BaseModel):
#     name: str
#     price: float
#     version: str
#     is_offer: bool | None = None


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.put("/items/{item_id}")
# def modify_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id, "item_price": item.price}

# @app.post("/item/")
# def create_item(item: Item):
#     return {"message": "Item created successfully","item":item}

# # @app.get("/headers/")
# # def read_headers(user_agent: str = Header(None)):
# #     if user_agent != "Chrome":
# #         raise HTTPException(status_code=400, detail="Invalid data")
# #     return {"User-Agent": user_agent}

# @app.get("/auth")
# def auth_validation(token: str=Header(...)):
#     if token!="abc12":
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return{"Token": token}

# # Multiple validation
# @app.get("/validations")
# def validation_q(q: int= Query(10,gt=0,lt=50), token :str= Header(...)):
#     if token!="aaa":
#         raise HTTPException(status_code=404, detail="Invalid data")
#     return{q:q}


# #task
# @app.get("/users/{id}")
# def task(id: int, page: int=Query(2,gt=0,lt=10), Token: str=Header(...)):
#     if Token!="secure12":
#         raise HTTPException(status_code=401, detail="Invalid Token")
#     return{"id":id, "page":page, "Token":Token}



#CRUD operation

class Employee(BaseModel):
    name: str
    id: int
    salary: float
    attend: bool |None=None
    
employees={}
    
# pOST
@app.post("/employee/")
def add_emolpyee(Emp: Employee):
    employees[Emp.id]=Emp
    return{"Emp_id":Emp.id, "Emp_name":Emp.name, "Emp_salary":Emp.salary}

#get
@app.get("/employee/{id}")
def read_employee(id: int):
    if id not in employees:
        return {"error":"Invalid data"}
    return employees[id]
    

#put
@app.put("/employee/{id}")
def update_emp(id: int, emp:Employee):
    if id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    employees[id]=emp
    return employees[id]
      