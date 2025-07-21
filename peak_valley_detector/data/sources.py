"""Data source implementations for StockDataFetcher."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import akshare as ak
import pandas as pd

try:
    from gm.api import history as gm_history, set_token as gm_set_token
except Exception:  # pragma: no cover - optional
    gm_history = None
    gm_set_token = None


class BaseDataSource(ABC):
    """Abstract base class for stock data sources."""

    def __init__(
        self,
        symbol: str,
        token: Optional[str] = None,
    ):
        self.symbol = symbol
        self.token = token

    @abstractmethod
    def get_hist(
        self,
        period: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Return historical OHLC data for the given period."""

    @abstractmethod
    def get_60min(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Return 60 minute bar data."""


class AkShareSource(BaseDataSource):
    """AkShare based data source."""

    def get_hist(
        self,
        period: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        df_kwargs = {
            "symbol": self.symbol,
            "period": period,
            "adjust": "qfq",
        }
        # 转换日期格式为 AkShare 需要的格式 (YYYYMMDD)
        if start_date:
            df_kwargs["start_date"] = start_date.replace("-", "")
        if end_date:
            df_kwargs["end_date"] = end_date.replace("-", "")
        
        df_raw = ak.stock_zh_a_hist(**df_kwargs)
        df = (
            df_raw[["日期", "收盘", "最高", "最低"]]
            .rename(
                columns={"日期": "date", "收盘": "close", "最高": "high", "最低": "low"}
            )
            .copy()
        )
        df["date"] = pd.to_datetime(df["date"])
        return df.set_index("date").sort_index()

    def get_60min(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        df_kwargs = {
            "symbol": self.symbol,
            "period": "60",
            "adjust": "qfq",
        }

        if start_date:
            df_kwargs["start_date"] = start_date
        if end_date:
            df_kwargs["end_date"] = end_date
        h1_raw = ak.stock_zh_a_hist_min_em(**df_kwargs)
        h1_raw["datetime"] = pd.to_datetime(h1_raw["时间"])
        return h1_raw.set_index("datetime").sort_index()


class MyQuantSource(BaseDataSource):
    """掘金量化数据源."""

    def __init__(
        self,
        symbol: str,
        token: Optional[str] = None,
    ):
        if gm_history is None:
            raise ImportError("MyQuant 数据接口不可用，请先安装 gm.api 并配置 token")
        if gm_set_token and token:
            gm_set_token(token)
        super().__init__(symbol, token=token)

    def get_hist(
        self,
        period: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        freq_map = {"daily": "1d", "weekly": "1w", "60min": "60m"}
        
        # 转换股票代码格式 - MyQuant需要交易所前缀
        symbol = self.symbol
        if not symbol.startswith(('SZSE.', 'SHSE.')):
            if symbol.startswith('00'):
                symbol = f"SZSE.{symbol}"  # 深圳证券交易所
            elif symbol.startswith('60'):
                symbol = f"SHSE.{symbol}"  # 上海证券交易所
        
        hist_kwargs = {
            "symbol": symbol,
            "frequency": freq_map.get(period, "1d"),
            "fields": "close,high,low,eob",  # 添加 eob 字段获取日期
            "adjust": 1,  # 1 = 前复权 (qfq)
        }

        if start_date:
            hist_kwargs["start_time"] = start_date
        if end_date:
            hist_kwargs["end_time"] = end_date
            
        # MyQuant 返回的是 list of dict，需要转换为 DataFrame
        data_list = gm_history(**hist_kwargs)
        if not data_list:
            # 返回空的 DataFrame
            return pd.DataFrame(columns=['close', 'high', 'low'], 
                              index=pd.DatetimeIndex([], name='date'))
        
        # 转换为 DataFrame
        df = pd.DataFrame(data_list)
        df = df.rename(columns={"eob": "date"})
        df["date"] = pd.to_datetime(df["date"])
        return df.set_index("date").sort_index()

    def get_60min(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        # 转换股票代码格式 - MyQuant需要交易所前缀
        symbol = self.symbol
        if not symbol.startswith(('SZSE.', 'SHSE.')):
            if symbol.startswith('00'):
                symbol = f"SZSE.{symbol}"  # 深圳证券交易所
            elif symbol.startswith('60'):
                symbol = f"SHSE.{symbol}"  # 上海证券交易所
        
        hist_kwargs = {
            "symbol": symbol,
            "frequency": "60m",
            "fields": "close,high,low,eob",  # 添加 eob 字段获取日期
            "adjust": 1,  # 1 = 前复权 (qfq)
        }

        if start_date:
            hist_kwargs["start_time"] = start_date
        if end_date:
            hist_kwargs["end_time"] = end_date

        # MyQuant 返回的是 list of dict，需要转换为 DataFrame
        data_list = gm_history(**hist_kwargs)
        if not data_list:
            # 返回空的 DataFrame
            return pd.DataFrame(columns=['close', 'high', 'low'], 
                              index=pd.DatetimeIndex([], name='datetime'))
        
        # 转换为 DataFrame
        df = pd.DataFrame(data_list)
        df = df.rename(columns={"eob": "datetime"})
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df.set_index("datetime").sort_index()


SOURCE_REGISTRY = {
    "akshare": AkShareSource,
    "myquant": MyQuantSource,
}
