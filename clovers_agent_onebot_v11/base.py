if not __package__:
    raise RuntimeError("插件路径只能作为模块导入。")

from clovers_agent import AgentTools
from .config import Config
from .constants import GROUP_UTILS, GROUP_UTILS_DESC

TOOLS = AgentTools()
CONFIG = Config.sync_config(__package__)
on_onebot_v11 = TOOLS.create_category(GROUP_UTILS, GROUP_UTILS_DESC)
