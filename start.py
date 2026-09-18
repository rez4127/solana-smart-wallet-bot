from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = (
        "3D'E =K\n\n"
        "EF 1('* <b>Solana Smart Wallet Tracker</b> G3*E.\n\n"
        "(' EF EÌ*HFÌ ©ÌA~HDG'ÌÌ ©G /1 Ì© *'1Ì. E4.5 Ì© *H©F 1' .1Ì/G'F/ ~Ì/' ©FÌ "
        "((1'Ì 4F'3'ÌÌ '3E'1*E'FÌ B(D '2 ~'E~).\n\n"
        "<b>/3*H1 '5DÌ:</b>\n"
        "<code>/buyers &lt;token_mint&gt; &lt;YYYY-MM-DD&gt;</code>\n\n"
        "<b>E+'D:</b>\n"
        "<code>/buyers So11111111111111111111111111111111111111112 2025-06-15</code>\n\n"
        "(1'Ì 1'GFE'Ì (Ì4*1: /help"
    )
    await message.answer(text)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    text = (
        "<b>1'GFE'Ì 1('*</b>\n\n"
        "<b>/buyers &lt;mint&gt; &lt;date&gt;</b>\n"
        "DÌ3* ©ÌA~HDG'ÌÌ ©G /1 *'1Ì. E4.54/G *H©F 1' .1Ì/G'F/.\n"
        "*'1Ì. ('Ì/ (G A1E* <code>YYYY-MM-DD</code> H (G HB* UTC ('4/.\n\n"
        "<b>F©*G EGE:</b>\n"
        "" 1HÌ RPC 9EHEÌ EE©F '3* (1'Ì *H©FG'Ì ~1E9'EDG ©F/ ('4/.\n"
        "" (1'Ì 9ED©1/ (G*1 ©DÌ/ 1'Ì¯'F Helius 1' /1 <code>.env</code> B1'1 /GÌ/.\n\n"
        "3H'DÌ /'4*Ì (~13."
    )
    await message.answer(text)
