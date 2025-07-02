"""High level stock data fetcher that delegates to pluggable data sources."""

from __future__ import annotations

from typing import Optional, Type

import pandas as pd

from .sources import BaseDataSource, SOURCE_REGISTRY


class StockDataFetcher:
    """Facade class for fetching stock data from various sources."""

    def __init__(
        self,
        symbol: str,
        source: str = "akshare",
        token: Optional[str] = None,
    ):
        """Create data fetcher.
        Parameters
        ----------
        symbol: 股票代码，如 "000001"
        source: 数据源名称，对应 ``SOURCE_REGISTRY``
        token: 掘金量化接口 token（某些数据源可能需要）
        """
        self.symbol = symbol
        source_cls: Type[BaseDataSource] | None = SOURCE_REGISTRY.get(source)
        if source_cls is None:
            raise ValueError(f"Unsupported data source: {source}")

        self._source = source_cls(symbol, token=token)
    
    def get_hist(
        self,
        period: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """通用历史行情抓取（复权收盘/最高/最低）."""

        df = self._source.get_hist(
            period,

            start_date=start_date,
            end_date=end_date,
        )
        return df
    
    def get_daily(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取日线数据"""
        return self.get_hist("daily", start_date=start_date, end_date=end_date)
    
    def get_weekly(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.Series:
        """获取周线收盘价数据"""
        daily = self.get_daily(start_date=start_date, end_date=end_date)
        return daily["close"].resample("W-FRI").last()
    
    def get_60min(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取60分钟K线数据."""

        return self._source.get_60min(
            start_date=start_date,
            end_date=end_date,
        )
