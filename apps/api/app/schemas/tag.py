from pydantic import BaseModel, ConfigDict

from app.models.enums import TagCategory


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    category: TagCategory
