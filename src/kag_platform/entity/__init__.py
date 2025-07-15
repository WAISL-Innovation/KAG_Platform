from dataclasses import dataclass


@dataclass(frozen=True)
class Neo4jConfig:
    neo4j_uri: str
    username: str 

@dataclass(frozen=True)
class ModelInfo:
    groq_model_name: str