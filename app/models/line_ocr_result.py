import itertools
from typing import List
import shapely.geometry as geo
import re

from app.models.ocr_result import OCRResult

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

    def group_ocr_results(ocr_results: List[OCRResult], img_height: int, line_diff_percentage: float = 0.02):
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