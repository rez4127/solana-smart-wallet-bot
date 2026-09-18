import re
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.buyers_finder import find_buyers
from utils.logger import logger

router = Router(name="buyers")

MINT_REGEX = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@router.message(Command("buyers"))
async def cmd_buyers(message: Message) -> None:
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.answer(
            "فرمت اشتباه است.\n\n"
            "استفاده صحیح:\n"
            "<code>/buyers &lt;token_mint&gt; &lt;YYYY-MM-DD&gt;</code>\n\n"
            "مثال:\n"
            "<code>/buyers So11111111111111111111111111111111111111112 2025-06-15</code>"
        )
        return

    mint = args[1].strip()
    date_str = args[2].strip()

    if not MINT_REGEX.match(mint):
        await message.answer("آدرس mint نامعتبر است.")
        return

    if not DATE_REGEX.match(date_str):
        await message.answer("فرمت تاریخ اشتباه است. باید به شکل <code>YYYY-MM-DD</code> باشد.")
        return

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        await message.answer("تاریخ نامعتبر است.")
        return

    if target_date > datetime.now(timezone.utc):
        await message.answer("تاریخ نمی‌تواند در آینده باشد.")
        return

    status_msg = await message.answer(
        f"در حال جستجوی خریداران توکن\n"
        f"<code>{mint[:8]}...{mint[-6:]}</code>\n"
        f"در تاریخ <b>{date_str}</b> (UTC)...\n\n"
        "این کار ممکن است ۱ تا ۳ دقیقه طول بکشد. لطفاً صبر کنید."
    )

    try:
        result = await find_buyers(mint=mint, target_date=target_date)

        if not result.buyers:
            await status_msg.edit_text(
                f"هیچ خریداری در تاریخ <b>{date_str}</b> برای این توکن پیدا نشد.\n\n"
                "ممکن است:\n"
                "• در آن روز تراکنشی نبوده\n"
                "• محدودیت RPC باعث شده همه تراکنش‌ها دیده نشوند\n"
                "• یا توکن در آن تاریخ هنوز لانچ نشده بوده"
            )
            return

        lines = [
            f"<b>خریداران توکن در {date_str}</b>\n",
            f"Mint: <code>{mint}</code>\n",
            f"تعداد یافت‌شده: <b>{len(result.buyers)}</b>\n",
            f"Signatures بررسی‌شده: {result.signatures_checked}\n",
            "─" * 20 + "\n",
        ]

        for i, buyer in enumerate(result.buyers[:25], 1):
            amount_str = f"{buyer.amount:,.2f}" if buyer.amount else "N/A"
            lines.append(
                f"{i}. <code>{buyer.wallet}</code>\n"
                f"   مقدار تقریبی: {amount_str}\n"
            )

        if len(result.buyers) > 25:
            lines.append(f"\n... و {len(result.buyers) - 25} کیف‌پول دیگر")

        text = "".join(lines)
        if len(text) > 4000:
            text = text[:4000] + "\n\n...(کوتاه شده)"

        await status_msg.edit_text(text)

    except Exception as e:
        logger.exception("Error in /buyers command")
        await status_msg.edit_text(
            f"خطا در پردازش درخواست:\n<code>{str(e)[:200]}</code>\n\n"
            "اگر از Public RPC استفاده می‌کنید، ممکن است rate limit خورده باشد. "
            "کلید رایگان Helius را امتحان کنید."
        )
