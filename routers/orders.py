from fastapi import APIRouter, Depends, Query, Path
from typing import Optional

from models import OrderCreate, OrderCreateResponse, OrdersListResponse
from services import OrderService, get_order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderCreateResponse, status_code=201)
async def create_order(
    order: OrderCreate,
    order_service: OrderService = Depends(get_order_service)
):
    """Create a new order"""
    return await order_service.create_order(order)


@router.get("/{user_id}", response_model=OrdersListResponse)
async def get_user_orders(
    user_id: str = Path(..., description="User ID to get orders for"),
    limit: int = Query(10, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    order_service: OrderService = Depends(get_order_service)
):
    """Get orders for a specific user with pagination"""
    return await order_service.get_orders_by_user(user_id, limit, offset)
