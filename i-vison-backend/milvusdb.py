from PIL import Image
import io
import base64

from pymilvus import MilvusClient, DataType
from collections import defaultdict

from sentence_transformers import SentenceTransformer
from transformers import AutoImageProcessor, Dinov2Model

import torch

from google import genai

import warnings
warnings.filterwarnings("ignore")


def encode_image_to_base64(image: Image.Image) -> str:
    img_bytes = io.BytesIO()
    if(image.format is None) :
        image.save(img_bytes, format="PNG")
    else :
        image.save(img_bytes, format=image.format)  # Save as PNG (or JPEG)
    return base64.b64encode(img_bytes.getvalue()).decode("utf-8")

def decode_base64_to_image(base64_str: str) -> Image.Image:

    try:
        img_bytes = base64.b64decode(base64_str.encode("utf-8"))
        return Image.open(io.BytesIO(img_bytes))
    except:
        return None

def getCaption(image):

    image = decode_base64_to_image(image)

    prompt = f"""Write a crisp, vivid caption (2–3 lines) describing the object in the image. Your caption should flow naturally as one short paragraph (not broken into bullet points or options).

                Include:

                Name + Category (e.g., animal: golden retriever, furniture: mid-century armchair).

                Color/Pattern/Material (e.g., "sunset-orange feathers," "oak wood with linen upholstery").

                Key trait, action, or mood (e.g., "perched elegantly on a mossy branch," "exuding retro charm").

                Make it engaging and sensory. Capture what makes the object special or memorable. Do not format it as options or bullet points—write it as one seamless, vivid sentence or two.

                Examples for style:

                Animal: "A fluffy ginger cat napping in a sunbeam, tail twitching with dreamy paws."

                Bird: "Majestic snowy owl perched on a pine branch, golden eyes piercing the twilight."

                Food: "Steaming ramen bowl—silky noodles, soft eggs, and swirls of chili oil dancing together."

                Fashion: "Vintage leather boots, scuffed but proud, ready for another adventure on cobblestone streets."

                Nature: "Crimson maple leaf caught mid-fall, a fleeting moment of autumn's fiery grace."

                """

    key = "AIzaSyDrtspyK5B3mMaUExTPVcF-uRo35K8wcNA"

    client = genai.Client(api_key=key)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[image, prompt]
    )

    return response.text.strip()

def add_images(data):

    # data: object_img, box, original imag, identity, caption,
    obj = decode_base64_to_image(data['object_img'])
    identity = data.get('identity', '')
    category = data.get('category', '')
    description = data.get('caption', '')

    # text = f"Identity: {identity}, Category: {category}, Caption: {getCaption(obj, category)},  Description: {data.get('caption', '')}"
    # text = text.lower()

    data['img_vector'] = encode_image(obj)
    # data['text_vector'] = text_model.encode(text, convert_to_numpy=True, normalize_embeddings=True, device="cuda")

    data['text_vector'] = ( .4 * text_model.encode(identity, convert_to_numpy=True, normalize_embeddings=True, device="cuda") 
                            # + .4 * text_model.encode(getCaption(obj), convert_to_numpy=True, normalize_embeddings=True, device="cuda") 
                            + .1 * text_model.encode(category, convert_to_numpy=True, normalize_embeddings=True, device="cuda") 
                            + .5 * text_model.encode(description, convert_to_numpy=True, normalize_embeddings=True, device="cuda") )

    del data['object_img']

    client.insert(collection_name="image_collection", data=data)

    return "Added sucessfully"

