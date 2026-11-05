if not __package__:
    raise RuntimeError("插件路径只能作为模块导入。")

import asyncio
from clovers_agent import CloversAgent, Turn, Event, AgentTools
from clovers_agent.constants import ON_CHAT
from .config import Config

CONFIG = Config.sync_config(__package__)
TOOLS = AgentTools()

URL = CONFIG.url.rstrip("/")
TOKEN = CONFIG.token


@TOOLS.register(
    "set_special_title",
    "为群内成员设置专属头衔。若不填写 title 字段则表示删除该成员的头衔。",
    {"title": {"type": "string"}},
    category=ON_CHAT,
    required=[],
)
async def _(agent: CloversAgent, turn: Turn, event: Event, title: str = ""):
    group_id = event.group_id
    if not group_id:
        return "当前对话不是群聊"
    url = f"{URL}/set_group_special_title"
    header = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
    response = await agent.async_client.post(
        url,
        json={"group_id": int(group_id), "user_id": int(event.user_id), "title": title},
        headers=header,
    )
    response.raise_for_status()
    if title:
        return f"已将 {event.nickname} 的群头衔设置为 {title}"
    else:
        return f"已删除 {event.nickname} 的群头衔"


@TOOLS.register(
    "mute_member",
    "禁言群内通过 @ 指定的一个或多个成员",
    {"duration": {"type": "integer", "description": "禁言时长（秒），0为取消禁言"}},
    category=ON_CHAT,
)
async def _(agent: CloversAgent, turn: Turn, event: Event, duration: int):
    if event.permission < 1:
        return "用户权限不足，无法执行禁言操作"
    group_id = event.group_id
    if not group_id:
        return "当前对话不是群聊"
    if not event.at:
        return "操作失败：该条消息没有 @ 任何用户"
    group_id = int(group_id)
    at_users = tuple(int(u) for u in event.at)
    url = f"{URL}/set_group_ban"
    header = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
    post = agent.async_client.post
    tasks = (post(url, json={"group_id": group_id, "user_id": u, "duration": duration}, headers=header) for u in at_users)
    resps = await asyncio.gather(*tasks)
    for resp in resps:
        resp.raise_for_status()
    if duration > 0:
        return f"已成功为 {len(at_users)} 个用户禁言 {duration} 秒"
    else:
        return f"已成功解除 {len(at_users)} 个用户的禁言"


@TOOLS.register(
    "kick_member",
    "将群内通过 @ 指定的一个或多个成员踢出群聊",
    category=ON_CHAT,
)
async def _(agent: CloversAgent, turn: Turn, event: Event, duration: int):
    if event.permission < 1:
        return "用户权限不足，无法执行踢人操作"
    group_id = event.group_id
    if not group_id:
        return "当前对话不是群聊"
    if not event.at:
        return "操作失败：该条消息没有 @ 任何用户"
    group_id = int(group_id)
    at_users = tuple(int(u) for u in event.at)
    url = f"{URL}/set_group_kick"
    header = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
    post = agent.async_client.post
    tasks = (post(url, json={"group_id": group_id, "user_id": u, "reject_add_request": False}, headers=header) for u in at_users)
    resps = await asyncio.gather(*tasks)
    for resp in resps:
        resp.raise_for_status()
    return f"已将 {len(at_users)} 个用户踢出群聊"


@TOOLS.register(
    "set_group_admin",
    "设置或取消群内通过 @ 指定成员的管理员权限",
    {"enable": {"type": "boolean", "description": "设置/取消"}},
    category=ON_CHAT,
)
async def _(agent: CloversAgent, turn: Turn, event: Event, enable: bool):
    if event.permission < 2:
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
