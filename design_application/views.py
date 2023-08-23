from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
import cv2
import numpy as np
from home.yoloseg import YOLOSeg
from home.yoloseg.utils import class_names
from imread_from_url import imread_from_url
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .app import ImageSimilarity
import os
import glob
def index(request):
    if request.method == "GET":
        return render(request, "index.html")
    if request.method == "POST":

        pass



def detect_objects(request):
    # Initialize YOLOv5 Instance Segmentator
    model_path = "home/models/yolov8m-seg.onnx"
    remove_files('static/similar_images')
    yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

    # Read image (assuming you have a form that allows users to upload an image)
    if request.method == 'POST' and request.FILES['image']:
        image_file = request.FILES['image']
        img = cv2.imdecode(np.frombuffer(image_file.read(), np.uint8), cv2.IMREAD_COLOR)

        # Detect Objects
        boxes, scores, class_ids, masks = yoloseg(img)

        # Draw detections
        combined_img = yoloseg.draw_masks(img)


        object_names = []
        # Process each detected object
        for index, mask_image in enumerate(masks):
            mask_image = mask_image.astype(np.uint8)  # Assuming there is only one mask for the first detected object

            # Resize the mask to match the size of the input image if needed
            if mask_image.shape[:2] != img.shape[:2]:
                mask_image = cv2.resize(mask_image, img.shape[:2][::-1])

            # Apply the segmentation mask to extract the masked area
            masked_area = cv2.bitwise_and(img, img, mask=mask_image)

            contours, _ = cv2.findContours(mask_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Get the bounding box of the masked area
            x, y, w, h = cv2.boundingRect(contours[0])

            # Crop the masked area image
            cropped_area = masked_area[y:y+h, x:x+w]

            # Save the masked area as a separate image
            cv2.imwrite("static/{}.jpg".format(class_names[class_ids[index]]), cropped_area)
            object_names.append( {"class":class_names[class_ids[index]]} )

        # Save the detected objects image
        cv2.imwrite("static/detected_objects.jpg", combined_img)

        # Pass the image paths to the template for display
        context = {
            'detected_image': "detected_objects.jpg",
            'cropped_images': ["static/{}_{}.jpg".format(class_names[class_ids[i]], i) for i in range(len(masks))],
            'result':object_names
        }

        return render(request, 'index.html', context)

    return render(request, 'upload.html')


def run_app(request):
    if request.method == "POST":
        selected_object = request.POST['object_detection']
        similarity_finder = ImageSimilarity()
        similarity_finder.load_feature_cache()
        similarity_finder.find_similar_images('static/{}.jpg'.format(selected_object), 'home/furniture', threshold=0.5, output_folder='static/similar_images')

        image_names = []
        for x in os.listdir('static/similar_images'):
            image_names.append({"name": x})

        context = {"images": image_names}
        print(context)
        print(image_names)

          # Call the function to remove files

        return render(request, "result.html", context)

def remove_files(folder_path):
    files = glob.glob(folder_path + "/*")
    for file_path in files:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to remove {file_path}. Reason: {str(e)}")