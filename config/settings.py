"""
全局配置模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 应用配置
APP_NAME = "dogeAgent"
APP_VERSION = "3.0.0"

# 模型配置
DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "nvidia")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# 语音配置
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "true").lower() == "true"
VOICE_ENGINE = os.getenv("VOICE_ENGINE", "edge")  # edge, azure, system

# 天气配置
WEATHER_API = os.getenv("WEATHER_API", "simulated")  # simulated, hefeng, openweather
HEFENG_API_KEY = os.getenv("HEFENG_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 数据存储路径
if os.name == 'nt':  # Windows
    DATA_DIR = Path(os.environ.get('APPDATA', '')) / 'dogeAgent'
else:  # Mac/Linux
    DATA_DIR = Path.home() / '.local' / 'share' / 'dogeAgent'

DATA_DIR.mkdir(exist_ok=True, parents=True)

# 数据库路径
DB_PATH = DATA_DIR / 'doge.db'

# 缓存目录
CACHE_DIR = DATA_DIR / 'cache'
CACHE_DIR.mkdir(exist_ok=True, parents=True)
