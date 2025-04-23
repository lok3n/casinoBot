import os
from aiohttp import ClientSession, TCPConnector
from datetime import datetime
from typing import Optional
import ssl
import certifi
from shop_rukassa.exceptions import RequestError, BadRequest
from shop_rukassa.models import CreatePayment, Payment, CreateWithdrawRequest
import asyncio


class Client:
    def __init__(self,
                 token: str = None,
                 shop_id: int = None,
                 base_url: str = None,
                 email: str = None,
                 password: str = None,
                 ):

        if base_url is None:
            self.base_url = "https://lk.rukassa.pro/api/v1/"
        if token is not None:
            self.token = token
        if shop_id is not None:
            self.shop_id = shop_id
        if email is not None:
            self.email = email
        if password is not None:
            self.password = password

        self._session: Optional[ClientSession] = None

    def _getsession(self) -> ClientSession:

        if isinstance(self._session, ClientSession) and not self._session.closed:
            return self._session

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = TCPConnector(ssl=ssl_context)

        self._session = ClientSession(connector=connector)

        return self._session

    async def _request(self, method, **kwargs) -> dict:
        session = self._getsession()
        async with session.post(self.base_url + method, **kwargs) as response:
            if response.status == 200:
                response = await response.json(content_type="text/html")
            else:
                raise RequestError(
                    f"Response status: {response.status}. Text: {await response.text()}"
                )

        await self._session.close()

        return await self._checkexception(response)

    async def _checkexception(self, response: dict) -> dict:
        if response.get("error"):
            raise BadRequest("[RuKassa] " + response["message"])
        return response

    async def create_payment(self, order_id: int, amount: float | int, user_code: str = None):
        method = 'create'

        params = {'order_id': order_id,
                  'amount': float(amount),
                  'shop_id': self.shop_id,
                  'token': self.token
                  }

        if user_code:
            params['user_code'] = user_code

        response = await self._request(method, params=params)

        return CreatePayment(**response)

    async def create_withdraw(self, way: str, wallet: str, amount: int | float, order_id: int = None):
        method = 'createWithdraw'

        params = {'email': self.email,
                  'password': self.password,
                  'way': way,
                  'wallet': wallet,
                  'amount': amount
                  }
        if order_id is not None:
            params['order_id'] = order_id

        response = await self._request(method, params=params)

        return CreateWithdrawRequest(**response)

    async def get_info_payment(self, payment_id: int = None, order_id: int = None, status: str = None):
        method = 'getPayInfo'

        params = {'id': payment_id,
                  'order_id': order_id,
                  'status': status,
                  'shop_id': self.shop_id,
                  'token': self.token}

        for key, value in params.copy().items():
            if value is None:
                params.pop(key)

        response = await self._request(method, params=params)

        return Payment(**response)

    async def revoke_payment(self, payment_id: int):
        method = 'revoke'

        params = {'id': payment_id,
                  'shop_id': self.shop_id,
                  'token': self.token}

        return await self._request(method, params=params)
