from flatpoints.common.header import Header
import json


class flatpoints():
    header: Header
    data: list[int]
    properties: dict

    def _get_type(obj: object) -> int:
        typeclass = type(obj)
        if typeclass is int:
            if obj < 0:
                return 1 if obj.bit_length() < 33 else 2
            else:
                return 3 if obj.bit_length() < 33 else 4
        elif typeclass is float:
            return 6
        elif typeclass is str:
            return 7
        elif typeclass is bool:
            return 8
        else:
            return 0

    def __init__(self, filepath: str):
        with open(filepath, 'r') as file:
            geojson = json.load(file)

    def _init_header(self, data: dict):
        template = geojson[0]['properties']
        self.header.coordinates_count = len(geojson)
        self.header.properties_count = len(template)
        self.header.properties_names = list(template.keys())
        self.header.properties_types = [
            self._get_type(x) for x in list(template.values())]

    def _parse_props(self, data: dict):
        self.properties = [x['properties'] for x in geojson]

    def _parse_coords(self, data: dict):
        pass
