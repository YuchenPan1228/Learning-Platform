from pydantic import BaseModel, ConfigDict


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None
    order_index: int
    parent_topic_id: int | None


class TopicWithSubtopicsRead(TopicRead):
    subtopics: list[TopicRead]
