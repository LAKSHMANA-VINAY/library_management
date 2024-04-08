from fastapi import FastAPI,Request
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from bson import ObjectId
from fastapi.responses import HTMLResponse
import bson.errors 
from pydantic import BaseModel
from pymongo import MongoClient

client=MongoClient("mongodb+srv://pradeepmajji42:Pradeep123@cluster0.mb8pytv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client.library_application
collection_name=db["library_app"]

class Student(BaseModel):
    regno:str
    phone:str
    book:str
    date:str
    status:bool


templates=Jinja2Templates(directory="templates")

app=FastAPI()

app.mount("/static",StaticFiles(directory="static",html=True),name="static")

@app.get("/",name="home")
def home(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})


@app.get("/book")
def book(request:Request):
    return templates.TemplateResponse("book.html",{"request":request})

@app.post("/book/details",response_class=HTMLResponse)
async def student_book(request:Request):
    data=await request.form()
    regno=data['regno'].upper()
    phone=data['phone']
    book=data['book']
    date=data['date']
    status=data['status']
    new_record=Student(regno=regno,phone=phone,book=book,date=date,status=status)
    print(new_record)
    _id=collection_name.insert_one(dict(new_record))
    todo=libraries_serializer(collection_name.find({"_id":ObjectId(_id.inserted_id)}))
    context = {"request": request, "todo": todo}
    return templates.TemplateResponse("book.html", context)

def library_serializer(student)->dict:
    return {
        "_id":str(student['_id']),
        "regno":student['regno'],
        "phone":student['phone'],
        "book":student['book'],
        "date":student['date'],
        "status":student['status']
    }


def libraries_serializer(students)->list:
    return [library_serializer(student) for student in students]


@app.get("/pending", response_class=HTMLResponse)
def pending(request: Request):
    details = libraries_serializer(collection_name.find())
    return templates.TemplateResponse("pending.html", {"request": request, "data": details})

@app.post("/search")
async def search(request:Request):
    data=await request.form()
    regno=data['regno'].upper()
    details=libraries_serializer(collection_name.find({"regno":regno}))
    return templates.TemplateResponse("base.html", {"request": request, "data": details})

@app.post("/delete")
async def delete(request: Request):
    data = await request.form()
    if '_id' in data and data['_id']:
        try:
            obj_id = ObjectId(data['_id'])
            collection_name.find_one_and_delete({"_id": obj_id})
            return templates.TemplateResponse("base.html", {"request": request}, status_code=200)
        except bson.errors.InvalidId:
            return templates.TemplateResponse("base.html", {"request": request}, status_code=400)
    else:
        return templates.TemplateResponse("base.html", {"request": request}, status_code=400)
