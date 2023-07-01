import os
from common import Config

CONFIG = "docomo_home5g_keep.ini"

config_path = os.path.join(os.path.dirname(__file__), CONFIG)
config = Config(config_path).get_config()

config["continue"]["continue"] = "1"

with open(CONFIG, 'w') as f:
    # 指定したconfigファイルを書き込み
    config.write(f)

import docomo_home5g_keep