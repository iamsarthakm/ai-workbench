"""Example resource wired end-to-end (route -> controller -> model -> DB). Replace
or delete once you have real resources — kept only to prove the scaffold works."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.item import create_item, list_items
from app.core.security import get_current_user
from app.database import get_db
from app.schemas.common import GenericApiResponse
from app.schemas.item import CreateItemRequest, ItemResponse

router = APIRouter(prefix="/items")


@router.get("", response_model=GenericApiResponse[list[ItemResponse]])
async def get_items(db: AsyncSession = Depends(get_db)):
    items = await list_items(db)
    return GenericApiResponse[list[ItemResponse]](
        data=[ItemResponse.model_validate(item) for item in items]
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=GenericApiResponse[ItemResponse],
)
async def post_item(
    payload: CreateItemRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await create_item(payload, db)
    return GenericApiResponse[ItemResponse](data=ItemResponse.model_validate(item))
