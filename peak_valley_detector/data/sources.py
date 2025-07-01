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

    def __init__(self, symbol: str, start_date: str, token: Optional[str] = None):
        self.symbol = symbol
        self.start_date = start_date
        self.token = token

    @abstractmethod
    def get_hist(self, period: str) -> pd.DataFrame:
        """Return historical OHLC data for the given period."""

    @abstractmethod
    def get_60min(self) -> pd.DataFrame:
        """Return 60 minute bar data."""


class AkShareSource(BaseDataSource):
    """AkShare based data source."""

    def get_hist(self, period: str) -> pd.DataFrame:
        df_raw = ak.stock_zh_a_hist(
            symbol=self.symbol,
            period=period,
            start_date=self.start_date,
            adjust="qfq",
        )
        df = (
            df_raw[["日期", "收盘", "最高", "最低"]]
            .rename(
                columns={"日期": "date", "收盘": "close", "最高": "high", "最低": "low"}
            )
            .copy()
        )
        df["date"] = pd.to_datetime(df["date"])
        return df.set_index("date").sort_index()

    def get_60min(self) -> pd.DataFrame:
        h1_raw = ak.stock_zh_a_hist_min_em(
            symbol=self.symbol,
            period="60",
            adjust="qfq",
        )
        h1_raw["datetime"] = pd.to_datetime(h1_raw["时间"])
        return h1_raw.set_index("datetime").sort_index()


class MyQuantSource(BaseDataSource):
    """掘金量化数据源."""

    def __init__(self, symbol: str, start_date: str, token: Optional[str] = None):
        if gm_history is None:
            raise ImportError("MyQuant 数据接口不可用，请先安装 gm.api 并配置 token")
        if gm_set_token and token:
            gm_set_token(token)
        super().__init__(symbol, start_date, token=token)

    def get_hist(self, period: str) -> pd.DataFrame:
        freq_map = {"daily": "1d", "weekly": "1w", "60min": "60m"}
        df_raw = gm_history(
            symbol=self.symbol,
            start_time=self.start_date,
            frequency=freq_map.get(period, "1d"),
            fields="close,high,low",
            adjust="qfq",
        )
        df = df_raw.rename(columns={"eob": "date"})
        df["date"] = pd.to_datetime(df["date"])
        return df.set_index("date").sort_index()

    def get_60min(self) -> pd.DataFrame:
        df_raw = gm_history(
            symbol=self.symbol,
            start_time=self.start_date,
            frequency="60m",
            fields="close,high,low",
            adjust="qfq",
        )
        df_raw = df_raw.rename(columns={"eob": "datetime"})
        df_raw["datetime"] = pd.to_datetime(df_raw["datetime"])
        return df_raw.set_index("datetime").sort_index()


SOURCE_REGISTRY = {
    "akshare": AkShareSource,
    "myquant": MyQuantSource,
}

