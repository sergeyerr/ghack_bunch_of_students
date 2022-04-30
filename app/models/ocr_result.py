import shapely.geometry as geo

class OCRResult:
    description: str
    bounding_box: geo.Polygon

    def __init__(self, description: str, bounding_poly: dict) -> None:
        self.description = description
        points = []

        for vertex in bounding_poly.vertices:
            points.append(geo.Point(vertex.x, vertex.y))
        
        self.bounding_box = geo.Polygon(points)
    