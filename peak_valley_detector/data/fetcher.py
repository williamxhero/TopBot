"""High level stock data fetcher that delegates to pluggable data sources."""

from __future__ import annotations

from typing import Optional, Type, Dict, Union

import pandas as pd

from .sources import BaseDataSource, SOURCE_REGISTRY
from ..config import get_global_config


class StockDataFetcher:
    """Facade class for fetching stock data from various sources."""

    def __init__(
        self,
        source: Optional[str] = None,
        source_config: Optional[Dict[str, str]] = None,
        default_source: Optional[str] = None,
        token: Optional[str] = None,
        use_config_file: bool = True,
    ):
        """Create data fetcher.
        
        Parameters
        ----------
        source: 单一数据源名称，对应 ``SOURCE_REGISTRY``（兼容旧接口）
        source_config: 各个API使用的数据源配置字典，例如 {"daily": "akshare", "60min": "myquant"}
        default_source: 默认数据源，当source_config中没有指定时使用
        token: 掘金量化接口 token（某些数据源可能需要）
        use_config_file: 是否尝试从配置文件读取配置
        """
        # 尝试从配置文件读取配置
        config = get_global_config() if use_config_file else None
        
        # 设置token：优先使用传入的token，否则从配置文件读取
        if token is not None:
            self._token = token
        elif config and config.has_config():
            # 从配置文件获取token（默认使用myquant token）
            self._token = config.get_token('myquant')
        else:
            self._token = None
        
        # 设置数据源配置
        # 兼容旧接口：如果传入了source参数，则所有API都使用这个数据源
        if source is not None:
            if source_config is not None:
                raise ValueError("不能同时指定 source 和 source_config 参数")
            self._source_config = {
                "daily": source,
                "weekly": source,
                "60min": source,
                "hist": source,
            }
        elif source_config is not None:
            # 验证所有配置的数据源都存在
            for period, src in source_config.items():
                if src not in SOURCE_REGISTRY:
                    raise ValueError(f"Unsupported data source: {src}")
            self._source_config = source_config.copy()
        elif config and config.has_config():
            # 从配置文件读取数据源配置
            file_source_config = config.get_source_config()
            # 验证配置文件中的数据源
            for period, src in file_source_config.items():
                if src not in SOURCE_REGISTRY:
                    raise ValueError(f"配置文件中不支持的数据源: {src}")
            self._source_config = file_source_config
        else:
            # 如果都没指定，使用空配置
            self._source_config = {}
        
        # 设置默认数据源：优先使用传入的，否则从配置文件读取，最后默认akshare
        if default_source is not None:
            self._default_source = default_source
        elif config and config.has_config():
            self._default_source = config.get_default_source()
        else:
            self._default_source = "akshare"
        
        # 验证默认数据源
        if self._default_source not in SOURCE_REGISTRY:
            raise ValueError(f"Unsupported default data source: {self._default_source}")
    
    def _get_source_instance(self, symbol: str, api_type: str) -> BaseDataSource:
        """获取指定API类型的数据源实例."""
        source_name = self._source_config.get(api_type, self._default_source)
        source_cls = SOURCE_REGISTRY[source_name]
        return source_cls(symbol, token=self._token)
    
    def get_hist(
        self,
        symbol: str,
        period: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """通用历史行情抓取（复权收盘/最高/最低）.
        
        Parameters
        ----------
        symbol: 股票代码，如 "000001"
        period: 时间周期
        start_date: 开始日期
        end_date: 结束日期
        """
        source_instance = self._get_source_instance(symbol, "hist")
        df = source_instance.get_hist(
            period,
            start_date=start_date,
            end_date=end_date,
        )
        return df
    
    def get_daily(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取日线数据
        
        Parameters
        ----------
        symbol: 股票代码，如 "000001"
        start_date: 开始日期
        end_date: 结束日期
        """
        source_instance = self._get_source_instance(symbol, "daily")
        return source_instance.get_hist("daily", start_date=start_date, end_date=end_date)
    
    def get_weekly(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.Series:
        """获取周线收盘价数据
        
        Parameters
        ----------
        symbol: 股票代码，如 "000001"
        start_date: 开始日期
        end_date: 结束日期
        """
        daily = self.get_daily(symbol, start_date=start_date, end_date=end_date)
        return daily["close"].resample("W-FRI").last()
    
    def get_60min(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取60分钟K线数据.
        
        Parameters
        ----------
        symbol: 股票代码，如 "000001"
        start_date: 开始日期
        end_date: 结束日期
        """
        source_instance = self._get_source_instance(symbol, "60min")
        return source_instance.get_60min(
            start_date=start_date,
            end_date=end_date,
        )
