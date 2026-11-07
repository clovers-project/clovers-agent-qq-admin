import asyncio
from clovers_agent import CloversAgent, Turn, Event
from .base import TOOLS, URL, TOKEN
from .constants import CHAT_UTILS


@TOOLS.register(
    "accept_friend",
    "通过该用户的好友申请",
    category=CHAT_UTILS,
)
async def _(agent: CloversAgent, turn: Turn, event: Event, enable: bool):
    header = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
    url = f"{URL}/get_friend_msg_history"
    payload = {"user_id": int(event.user_id), "message_seq": 0, "count": 20, "reverseOrder": True}
    response = await agent.async_client.post(url, json=payload, headers=header)
    response.raise_for_status()
    messages = response.json()["data"]["messages"]

    return ""


@TOOLS.register(
    "accept_group_invite",
    "通过用户的加群邀请",
    category=CHAT_UTILS,
)
async def _(agent: CloversAgent, turn: Turn, event: Event, enable: bool):
    return ""
