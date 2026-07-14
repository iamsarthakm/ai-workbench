from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import CreateItemRequest


async def create_item(payload: CreateItemRequest, db: AsyncSession) -> Item:
    item = Item(name=payload.name)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def list_items(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item).order_by(Item.id.desc()))
    return list(result.scalars().all())
