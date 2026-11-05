if not __package__:
    raise RuntimeError("插件路径只能作为模块导入。")

import asyncio
from clovers_agent import CloversAgent, Turn, Event, AgentTools
from clovers_agent.constants import ON_CHAT, HIDDEN_CATEGORY
from .config import Config

from typing import cast

CONFIG = Config.sync_config(__package__)
TOOLS = AgentTools()

URL = CONFIG.url.rstrip("/")
TOKEN = CONFIG.token
ADMIN_GROUPS = set(CONFIG.admin_groups)
OWNER_GROUPS = set(CONFIG.onwer_groups)
GROUP_MANAGE = "group_manage"
ADMIN_TOOLIST = "mute_member", "kick_member"
OWNER_TOOLIST = "mute_member", "kick_member", "set_special_title", "set_group_admin"

if ADMIN_GROUPS or OWNER_GROUPS:

    @TOOLS.on_intro(ON_CHAT)
    @TOOLS.create_category(GROUP_MANAGE, "群管理工具")
    async def _(agent: CloversAgent, turn: Turn, event: Event):
        group_id = event.group_id
        if not group_id:
            return ""
        if group_id in OWNER_GROUPS:
            permission = "群主"
            turn.extend_tools(agent.tool_manifest[x] for x in OWNER_TOOLIST)
        elif group_id in ADMIN_GROUPS:
            permission = "管理员"
            turn.extend_tools(agent.tool_manifest[x] for x in ADMIN_TOOLIST)
        else:
            return ""
        return f"""\
你在当前群的权限为 {permission}
当用户提出群管理请求时，直接调用对应工具。工具会自动校验权限并获取消息中 @ 的成员信息，无需自行解析或重复询问。"""

    @TOOLS.register(
        "mute_member",
        "为用户 @ 的成员设置禁言",
        {"duration": {"type": "integer", "description": "禁言时长（秒），0为取消禁言"}},
        category=HIDDEN_CATEGORY,
    )
    async def _(agent: CloversAgent, turn: Turn, event: Event, duration: int):
        permission = cast(int, await event.call("permission"))  # type: ignore
        if permission < 1:
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
        "将用户 @ 的成员移出群聊",
        category=HIDDEN_CATEGORY,
    )
    async def _(agent: CloversAgent, turn: Turn, event: Event, duration: int):
        permission = cast(int, await event.call("permission"))  # type: ignore
        if permission < 1:
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

    @TOOLS.register(
        "set_special_title",
        "为群内成员设置专属头衔。若不填写 title 字段则表示删除该成员的头衔。",
        {"title": {"type": "string", "description": "最长6个字符"}},
        category=HIDDEN_CATEGORY,
        required=[],
    )
    async def _(agent: CloversAgent, turn: Turn, event: Event, title: str = ""):
        if len(title) > 6:
            return "头衔长度不能超过6个字符"
        group_id = event.group_id
        if not group_id:
            return "当前对话不是群聊"
        url = f"{URL}/set_group_special_title"
        header = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
        response = await agent.async_client.post(
            url,
            json={"group_id": int(group_id), "user_id": int(event.user_id), "special_title": title},
            headers=header,
        )
        response.raise_for_status()
        if title:
            return f"已将 {event.nickname} 的群头衔设置为 {title}"
        else:
            return f"已删除 {event.nickname} 的群头衔"
