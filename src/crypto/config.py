from dataclasses import dataclass

@dataclass(frozen=True)
class Argon2Config:
    memory_cost: int = 65536
    time_cost: int = 3
    parallelism: int = 4
    hash_length: int = 32    
