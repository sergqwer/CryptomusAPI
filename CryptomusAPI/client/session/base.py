from __future__ import annotations
from typing import Callable, Any
from types import TracebackType
from abc import ABC, abstractmethod
import json

from adaptix.load_error import LoadError

from CryptomusAPI.methods.base import Method, ResponseType
from CryptomusAPI.exceptions import CryptomusError

_JsonDumps = Callable[..., Any]

DEFAULT_TIMEOUT = 60.0
DEFAULT_HEADERS = {
    "merchant": "",
    "sign": "",
    "Content-Type": "application/json"
}
API_BASE_URL = "https://api.cryptomus.com/{}"


class BaseSession(ABC):

    def __init__(
        self,
        json_dumps: _JsonDumps = json.dumps,
        timeout: float = DEFAULT_TIMEOUT,
        headers: dict[str, str] | None = None,
        api_endpoint: str | None = None
    ) -> None:
        self.json_dumps = json_dumps
        self.timeout = timeout
        self.headers = headers or DEFAULT_HEADERS
        self.endpoint = api_endpoint or API_BASE_URL

    def check_response(
        self,
        method: Method[ResponseType],
        status_code: int,
        data: dict[str, Any]
    ) -> ResponseType:
        try:
            json_data = self.json_dumps(data)
        except Exception as e:
            raise CryptomusError(f"Error while parsing json: {e}")

        if status_code == 200:
            return json_data

        raise CryptomusError(f"Error while request [{status_code}]: {json_data}")
    
    @abstractmethod
    async def make_request(self, method: Method[ResponseType]) -> ResponseType:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
    
    async def __aenter__(self) -> BaseSession:
        return self
    
    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def __call__(self, method: Method[ResponseType]) -> ResponseType:
        return await self.make_request(method)


# class _BaseCryptomusAPI(abc.ABC):
#     _BASE_API_LINK = "https://api.cryptomus.com/"

#     def __init__(self, merchant_uuid: str, api_key: str) -> None:
#         self._merchant_uuid = merchant_uuid
#         self._api_key = api_key

#         self._session = aiohttp.ClientSession()

#     async def __aenter__(self) -> "_BaseCryptomusAPI":
#         return self
    
#     async def __aexit__(self, *args) -> None:
#         await self.close()

#     async def _make_request(
#         self, endpoint: str, method: Literal["post", "get"] = "post", **kwargs
#     ) -> Any:
#         json_dumps = json.dumps(kwargs["data"])
#         sign = hashlib.md5(
#             base64.b64encode(json_dumps.encode('ascii')) + self._api_key.encode('ascii')
#         ).hexdigest()

#         headers = {
#             "merchant": self._merchant_uuid,
#             "sign": sign,
#             "Content-Type": "applicaiton/json"
#         }

#         async with self._session.request(
#             method,
#             f"{self._BASE_API_LINK}{endpoint}",
#             headers=headers,
#             data=json_dumps
#         ) as response:
#             match response.status:
#                 case 405:
#                     raise CryptomusError("[405] Method not allowed")

#             data = await response.json()

#             if data.get("message"):
#                 raise CryptomusError(data["message"])
#             if data.get("errors"):
#                 raise CryptomusError(str(data["errors"]))
#             return data
        

#     @staticmethod
#     def _get_func_params(params: dict[str, Any]) -> dict[str, Any]:
#         if params.get("self"):
#             del params["self"]

#         data = {}
#         [
#             data.update({key: value})
#             for key, value in params.items()
#             if params[key] is not None
#         ]
#         return data
    
#     async def close(self) -> None:
#         return await self._session.close()
