from ultralytics import YOLO
import numpy as np
from skimage.morphology import skeletonize
import sys
import os


def measure_dir(model, images, px_per_mm, output_dir):
    results = model.predict(images, save=False)   # получаем объекты Results
    dir_files = os.listdir(images)
    output_files = []

    # сохраняем каждый результатный файл по указанному шаблону
    # с добавлением к пути файла порядкового номера i
    if output_dir:
        i = 0
        for r in results:
            output_file = output_dir + "/seg_" + dir_files[i]
            output_files.append(output_file)
            r.save(output_file)
            i += 1

    res = []
    file_i = 0
    for r in results:
        # список объектов с посчитанными длиной/площадью
        # поля объектов списка: classname, amount (результат замера), unit (единица измерения, str)
        objects = []

        # проходимcя по каждому обнаруженному объекту
        for i in range(len(r.boxes)):
            # достаем класс объекта и его маску
            classname = r.names[r.boxes.cls.int().tolist()[i]]
            amount = 0
            unit = ""
            mask = r.masks.data[i].cpu().numpy() # превращаем в ndarray

            # если это стебель или корень - считаем длину (скелетизируем -> суммируем пиксели -> делим на линейный масштаб)
            # а если это лист, то считаем его площадь (делим на квадратный масштаб)
            if classname == "stem" or classname == "root":
                len_px = int(skeletonize(mask).sum())
                amount = len_px / px_per_mm
                unit = "mm"
            else:
                area_px = int(np.sum(mask))
                amount = area_px / (px_per_mm ** 2)
                unit = "mm2"
        
            # добавляем к выходному списку измерений
            objects.append({
                "classname": classname,
                "amount": int(amount),
                "unit": unit
            })

        res.append({
            "output_file": output_files[file_i],
            "object_list": objects
        })

        file_i += 1
    
    return res



# запуск скрипта напрямую с коммандной строки
if __name__ == "__main__":
    model_file = sys.argv[1]
    images = sys.argv[2]
    output_dir = sys.argv[3]
    px_per_mm = float(sys.argv[4])

    # если вместо пути файла весов передать точку,
    # то скрипт будет искать в текущей директории файл весов
    # с тем же именем что и скрипт, но с расширением ".pt"
    if model_file == ".":
        model_file = sys.argv[0].split(".")[0] + ".pt"
    
    # прогоняем пачку картинок через модель
    results = measure_dir(YOLO(model_file), images, px_per_mm, output_dir)
    for res in results:
        # выводим в консоль обнаруженные объекты: имя класса и их площадь/длину
        i = 1
        for obj in res["object_list"]:
            print("Object " + str(i) + ": ", obj["classname"] + "  " + str(obj["amount"]) + " " + obj["unit"])
            i += 1
        print("in " + res["output_file"] + "\n")
