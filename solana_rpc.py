from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import get_settings
from utils.logger import logger


class SolanaRPCError(Exception):
    pass


class SolanaRPC:
    def __init__(self) -> None:
        settings = get_settings()
        self.rpc_url = settings.rpc_url
        self.timeout = settings.request_timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "SolanaRPC":
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *args) -> None:
        if self._client:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, SolanaRPCError)),
        reraise=True,
    )
    async def _request(self, method: str, params: list) -> Any:
        if not self._client:
            raise RuntimeError("SolanaRPC must be used as async context manager")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }

        try:
            resp = await self._client.post(self.rpc_url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            if "error" in data:
                err = data["error"]
                msg = err.get("message", str(err))
                # Rate limit or node errors
                if "429" in str(err) or "rate" in msg.lower() or "limit" in msg.lower():
                    raise SolanaRPCError(f"Rate limited: {msg}")
                raise SolanaRPCError(msg)

            return data.get("result")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise SolanaRPCError("HTTP 429 Rate limited")
            raise

    async def get_signatures_for_address(
        self,
        address: str,
        limit: int = 1000,
        before: Optional[str] = None,
        until: Optional[str] = None,
    ) -> List[Dict]:
        params: List[Any] = [address, {"limit": limit}]
        options = params[1]
        if before:
            options["before"] = before
        if until:
            options["until"] = until

        result = await self._request("getSignaturesForAddress", params)
        return result or []

    async def get_transaction(self, signature: str) -> Optional[Dict]:
        result = await self._request(
            "getTransaction",
            [
                signature,
                {
                    "encoding": "jsonParsed",
                    "maxSupportedTransactionVersion": 0,
                    "commitment": "confirmed",
                },
            ],
        )
        return result

    async def get_token_supply(self, mint: str) -> Optional[Dict]:
        result = await self._request("getTokenSupply", [mint])
        return result
