import cv2
import numpy as np
from PIL import Image
from pytesseract import pytesseract
from io import BytesIO
import enum

class OS(enum.Enum):
    Windows = 1

class Language(enum.Enum):
    ENG = 'eng'

class ImageReader:
    def __init__(self, os: OS):
        if os == os.Windows:
            windows_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pytesseract.tesseract_cmd = windows_path

    def preprocess_image(self, image_io):
        image = Image.open(image_io)
        img_np = np.array(image)

        # Convert image to grayscale if it has more than one channel
        if len(img_np.shape) > 2 and img_np.shape[2] > 1:
            gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_np

        # Manually set threshold and apply global binarization
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        # Save the preprocessed image for OCR
        cv2.imwrite('images/preprocessed_image.png', thresh)
        return 'images/preprocessed_image.png'

    def extract_text(self, image: Image.Image, lang: str) -> str:
        preprocessed_image = self.preprocess_image(image)
        preprocessed_image = self.preprocess_image(preprocessed_image)
        img = Image.open(preprocessed_image)
        extracted_text = pytesseract.image_to_string(img, lang=lang)
        return extracted_text