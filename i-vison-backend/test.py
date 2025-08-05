import json
from gemma3 import *
from milvusdb import *

import uuid

cetagories_only_object = ["face", "food", "plant", "book"]

def getAllObjects(img, category):    
    fileName = "Images/" + str(uuid.uuid4().int) + "." + img.format
    img.save(fileName)

    objects = getObjectsList(img, category) if category not in cetagories_only_object else [category]

    if(objects is None) : 
        return None
    
    doSeg = category not in cetagories_only_object
    objectsList = getObjects(img, ". ".join(objects)+".", doSeg)        
    return objectsList if objectsList != "No Object detected" else None

def add_new_image(data):
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

    return "Added Successfully"

def add_new():

    category = "face"
    uploadData = {}

    for idx in range(55, 61):
        print(idx)
        img = Image.open(rf"E:\AKHIL\NFSU\Sam 4\Datasets\data\images\{idx}.jpg")

        objecs = getAllObjects(img, category)

        if(objecs is None):
            continue

        uploadData['category'] = category
        uploadData['image'] = encode_image_to_base64(img)
        uploadData['objects'] = []

        for obj in objecs :
            uploadData['objects'].append({
                "identity": "Yasmin Karachiwala",
                "object_img": obj['object'],
                "caption": "",
                "box":obj["box"]
            })

        print(add_new_image(uploadData))

add_new()