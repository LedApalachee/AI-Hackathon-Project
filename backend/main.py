import measure_plant as mp
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import uuid
import os
import zipfile
import shutil
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/segmented", StaticFiles(directory="segmented"), name="segmented")

model = YOLO("measure_plant.pt")

@app.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):

    # создаём уникальную папку
    folder_id = str(uuid.uuid4())
    extract_path = os.path.join("uploads", folder_id)
    os.makedirs(extract_path, exist_ok=True)

    temp_zip_path = f"{folder_id}.zip"

    # сохраняем zip
    with open(temp_zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # разархивируем
    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
   
    os.remove(temp_zip_path)

    # прогоняем через модель
    results = mp.measure_dir(model, f"uploads/{folder_id}", 9, f"segmented/{folder_id}")
    shutil.rmtree(f"uploads/{folder_id}") # удаляем полученные с фронтенда файлы

    # сохраняем измерения в виде текстовых файлов + формируем возврат на фронтенд
    to_frontend = []
    for res in results:
        leaves = []
        stems = []
        roots = []
        for obj in res["object_list"]:
            if obj["classname"] == "leaf":
                leaves += [obj["amount"]]
            elif obj["classname"] == "stem":
                stems += [obj["amount"]]
            else:
                roots += [obj["amount"]]
        
        result_str = ""
        if len(leaves) > 0:
            result_str += "Лист: " if len(leaves) == 1 else "Листья: "
            result_str += ", ".join(str(leaf) for leaf in leaves) + " мм2\n"
        if len(stems) > 0:
            result_str += "Стебль: " if len(stems) == 1 else "Стебли: "
            result_str += ", ".join(str(stem) for stem in stems) + " мм\n"
        if len(roots) > 0:
            result_str += "Корень: " if len(roots) == 1 else "Корни: "
            result_str += ", ".join(str(root) for root in roots) + " мм\n"
        
        txt_path = res["output_file"].split(".")[0] + ".txt"
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(result_str)
        
        to_frontend.append({
            "image_url": res["output_file"],
            "txt_url": txt_path
        })

    return {"results": to_frontend}
