import os
from minio import Minio
from io import BytesIO

USE_MINIO = True  # switch to False for local dev
MINIO_CLIENT = Minio("127.0.0.1:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)

LOCAL_STORAGE = os.getcwd()

def put_obj(key: str, data: bytes):
    if USE_MINIO:
        MINIO_CLIENT.put_object("book-edit", key, BytesIO(data), length=len(data))
    else:
        path = os.path.join(LOCAL_STORAGE, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

def get_obj_url(key: str) -> str:
    if USE_MINIO:
        return MINIO_CLIENT.presigned_get_object("book-edit", key)
    else:
        return f"/local_results/{key}"
