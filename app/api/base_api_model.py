from pydantic import BaseModel


class BaseAPIModel(BaseModel):
    model_config = {
        "from_attributes": True,
    }
