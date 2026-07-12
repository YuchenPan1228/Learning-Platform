from fastapi import APIRouter
from sqlalchemy import select

from app.dependencies import SessionDep
from app.models.tag import Tag
from app.schemas.tag import TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
def list_tags(session: SessionDep) -> list[TagRead]:
    tags = session.scalars(select(Tag).order_by(Tag.category, Tag.name, Tag.id)).all()
    return [TagRead(id=tag.id, slug=tag.slug, name=tag.name, category=tag.category) for tag in tags]
