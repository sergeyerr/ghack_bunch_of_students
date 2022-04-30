from typing import List
from google.cloud import vision
import io
import shapely.geometry as geo
import itertools
import re

#temp
import random
import cv2
import numpy as np

class OCRResult:
    description: str
    bounding_box: geo.Polygon

    def __init__(self, description: str, bounding_poly: dict) -> None:
        self.description = description
        points = []

        for vertex in bounding_poly.vertices:
            points.append(geo.Point(vertex.x, vertex.y))
        
        self.bounding_box = geo.Polygon(points)
    
class LineOCRResult:
    full_description: List[str]
    expected_article_description: List[str]
    bounding_box: geo.Polygon
    pixel_margin = 20

    def __init__(self, ocr_results: List[OCRResult]) -> None:
        min_x = min(itertools.chain.from_iterable(r.bounding_box.boundary.xy[0] for r in ocr_results))
        max_x = max(itertools.chain.from_iterable(r.bounding_box.boundary.xy[0] for r in ocr_results))
        min_y = min(itertools.chain.from_iterable(r.bounding_box.boundary.xy[1] for r in ocr_results))
        max_y = max(itertools.chain.from_iterable(r.bounding_box.boundary.xy[1] for r in ocr_results))

        self.bounding_box = geo.Polygon.from_bounds(min_x, min_y, max_x, max_y)

        ocr_results.sort(key=lambda r: min(r.bounding_box.boundary.xy[0]))

        self.full_description = [r.description for r in ocr_results]
        self.expected_article_description = []

        digit_regex = re.compile(r'\d+(?:,\d*)?')

        for fd in self.full_description:
            if not digit_regex.match(fd):
                self.expected_article_description.append(fd)


    def within_pixel_margin(left, right, margin):
        return left - margin <= right <= left + margin

    def group_ocr_results(ocr_results: List[OCRResult], img_height: int, line_diff_percentage: float = 0.025):
        y_groups = []
        margin = img_height * line_diff_percentage

        for r in ocr_results:
            miny = min(r.bounding_box.boundary.xy[1])

            if not any(filter(lambda y: LineOCRResult.within_pixel_margin(miny, y, margin), y_groups)):
                y_groups.append(miny)

            
        grouped = [
            [
                r for r in ocr_results 
                if LineOCRResult.within_pixel_margin(min(r.bounding_box.boundary.xy[1]), y_group, margin)
            ]
            for y_group in y_groups
        ]
        return [LineOCRResult(results) for results in grouped]


def test(img_path, line_results):
    img = cv2.imread(img_path)

    for l in line_results:
        color  = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pts = np.array(list(zip(*l.bounding_box.exterior.coords.xy)), np.int32)
        cv2.polylines(img, [pts], True, color, 5)

    cv2.imshow("Test", cv2.resize(img, (640, 640)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    # first one is the overall bounding box. we can skip it
    text_iter = iter(texts)
    full = next(text_iter)
    full = OCRResult(full.description, full.bounding_poly)
    y = full.bounding_box.boundary.xy[0]
    full_height = max(y) - min(y)

    ocr_results = []

    for text in text_iter:
        ocr_results.append(OCRResult(text.description, text.bounding_poly))

    line_ocrs = LineOCRResult.group_ocr_results(ocr_results, full_height)

    test(path, line_ocrs)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

if __name__ == '__main__':
    detect_text('./ocr_test_image.jpg')
