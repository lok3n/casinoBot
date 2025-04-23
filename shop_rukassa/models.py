from pydantic import BaseModel
from typing import Union, Optional


class Balance(BaseModel):
    balance_rub: float
    balance_usd: float


class CreatePayment(BaseModel):
    id: int
    hash: str
    url: str


class Payment(BaseModel):
    id: Optional[int] = None
    order_id: Union[int, str] = None
    amount: Optional[float] = None
    in_amount: Optional[float] = None
    data: Optional[str] = None
    createdDateTime: Optional[str] = None
    status: Optional[str] = None
    way: Optional[str] = None


class CreateWithdrawRequest(BaseModel):
    id: int
    status: str


class CancelWithdrawRequest(BaseModel):
    id: int
    status: str


class WithdrawRequest(BaseModel):
    id: int
    order_id: Union[int, str]
    amount: float
    fee: Optional[float] = None
    way: str
    who_fee: str
    status: str
