import dataclasses


@dataclasses.dataclass
class QueryParameter:
    name: str
    map_to: str
    explode: bool