def search(query_dict) : 

    obj = query_dict.get("object")
    text = query_dict.get("text")

    obj = decode_base64_to_image(obj) if obj is not None else None

    obj_vector = [encode_image(obj).tolist()] if obj is not None else None
    text_vector = [text_model.encode(text.lower(), convert_to_numpy=True, normalize_embeddings=True, device="cuda").tolist()] if text is not None and text else None

    search_params = {"metric_type": "COSINE", "params": {"ef": 100}}
    output_fields = ["org_img", "box", "identity", "caption", "img_vector"]
    results = []

    if(obj_vector) :
        obj_results = client.search(
            collection_name="image_collection",
            anns_field="img_vector", 
            search_params= search_params,
            data=obj_vector,
            limit=100,
            output_fields=output_fields
            )
        results.extend(obj_results[0])
        
    if(text_vector) :
        text_results = client.search(
            collection_name="image_collection",
            anns_field="text_vector", 
            search_params=search_params,
            data=text_vector,
            limit=100,
            output_fields=output_fields
            )
        results.extend(text_results[0])

    unique_results = {}
    
    for item in results:
        uid = item.get("id")
        distance = item.get("distance")

        if uid not in unique_results:
            if(text_vector and obj_vector) :
                unique_results[uid] = .5 * distance
            else :
                unique_results[uid] = item
        else:
            item["distance"] =  unique_results[uid] + .5 * distance
            unique_results[uid] = item

    sorted_unique_results = sorted([x for x in unique_results.values() if isinstance(x, dict)], key=lambda x: x.get("distance"))


    distance_threshold = .6 if (text_vector and obj_vector) or query_dict.get("category") == 'face' else .75

    return rerank_and_group_by_image(sorted_unique_results, distance_threshold)

def rerank_and_group_by_image(results, distance_threshold=0.6):
    grouped_by_image = defaultdict(list)

    for item in results:
        distance = item.get("distance")
        if distance is None or distance < distance_threshold:
            continue

        entity = item.get("entity", {})
        org_img = entity.pop("org_img", None)
        if org_img is None:
            continue

        entity["distance"] = round(distance, 2)
        grouped_by_image[org_img].append(entity)

    for org_img in grouped_by_image:
        grouped_by_image[org_img].sort(key=lambda x: x["distance"])

    return grouped_by_image

def getMostReleventInfo(image, className, category) : 
    normalized_vector = encode_image(image)

    results = client.search(
    collection_name="image_collection",
    anns_field="vector", 
    search_params={"metric_type": "COSINE", "params": {"ef": 100}},
    data=normalized_vector,
    filter=f"class == '{className}' and category == '{category}'",
    limit=1,
    output_fields=["org_img", "box", "identity", "caption"]
    )

    return results[0] if results else []


def removeIndex(collectionName, indexName):
    client.release_collection(collectionName)
    client.drop_index(collectionName, indexName)
    client.load_collection(collectionName)

def encode_image(image):
    inputs = image_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = image_model(**inputs)
    return torch.nn.functional.normalize(outputs.last_hidden_state[:, 0]).squeeze().cpu().numpy()

def main():
    global client
    client = MilvusClient(uri="http://localhost:19530")

    global text_model
    text_model = SentenceTransformer("BAAI/bge-m3", local_files_only=True)
    # text_model = SentenceTransformer("jinaai/jina-clip-v2", trust_remote_code=True)

    global image_processor
    image_processor = AutoImageProcessor.from_pretrained('facebook/webssl-dino300m-full2b-224')

    global image_model
    image_model = Dinov2Model.from_pretrained('facebook/webssl-dino300m-full2b-224')

    # client.drop_collection(collection_name="image_collection")

    if not client.has_collection(collection_name='image_collection'):

        index_params = MilvusClient.prepare_index_params()

        index_params.add_index(
            field_name="img_vector",
            metric_type="COSINE",
            index_type="HNSW",
            index_name="img_vector_index",
            params={
                "M": 64, # Maximum number of neighbors each node can connect to in the graph
                "efConstruction": 100 # Number of candidate neighbors considered for connection during index construction
            } 
        )

        index_params.add_index(
            field_name="text_vector",
            metric_type="COSINE",
            index_type="HNSW",
            index_name="text_vector_index",
            params={
                "M": 64, # Maximum number of neighbors each node can connect to in the graph
                "efConstruction": 100 # Number of candidate neighbors considered for connection during index construction
            } 
        )

        schema = MilvusClient.create_schema(enable_dynamic_field=True)

        schema.add_field( field_name="text_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field( field_name="img_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field( field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True,)

        client.create_collection(collection_name="image_collection", index_params=index_params, schema=schema)
        
        print("Collection has been Created .........")


    else :
        client.load_collection(collection_name='image_collection')

main()