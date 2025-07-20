from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


# Product Models
class SizeInfo(BaseModel):
    size: str
    quantity: int


class ProductCreate(BaseModel):
    name: str
    price: float
    size: List[SizeInfo]


class Product(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    price: float
    size: List[SizeInfo]


class ProductResponse(BaseModel):
    id: str
    name: str
    price: float


class ProductCreateResponse(BaseModel):
    id: str


# Order Models
class OrderItem(BaseModel):
    productId: str
    qty: int


class OrderCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    userId: str
    items: List[OrderItem] = Field(alias="limit") 


class Order(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: str
    items: List[OrderItem]


class OrderCreateResponse(BaseModel):
    id: str


class ProductDetails(BaseModel):
    name: str
    id: str


class OrderItemResponse(BaseModel):
    productDetails: ProductDetails
    qty: int


class OrderResponse(BaseModel):
    id: str
    items: List[OrderItemResponse]


class PageInfo(BaseModel):
    next: Optional[int] = None
    limit: int
    previous: Optional[int] = None


class ProductsListResponse(BaseModel):
    data: List[ProductResponse]
    page: PageInfo


class OrdersListResponse(BaseModel):
    data: List[OrderResponse]
    page: PageInfo
