import platform
import cv2
import numpy as np
import openvino as ov
import requests
from pathlib import Path
import ipywidgets as widgets

# Descarca modulul `notebook_utils`
r = requests.get(url="https://raw.githubusercontent.com/openvinotoolkit/openvino_notebooks/latest/utils/notebook_utils.py")
open("notebook_utils.py", "w").write(r.text)
from notebook_utils import segmentation_map_to_image, download_file

# Defineste caile pentru model
base_model_dir = Path("./model").expanduser()
model_name = "road-segmentation-adas-0001"
model_xml_name = f"{model_name}.xml"
model_bin_name = f"{model_name}.bin"
model_xml_path = base_model_dir / model_xml_name

# Descarca modelul daca nu este deja descarcat
if not model_xml_path.exists():
    model_xml_url = (
        "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2023.0/models_bin/1/road-segmentation-adas-0001/FP32/road-segmentation-adas-0001.xml"
    )
    model_bin_url = (
        "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2023.0/models_bin/1/road-segmentation-adas-0001/FP32/road-segmentation-adas-0001.bin"
    )
    download_file(model_xml_url, model_xml_name, base_model_dir)
    download_file(model_bin_url, model_bin_name, base_model_dir)
else:
    print(f"{model_name} deja descarcat in {base_model_dir}")

# Initializeaza core-ul OpenVINO si listeaza dispozitivele disponibile
core = ov.Core()
device = widgets.Dropdown(
    options=core.available_devices + ["AUTO"],
    value="AUTO",
    description="Device:",
    disabled=False,
)
print("Dispozitive disponibile:", core.available_devices)

# Incarca modelul
model = core.read_model(model=model_xml_path)
compiled_model = core.compile_model(model=model, device_name=device.value)

# Obtine straturile de intrare si iesire ale modelului
input_layer_ir = compiled_model.input(0)
output_layer_ir = compiled_model.output(0)

# Creeaza cereri de inferenta
num_requests = 2  
infer_requests = [compiled_model.create_infer_request() for _ in range(num_requests)]

def procesareRoad(image):
    # Converteste imaginea din BGR in RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_h, image_w, _ = image.shape

    # Obtine forma de intrare a modelului
    N, C, H, W = input_layer_ir.shape

    # Redimensioneaza imaginea la forma de intrare a modelului
    resized_image = cv2.resize(image, (W, H))

    # Pregateste imaginea pentru model
    input_image = np.expand_dims(resized_image.transpose(2, 0, 1), 0).astype(np.float32)

    # Converteste imaginea de intrare intr-un tensor OpenVINO
    tensor = ov.Tensor(array=input_image)

    # Selecteaza o cerere de inferenta disponibila
    request_id = 0  # Alege ID-ul cererii dupa cum este necesar, in mod rotativ sau prin alta metoda
    infer_request = infer_requests[request_id]

    # Seteaza tensorul de intrare
    infer_request.set_tensor(input_layer_ir, tensor)

    # Ruleaza inferenta asincron
    infer_request.start_async()

    # Asteapta rezultatul
    infer_request.wait()

    # Obtine rezultatul
    result = infer_request.get_tensor(output_layer_ir).data

    # Pregateste datele pentru vizualizare
    segmentation_mask = np.argmax(result, axis=1)

    # Defineste colormap-ul
    colormap = np.array([[0, 0, 0], [48, 103, 141], [53, 183, 120], [199, 216, 52]])
    
    # Defineste transparenta
    alpha = 0.3

    # Converteste harta de segmentare in imagine RGB
    mask = segmentation_map_to_image(segmentation_mask, colormap, remove_holes=True)
    resized_mask = cv2.resize(mask, (image_w, image_h))

    # Suprapune masca peste imaginea originala
    image_with_mask = cv2.addWeighted(resized_mask, alpha, rgb_image, 1 - alpha, 0)

    # Returneaza imaginea cu masca
    return image_with_mask
