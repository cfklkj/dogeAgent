"""
日志模块 - 为 dogeAgent 提供统一的日志功能
支持控制台输出、文件记录、日志轮转
注意：日志不会污染标准输出，确保 JSON 通信正常
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from datetime import datetime

# 日志格式配置
CONSOLE_FORMAT = "[%(levelname)s] %(name)s: %(message)s"
FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
CONSOLE_DATE_FORMAT = "%H:%M:%S"
FILE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

class DogeLogger:
    """
    Doge 日志类
    提供统一的日志管理功能
    注意：日志输出到 stderr，避免污染 stdout（用于 JSON 通信）
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        name: str = "dogeAgent",
        level: str = "INFO",
        log_dir: str = "logs",
        console_output: bool = True,
        file_output: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 7,
    ):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志文件目录
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的日志文件数量
        """
        if DogeLogger._initialized:
            return
        
        self.name = name
        self.level = LOG_LEVELS.get(level.upper(), logging.INFO)
        self.log_dir = Path(log_dir)
        self.console_output = console_output
        self.file_output = file_output
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 添加控制台处理器（输出到 stderr，避免污染 stdout）
        if self.console_output:
            self._add_console_handler()
        
        # 添加文件处理器
        if self.file_output:
            self._add_file_handler()
        
        DogeLogger._initialized = True
    
    def _add_console_handler(self):
        """添加控制台处理器（输出到 stderr）"""
        # 重要：输出到 stderr，避免影响 stdout 的 JSON 通信
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(self.level)
        
        # 设置格式
        formatter = logging.Formatter(
            CONSOLE_FORMAT,
            datefmt=CONSOLE_DATE_FORMAT
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """添加文件处理器"""
        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成日志文件名（按日期）
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"{self.name}_{timestamp}.log"
        
        # 创建轮转文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.level)
        
        # 设置格式
        formatter = logging.Formatter(
            FILE_FORMAT,
            datefmt=FILE_DATE_FORMAT
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # 记录日志文件路径
        self.logger.info(f"Log file: {log_file}")
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """
        获取子日志器
        
        Args:
            name: 子日志器名称后缀
    
        Returns:
            logging.Logger 实例
        """
        if name:
            return logging.getLogger(f"{self.name}.{name}")
        return self.logger
    
    def set_level(self, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别
        """
        self.level = LOG_LEVELS.get(level.upper(), logging.INFO)
        for handler in self.logger.handlers:
            handler.setLevel(self.level)
    
    def debug(self, msg: str):
        self.logger.debug(msg)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str, exc_info: bool = False):
        if exc_info:
            self.logger.error(msg, exc_info=True)
        else:
            self.logger.error(msg)
    
    def critical(self, msg: str, exc_info: bool = False):
        if exc_info:
            self.logger.critical(msg, exc_info=True)
        else:
            self.logger.critical(msg)
    
    def exception(self, msg: str):
        self.logger.exception(msg)


# 全局日志器实例
_doge_logger: Optional[DogeLogger] = None

def get_doge_logger(
    name: str = "dogeAgent",
    level: str = "INFO",
    log_dir: str = "logs",
    console_output: bool = True,
    file_output: bool = True,
) -> DogeLogger:
    """
    获取全局 Doge 日志器实例
    
    Args:
        name: 日志器名称
        level: 日志级别
        log_dir: 日志文件目录
        console_output: 是否输出到控制台
        file_output: 是否输出到文件
    
    Returns:
        DogeLogger 实例
    """
    global _doge_logger
    if _doge_logger is None:
        _doge_logger = DogeLogger(
            name=name,
            level=level,
            log_dir=log_dir,
            console_output=console_output,
            file_output=file_output,
        )
    return _doge_logger

def get_logger(name: str = None) -> logging.Logger:
    """
    获取子日志器
    
    Args:
        name: 子日志器名称后缀
    
    Returns:
        logging.Logger 实例
    """
    logger = get_doge_logger()
    return logger.get_logger(name)

# 便捷函数
def debug(msg: str):
    get_doge_logger().debug(msg)

def info(msg: str):
    get_doge_logger().info(msg)

def warning(msg: str):
    get_doge_logger().warning(msg)

def error(msg: str, exc_info: bool = False):
    get_doge_logger().error(msg, exc_info=exc_info)

def critical(msg: str, exc_info: bool = False):
    get_doge_logger().critical(msg, exc_info=exc_info)

def exception(msg: str):
    get_doge_logger().exception(msg)

# 模块级别的便捷日志器
class ModuleLogger:
    """模块级日志器，自动添加模块名前缀"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = get_doge_logger().get_logger(module_name)
    
    def debug(self, msg: str):
        self.logger.debug(f"[{self.module_name}] {msg}")
    
    def info(self, msg: str):
        self.logger.info(f"[{self.module_name}] {msg}")
    
    def warning(self, msg: str):
        self.logger.warning(f"[{self.module_name}] {msg}")
    
    def error(self, msg: str, exc_info: bool = False):
        if exc_info:
            self.logger.error(f"[{self.module_name}] {msg}", exc_info=True)
        else:
            self.logger.error(f"[{self.module_name}] {msg}")
    
    def critical(self, msg: str, exc_info: bool = False):
        if exc_info:
            self.logger.critical(f"[{self.module_name}] {msg}", exc_info=True)
        else:
            self.logger.critical(f"[{self.module_name}] {msg}")

def create_module_logger(module_name: str) -> ModuleLogger:
    """
    创建模块日志器
    
    Args:
        module_name: 模块名称
    
    Returns:
        ModuleLogger 实例
    """
    return ModuleLogger(module_name)
