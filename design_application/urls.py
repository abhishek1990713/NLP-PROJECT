from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.index,name ='homes'),
    path("detect-object/", views.detect_objects, name='detect_objects'),
    path('run_app/',views.run_app, name="run_app")
]


from ultralytics import YOLO
from PIL import Image
import os
import numpy as np
import logging
import cv2
import pandas as pd
ffrom ultralytics import YOLO
from PIL import Image
import os
import numpy as np
import logging
import cv2
import pandas as pd
import re
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor

logging.getLogger('ppocr').setLevel(logging.WARNING)

# DocTR configuration
os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models"
os.environ['USE_TORCH'] = '1'

# Initialize DocTR OCR model
ocr_model = ocr_predictor(det_arch='db_resnet50',
                          reco_arch='crnn_vgg16_bn',
                          pretrained=True)

# PaddleOCR model paths
det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

# Initialize PaddleOCR
paddle_ocr = PaddleOCR(lang='en',
                        use_angle_cls=False,
                        use_gpu=False,
                        det=True,
                        rec=True,
                        cls=False,
                        det_model_dir=det_model_dir,
                        rec_model_dir=rec_model_dir,
                        cls_model_dir=cls_model_dir)

passport_model_path = r"/home/ko19678/japan_pipeline/ALL_Passport/best.pt"

valid_issue_date = "22 AUG 2010"
valid_expiry_date = "22 AUG 2029"


def preprocess_image(image_path):
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image


def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom

    if image.mode == 'RGB':
        color = (255, 255, 255)
    else:
        color = 0

    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (left, top))
    return result


def extract_text_doctr(image_cv2):
    """ Extract text using DocTR """
    result_texts = ocr_model([image_cv2])
    extracted_text = ""

    if result_texts.pages:
        for page in result_texts.pages:
            for block in page.blocks:
                for line in block.lines:
                    extracted_text += "".join([word.value for word in line.words]) + " "

    return extracted_text.strip()


def extract_text_paddle(image_cv2):
    """ Extract text using PaddleOCR """
    result_texts = paddle_ocr.ocr(image_cv2, cls=False)
    extracted_text = ""

    if result_texts:
        for result in result_texts:
            for line in result:
                extracted_text += line[1][0] + " "

    return extracted_text.strip()


def parse_mrz(mrl1, mrl2):
    """Extracts passport details from MRZ (Machine Readable Zone) lines and returns a DataFrame."""

    # Ensure MRZ lines are padded to at least 44 characters
    mrl1 = mrl1.ljust(44, "<")[:44]
    mrl2 = mrl2.ljust(44, "<")[:44]

    # Extract document type (e.g., P, PD, PP)
    document_type = mrl1[:2].strip("<")

    # Extract issuing country code
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"

    # Extract surname and given names
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    # Extract passport number
    passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else "Unknown"

    # Extract nationality
    nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else "Unknown"

    # Date conversion function (YYMMDD → DD/MM/YYYY)
    def format_date(yyMMdd):
        if len(yyMMdd) != 6 or not yyMMdd.isdigit():
            return "Invalid Date"
        yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
        return f"{dd}/{mm}/{year}"

    # Extract date of birth and expiry date
    dob = format_date(mrl2[13:19]) if len(mrl2) > 19 else "Unknown"
    expiry_date = format_date(mrl2[21:27]) if len(mrl2) > 27 else "Unknown"

    # Extract gender
    gender_code = mrl2[20] if len(mrl2) > 20 else "X"
    gender_mapping = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}
    gender = gender_mapping.get(gender_code, "Unspecified")

    # Extract optional data
    optional_data = re.sub(r"<+$", "", mrl2[28:]).strip() if len(mrl2) > 28 else "N/A"

    # Create structured data for DataFrame
    data = [
        ("Document Type", document_type),
        ("Issuing Country", country_code),
        ("Surname", surname),
        ("Given Names", given_names),
        ("Passport Number", passport_number),
        ("Nationality", nationality),
        ("Date of Birth", dob),
        ("Gender", gender),
        ("Expiry Date", expiry_date),
        ("Optional Data", optional_data if optional_data else "N/A"),
    ]

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=["Label", "Extracted_text"])
    return df


def process_passport_information(input_file_path):
    model = YOLO(passport_model_path)
    input_image = preprocess_image(input_file_path)

    results = model(input_image)

    input_image = Image.open(input_file_path)
    output = []
    mrz_data = {"MRL_One": None, "MRL_Second": None}

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy.tolist()[0]

            # Crop and pad image
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            padded_image = add_fixed_padding(cropped_image, right=100, left=100, top=100, bottom=100)

            cropped_image_np = np.array(padded_image)
            cropped_image_cv2 = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

            # Use PaddleOCR for MRZ, otherwise use DocTR
            if label in ["MRL_One", "MRL_Second"]:
                extracted_text = extract_text_paddle(cropped_image_cv2)
                mrz_data[label] = extracted_text
            else:
                extracted_text = extract_text_doctr(cropped_image_cv2)

            output.append({'Label': label, 'Extracted_text': extracted_text})

    # If both MRZ lines were extracted, parse them
    if mrz_data["MRL_One"] and mrz_data["MRL_Second"]:
        mrz_df = parse_mrz(mrz_data["MRL_One"], mrz_data["MRL_Second"])
        output.extend(mrz_df.to_dict(orient="records"))

    data = pd.DataFrame(output)
    return data
