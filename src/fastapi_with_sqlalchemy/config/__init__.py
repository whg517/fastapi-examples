"""
Config center.
"""

import os
import sys
from pathlib import Path

from dynaconf import Dynaconf

base_dir = Path(__file__).parent.parent

user_local = Path(Path.home()) / '.local'

os.makedirs(user_local, exist_ok=True)

user_local_path = user_local / 'fastapi_with_sqlalchemy'

# 指定绝对路径加载默认配置
settings_files = [
    Path(__file__).parent / 'settings.yml',
]

external_files = [
    Path(sys.prefix) / 'etc' / 'fastapi_with_sqlalchemy', 'settings.yml'
]

settings = Dynaconf(
    envvar_prefix="FASTAPI_WITH_SQLALCHEMY",  # 环境变量前缀。设置`SPIDERKEEPER_FOO='bar'`，使用`settings.FOO`
    settings_files=settings_files,
    environments=False,  # 启用多层次日志，支持 dev, pro
    load_dotenv=True,  # 加载 .env
    env_switcher="FASTAPI_WITH_SQLALCHEMY_ENV",  # 用于切换模式的环境变量名称 SPIDERKEEPER_ENV=production
    lowercase_read=False,  # 禁用小写访问， settings.name 是不允许的
    includes=external_files,  # 自定义配置覆盖默认配置
    base_dir=base_dir,  # 编码传入配置
)
