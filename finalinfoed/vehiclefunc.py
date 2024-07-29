import os
from pathlib import Path
from typing import Tuple
import cv2
import numpy as np
import openvino as ov

# Importă modulul `notebook_utils`
import requests
r = requests.get(url="https://raw.githubusercontent.com/openvinotoolkit/openvino_notebooks/latest/utils/notebook_utils.py")
open("notebook_utils.py", "w").write(r.text)
import notebook_utils as utils

# Definirea căilor și numelor modelelor
base_model_dir = Path("model")
detection_model_name = "vehicle-detection-0200"
recognition_model_name = "vehicle-attributes-recognition-barrier-0039"
precision = "FP32"
base_model_url = "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2023.0/models_bin/1"
detection_model_url = f"{base_model_url}/{detection_model_name}/{precision}/{detection_model_name}.xml"
recognition_model_url = f"{base_model_url}/{recognition_model_name}/{precision}/{recognition_model_name}.xml"
detection_model_path = (base_model_dir / detection_model_name).with_suffix(".xml")
recognition_model_path = (base_model_dir / recognition_model_name).with_suffix(".xml")

# Descărcarea modelului de detectare
if not detection_model_path.exists():
    utils.download_file(detection_model_url, detection_model_name + ".xml", base_model_dir)
    utils.download_file(detection_model_url.replace(".xml", ".bin"), detection_model_name + ".bin", base_model_dir)

# Inițializarea OpenVINO Runtime
core = ov.Core()

# Funcție pentru inițializarea modelelor
def model_init(model_path: str) -> Tuple:
    model = core.read_model(model=model_path)
    compiled_model = core.compile_model(model=model, device_name="AUTO")
    input_key = compiled_model.input(0)
    output_key = compiled_model.output(0)
    return input_key, output_key, compiled_model

# Inițializarea modelului de detectare și recunoaștere
input_key_de, output_key_de, compiled_model_de = model_init(detection_model_path)
input_key_re, output_key_re, compiled_model_re = model_init(recognition_model_path)

# Obținerea dimensiunilor de intrare
height_de, width_de = list(input_key_de.shape)[2:]
height_re, width_re = list(input_key_re.shape)[2:]

# Funcție pentru procesarea vehiculului
def procesareVehicle(image_de):
    resized_image_de = cv2.resize(image_de, (width_de, height_de))
    input_image_de = np.expand_dims(resized_image_de.transpose(2, 0, 1), 0)
    infer_request = compiled_model_de.create_infer_request()
    
    # Începe inferența asincronă
    infer_request.start_async({input_key_de: input_image_de})
    
    # Așteaptă rezultatele
    infer_request.wait()
    boxes = infer_request.get_output_tensor(0)  # Modalitatea corectă de a obține tensorul de ieșire prin index
    boxes = np.squeeze(boxes.data, (0, 1))
    boxes = boxes[~np.all(boxes == 0, axis=1)]

    # Funcție pentru decuparea imaginilor
    def crop_images(bgr_image, resized_image, boxes, threshold=0.6) -> np.ndarray:
        (real_y, real_x), (resized_y, resized_x) = (bgr_image.shape[:2], resized_image.shape[:2])
        ratio_x, ratio_y = real_x / resized_x, real_y / resized_y
        boxes = boxes[:, 2:]
        car_position = []

        for box in boxes:
            conf = box[0]
            if conf > threshold:
                (x_min, y_min, x_max, y_max) = [
                    (int(max(corner_position * ratio_y * resized_y, 10)) if idx % 2 else int(corner_position * ratio_x * resized_x))
                    for idx, corner_position in enumerate(box[1:])
                ]
                car_position.append([x_min, y_min, x_max, y_max])

        return car_position

    car_position = crop_images(image_de, resized_image_de, boxes)

    # Funcție pentru convertirea rezultatelor în imagine
    def convert_result_to_image(compiled_model_re, bgr_image, resized_image, boxes, threshold=0.6):
        colors = {"red": (255, 0, 0), "green": (0, 255, 0)}
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        car_position = crop_images(image_de, resized_image, boxes)

        for x_min, y_min, x_max, y_max in car_position:
            rgb_image = cv2.rectangle(rgb_image, (x_min, y_min), (x_max, y_max), colors["red"], 2)

        return rgb_image

    return car_position
