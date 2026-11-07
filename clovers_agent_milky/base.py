if not __package__:
    raise RuntimeError("插件路径只能作为模块导入。")

from clovers_agent import AgentTools, PLUGIN
from milky import AsyncMilkyClient
from .config import Config
from .constants import CHAT_UTILS, CHAT_UTILS_DESC

TOOLS = AgentTools()
CONFIG = Config.sync_config(__package__)
on_onebot_v11 = TOOLS.create_category(CHAT_UTILS, CHAT_UTILS_DESC)
milky = AsyncMilkyClient(CONFIG.url, CONFIG.token)
PLUGIN.shutdown(milky.close)
