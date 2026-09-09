from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot import handle_message


@pytest.mark.asyncio
async def test_replies_to_invalid_message():
    update = MagicMock()
    update.message.text = "hello"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}
    await handle_message(update, context)
    update.message.reply_text.assert_awaited_once()
    assert "رابط TikTok" in update.message.reply_text.await_args.args[0]
