import torch
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection 
import io
import base64
import os
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
import numpy as np
from PIL import Image
from google import genai

from skimage.morphology import binary_closing, binary_dilation, remove_small_objects, remove_small_holes, disk

from dotenv import load_dotenv
load_dotenv()

def encode_image_to_base64(image: Image.Image) -> str:
    img_bytes = io.BytesIO()
    if(image.format is None) :
        image.save(img_bytes, format="PNG")
    else :
        image.save(img_bytes, format=image.format)  # Save as PNG (or JPEG)
    return base64.b64encode(img_bytes.getvalue()).decode("utf-8")

def decode_base64_to_image(base64_str: str) -> Image.Image:
    img_bytes = base64.b64decode(base64_str.encode("utf-8"))
    img = Image.open(io.BytesIO(img_bytes))
    return img

def getObjectsList(img_path, category):

    prompt = f"""List all unique objects visible in this image that belong to the {category} category. Use only object names, with no duplicates. Follow this exact format:
                object1, object2
                Example: cat, remote control
                Do not include quantities, descriptions, or any other information—only object names in the specified format.
                If no relevant objects are found, return only: None"""
    
    # response = ollama.chat(
    #     model='gemma3:12b',
    #     messages=[{
    #             'role': 'user',
    #             'content': prompt,
    #             'images': [img_path]
    #         }]
    #     )

    key = os.getenv("GOOGLE_API_KEY")

    client = genai.Client(api_key=key)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[img_path, prompt]
    )

    # return response.message.content.split(',')
    return list(set([obj.strip().lower() for obj in response.text.split(',')])) if response.text.strip() != """None""" else None

# def do_segment(image, box):

#     x1, y1, x2, y2 = box
    
#     with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
#         predictor.set_image(image)
#         masks, _, _ = predictor.predict(point_labels =[0], box=[[x1, y1, x2, y2]], multimask_output=False)

#     cutout = Image.new("RGB", image.size, (0, 0, 0))
#     cutout.paste(image, mask=Image.fromarray(masks[0].astype(np.uint8) * 255))
#     cutout = cutout.crop([x1, y1, x2, y2])
#     return cutout

def do_segment(image, box):
    x1, y1, x2, y2 = box
    x, y = (x1 + x2) / 2, (y1 + y2) / 2

    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
        predictor.set_image(np.array(image))
        masks, _, _ = predictor.predict(
            # point_coords=[[x, y]],
            point_labels=[0],
            box=[[x1, y1, x2, y2]],
            multimask_output=False
        )

    mask_bool = masks[0].astype(np.uint8).astype(bool)

    # --- CLEANING to KEEP FULL OBJECT and REMOVE GAPS ---

    mask_clean = binary_closing(mask_bool, disk(5))  # closes gaps, connects edges
    mask_clean = remove_small_holes(mask_clean, area_threshold=2000)
    mask_clean = remove_small_objects(mask_clean, min_size=30)
    mask_clean = binary_dilation(mask_clean, disk(2))

    mask_pil = Image.fromarray((mask_clean.astype(np.uint8)) * 255)

    # Apply to image
    cutout = Image.new("RGB", image.size, (0, 0, 0))
    cutout.paste(image, mask=mask_pil)
    cutout = cutout.crop([x1, y1, x2, y2])

    return cutout

def getObjects(img, objects, doSegment=True):

    objList = []

    inputs = processor(images=img, text= f"{objects}", return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    
    results = processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        box_threshold=0.36,
        text_threshold=0.3,
        target_sizes=[img.size[::-1]]
    )
    
    if(len(results[0]['labels']) < 1) :
        return "No Object detected"

    for idx, box in enumerate(results[0]['boxes'].tolist()) :
        segment = do_segment(img, box) if doSegment else img.crop(box)
        
        objList.append({'identity': str(results[0]['labels'][idx]),'box': box, 'object': encode_image_to_base64(segment)})
    
    return objList

# ===========================================================================================================================

model_id = "IDEA-Research/grounding-dino-base"
device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)

checkpoint = "../checkpoints/sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"

sam2 = build_sam2(model_cfg, checkpoint)
predictor = SAM2ImagePredictor(sam2)