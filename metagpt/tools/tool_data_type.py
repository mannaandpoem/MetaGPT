from enum import Enum

from pydantic import BaseModel


class ToolTypeEnum(Enum):
    IMAGE2WEBPAGE = "image2webpage"
    OTHER = "other"

    def __missing__(self, key):
        return self.OTHER


class ToolType(BaseModel):
    name: str
    desc: str
    usage_prompt: str = ""


class ToolSchema(BaseModel):
    name: str


class Tool(BaseModel):
    name: str
    path: str
    schemas: dict = {}
    code: str = ""
