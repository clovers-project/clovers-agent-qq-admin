import asyncio
from clovers_agent import CloversAgent, Turn, Event
from clovers_agent.constants import ON_CHAT, HIDDEN_CATEGORY
from .base import TOOLS, CONFIG, on_onebot_v11

from typing import cast

OWNER_GROUPS = set(CONFIG.onwer_groups)
if OWNER_GROUPS:
    URL = CONFIG.url.rstrip("/")
    TOKEN = CONFIG.token
    TOOLIST = "set_group_admin", "set_special_title"

    @TOOLS.on_intro(ON_CHAT)
    @on_onebot_v11
    async def _(agent: CloversAgent, turn: Turn, event: Event):
        group_id = event.group_id
        if group_id and group_id in OWNER_GROUPS:
            turn.extend_tools(agent.tool_manifest[x] for x in TOOLIST)
        return ""

    @TOOLS.register(
        "set_group_admin",
        "为用户 @ 的成员设置或取消管理员权限",
        {"enable": {"type": "boolean", "description": "设置/取消"}},
        category=HIDDEN_CATEGORY,
    )
    async def _(agent: CloversAgent, turn: Turn, event: Event, enable: bool):
        permission = cast(int, await event.call("permission"))  # type: ignore
        if permission < 2:
            return "只有群主或拥有足够权限的用户可以设置管理员"
        group_id = event.group_id
        if not group_id:
            return "当前对话不是群聊"
        if not event.at:
            return "操作失败：该条消息没有 @ 任何用户"
        at_users = tuple(int(u) for u in event.at)
        group_id = int(group_id)
        header = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
        url = f"{URL}/set_group_admin"
        post = agent.async_client.post
        tasks = (post(url, json={"group_id": group_id, "user_id": u, "enable": enable}, headers=header) for u in at_users)
        resps = await asyncio.gather(*tasks)
        for resp in resps:
            resp.raise_for_status()
        if enable:
            return f"已为 {len(at_users)} 个用户设置管理员权限"
        else:
            return f"已取消 {len(at_users)} 个用户的管理员权限"
