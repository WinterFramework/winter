import dataclasses


@dataclasses.dataclass
class MapQueryParameterAnnotation:
    name: str
    map_to: str = None

    def __eq__(self, other):
        return isinstance(other, MapQueryParameterAnnotation) and (
                self.name == other.name or self.map_to == other.map_to)
