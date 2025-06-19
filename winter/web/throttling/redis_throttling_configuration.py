from dataclasses import dataclass


@dataclass
class RedisThrottlingConfiguration:
    host: str
    port: int
    db: int
    password: str | None = None
