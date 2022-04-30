from google.cloud import vision
from models import OCRResult

class OCRService:
    def get_ocr_results(image):
        client = vision.ImageAnnotatorClient()
        vision_image = vision.Image(content=image)
        response = client.text_detection(image=vision_image)
        texts = response.text_annotations
        ocr_results = []

        for text in texts:
            ocr_results.append(OCRResult(text.description, text.bounding_poly))

        return ocr_results