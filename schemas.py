from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    quantity: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
