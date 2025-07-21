"""配置管理模块"""

import os
import yaml
from typing import Dict, Optional, Any
from pathlib import Path


class DataSourceConfig:
    """数据源配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Parameters
        ----------
        config_file : Optional[str]
            配置文件路径，如果不指定则按优先级查找默认配置文件
        """
        self.config_file = self._find_config_file(config_file)
        self.config = self._load_config()
    
    def _find_config_file(self, config_file: Optional[str] = None) -> Optional[str]:
        """查找配置文件"""
        if config_file and os.path.exists(config_file):
            return config_file
        
        # 按优先级查找配置文件
        possible_files = [
            "data_sources_config.yaml",
            "data_sources_config.yml", 
            "config.yaml",
            "config.yml",
            "local_config.yaml",
            "local_config.yml"
        ]
        
        # 在当前目录和项目根目录查找
        search_dirs = [
            os.getcwd(),
            Path(__file__).parent.parent,  # 项目根目录
        ]
        
        for search_dir in search_dirs:
            for filename in possible_files:
                filepath = os.path.join(search_dir, filename)
                if os.path.exists(filepath):
                    return filepath
        
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_file:
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"警告：无法加载配置文件 {self.config_file}: {e}")
            return {}
    
    def get_source_config(self) -> Dict[str, str]:
        """获取数据源配置"""
        return self.config.get('source_config', {})
    
    def get_default_source(self) -> str:
        """获取默认数据源"""
        return self.config.get('default_source', 'akshare')
    
    def get_token(self, source: str = 'myquant') -> Optional[str]:
        """获取指定数据源的token"""
        tokens = self.config.get('tokens', {})
        return tokens.get(source)
    
    def get_all_tokens(self) -> Dict[str, str]:
        """获取所有token"""
        return self.config.get('tokens', {})
    
    def has_config(self) -> bool:
        """检查是否有有效的配置文件"""
        return self.config_file is not None and bool(self.config)
    
    def get_config_file_path(self) -> Optional[str]:
        """获取当前配置文件路径"""
        return self.config_file
    
    def get_full_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config.copy()


# 全局配置实例
_global_config = None

def get_global_config() -> DataSourceConfig:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = DataSourceConfig()
    return _global_config

def reload_config(config_file: Optional[str] = None):
    """重新加载配置"""
    global _global_config
    _global_config = DataSourceConfig(config_file)
