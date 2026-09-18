from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set

from config.settings import get_settings
from services.solana_rpc import SolanaRPC, SolanaRPCError
from utils.logger import logger


@dataclass
class BuyerInfo:
    wallet: str
    amount: Optional[float] = None
    signature: Optional[str] = None
    slot: Optional[int] = None


@dataclass
class BuyersResult:
    mint: str
    date: str
    buyers: List[BuyerInfo] = field(default_factory=list)
    signatures_checked: int = 0
    error: Optional[str] = None


async def find_buyers(mint: str, target_date: datetime) -> BuyersResult:
    settings = get_settings()
    max_sigs = settings.max_signatures_per_query

    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    start_ts = int(day_start.timestamp())
    end_ts = int(day_end.timestamp())

    result = BuyersResult(mint=mint, date=target_date.strftime("%Y-%m-%d"))

    buyers_map: Dict[str, BuyerInfo] = {}

    async with SolanaRPC() as rpc:
        signatures_in_range: List[dict] = []
        before: Optional[str] = None
        total_fetched = 0

        logger.info(f"Searching signatures for mint {mint[:8]}... on {result.date}")

        while total_fetched < max_sigs:
            try:
                batch = await rpc.get_signatures_for_address(
                    address=mint,
                    limit=min(1000, max_sigs - total_fetched),
                    before=before,
                )
            except SolanaRPCError as e:
                logger.warning(f"RPC error while fetching signatures: {e}")
                if not signatures_in_range:
                    result.error = str(e)
                    return result
                break

            if not batch:
                break

            total_fetched += len(batch)
            stop = False

            for sig_info in batch:
                block_time = sig_info.get("blockTime")
                if block_time is None:
                    continue

                if block_time >= end_ts:
                    continue
                if block_time < start_ts:
                    stop = True
                    break

                signatures_in_range.append(sig_info)

            if stop or len(batch) < 1000:
                break

            before = batch[-1]["signature"]

        result.signatures_checked = len(signatures_in_range)
        logger.info(f"Found {len(signatures_in_range)} signatures in target day")

        if not signatures_in_range:
            return result

        signatures_in_range.sort(key=lambda x: x.get("blockTime") or 0, reverse=True)
        to_process = signatures_in_range[: max(50, min(150, max_sigs // 2))]

        for i, sig_info in enumerate(to_process):
            sig = sig_info["signature"]
            try:
                tx = await rpc.get_transaction(sig)
            except SolanaRPCError as e:
                logger.debug(f"Failed to fetch tx {sig[:16]}...: {e}")
                continue

            if not tx:
                continue

            meta = tx.get("meta")
            if not meta or meta.get("err"):
                continue

            pre_balances = {
                (b.get("owner"), b.get("mint")): float(b.get("uiTokenAmount", {}).get("uiAmount") or 0)
                for b in (meta.get("preTokenBalances") or [])
                if b.get("mint") == mint and b.get("owner")
            }
            post_balances = {
                (b.get("owner"), b.get("mint")): float(b.get("uiTokenAmount", {}).get("uiAmount") or 0)
                for b in (meta.get("postTokenBalances") or [])
                if b.get("mint") == mint and b.get("owner")
            }

            all_owners = set(k[0] for k in pre_balances) | set(k[0] for k in post_balances)

            for owner in all_owners:
                pre = pre_balances.get((owner, mint), 0.0)
                post = post_balances.get((owner, mint), 0.0)
                delta = post - pre

                if delta > 0.000001:
                    existing = buyers_map.get(owner)
                    if existing is None or (existing.amount or 0) < delta:
                        buyers_map[owner] = BuyerInfo(
                            wallet=owner,
                            amount=delta,
                            signature=sig,
                            slot=tx.get("slot"),
                        )

            if (i + 1) % 20 == 0:
                logger.info(f"Processed {i + 1}/{len(to_process)} transactions...")

    sorted_buyers = sorted(
        buyers_map.values(),
        key=lambda b: b.amount or 0,
        reverse=True,
    )
    result.buyers = sorted_buyers

    logger.info(f"Found {len(result.buyers)} unique buyers")
    return result
