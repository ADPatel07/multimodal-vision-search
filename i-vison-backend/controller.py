from fastapi import FastAPI, File, UploadFile, Form, Body, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import io

from gemma3 import *
import uuid
from milvusdb import *


app = FastAPI()

origins = ["http://localhost:4200", "http://192.168.181.141:4200"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def read_img(raw_image):
    image_byte = await raw_image.read()
    return Image.open(io.BytesIO(image_byte))

cetagories_only_object = ["face", "food", "plant", "book"]

@app.post("/get/objects/")
async def getAllObjects(raw_image:UploadFile = File(...), category:str = Form(...)):
    img = await read_img(raw_image)
    
    fileName = "Images/" + str(uuid.uuid4().int) + "." + img.format
    img.save(fileName)

    objects = getObjectsList(img, category) if category not in cetagories_only_object else [category]

    if(objects is None) : 
        raise HTTPException(
            status_code=404,
            detail=f"No Objects are found"
        )
    
    doSeg = category not in cetagories_only_object

    objectsList = getObjects(img, ". ".join(objects)+".", doSeg)        
    return JSONResponse(objectsList)

@app.post("/search/img/")
async def search_img(query = Body(...)):
    return JSONResponse(search(query))

@app.post("/get/info/")
async def get_info(imgObj = Body(...)):

    img = decode_base64_to_image(imgObj['image'])

    return JSONResponse(getMostReleventInfo(img, imgObj['class'], imgObj['category']))

@app.post("/add/image/")
async def add_new_image(data: dict = Body(...)):
    image_data = base64.b64decode(data['image'])
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    category = data['category']

    img_format = "JPEG" if img.format is None else img.format

    fileName = str(uuid.uuid4().int) + "." + img_format
    img.save("db_images/"+fileName)

    for obj in data['objects']:
        obj['org_img'] = fileName 
        obj['category'] = category
        add_images(obj)

    return JSONResponse(content={"message": "Added Successfully"})

@app.get("/images/{image_name}")
async def get_image(image_name: str):

    image_directory = "db_images"
    image_path = os.path.join(image_directory, image_name)
    
    if not os.path.exists(image_path):
        return {"error": "Image not found"}
    
    return FileResponse(image_path)