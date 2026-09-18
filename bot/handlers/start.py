from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = (
        "سلام 👋\n\n"
        "من ربات <b>Solana Smart Wallet Tracker</b> هستم.\n\n"
        "با من می‌تونی کیف‌پول‌هایی که در یک تاریخ مشخص یک توکن را خریده‌اند پیدا کنی "
        "(برای شناسایی اسمارت‌مانی قبل از پامپ).\n\n"
        "<b>دستور اصلی:</b>\n"
        "<code>/buyers &lt;token_mint&gt; &lt;YYYY-MM-DD&gt;</code>\n\n"
        "<b>مثال:</b>\n"
        "<code>/buyers So11111111111111111111111111111111111111112 2025-06-15</code>\n\n"
        "برای راهنمای بیشتر: /help"
    )
    await message.answer(text)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    text = (
        "<b>راهنمای ربات</b>\n\n"
        "<b>/buyers &lt;mint&gt; &lt;date&gt;</b>\n"
        "لیست کیف‌پول‌هایی که در تاریخ مشخص‌شده توکن را خریده‌اند.\n"
        "تاریخ باید به فرمت <code>YYYY-MM-DD</code> و به وقت UTC باشد.\n\n"
        "<b>نکته مهم:</b>\n"
        "• روی RPC عمومی ممکن است برای توکن‌های پرمعامله کند باشد.\n"
        "• برای عملکرد بهتر، کلید رایگان Helius را در <code>.env</code> قرار دهید.\n\n"
        "سوالی داشتی بپرس."
    )
    await message.answer(text)
