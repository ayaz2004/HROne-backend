from fastapi import APIRouter, Depends, Query
from typing import Optional

from models import ProductCreate, ProductCreateResponse, ProductsListResponse
from services import ProductService, get_product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductCreateResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    product_service: ProductService = Depends(get_product_service)
):
    """Create a new product"""
    return await product_service.create_product(product)


@router.get("/", response_model=ProductsListResponse)
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports regex)"),
    size: Optional[str] = Query(None, description="Filter by product size"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    product_service: ProductService = Depends(get_product_service)
):
    """List products with optional filtering and pagination"""
    return await product_service.get_products(name, size, limit, offset)
