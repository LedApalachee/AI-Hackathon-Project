import numpy as np
from skimage.morphology import skeletonize


def measure(model, image, px_per_mm, output_path):
    results = model.predict(image, save=False)[0]   # получаем объект Results
    results.save(output_path)

    # список объектов с посчитанными длиной/площадью
    # поля объектов списка: classname, amount (результат замера), unit (единица измерения, str)
    objects = []

    # проходимcя по каждому обнаруженному объекту
    for i in range(len(results.boxes)):
        # достаем класс объекта и его маску
        classname = results.names[results.boxes.cls.int().tolist()[i]]
        amount = 0
        unit = ""
        mask = results.masks.data[i].cpu().numpy() # превращаем в ndarray

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
    
    return objects
