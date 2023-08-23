import cv2
from imread_from_url import imread_from_url

from yoloseg import YOLOSeg
import cv2
import numpy as np
from yoloseg.utils import class_names
# Initialize YOLOv5 Instance Segmentator
model_path = "models/yolov8m-seg.onnx"
yoloseg = YOLOSeg(model_path, conf_thres=0.5, iou_thres=0.3)

# Read image
img_url = "image_test/abhi.jpg"#furniture_image_tags/aashish.png"
img = cv2.imread(img_url)

# Detect Objects
boxes, scores, class_ids, masks = yoloseg(img)

print(type(masks))

# Draw detections
combined_img = yoloseg.draw_masks(img)
cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
cv2.imshow("Detected Objects", combined_img)
cv2.imwrite("doc/img/detected_objects.jpg", combined_img)

cv2.waitKey(0)
cv2.destroyAllWindows()


for index,i in enumerate(masks):
    mask_image = i.astype(np.uint8)  # Assuming there is only one mask for the first detected object

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
    cv2.imwrite("{}_{}.jpg".format(class_names[class_ids[index]],index), cropped_area)
