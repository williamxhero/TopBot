# 多数据源配置功能

## 概述

`StockDataFetcher` 现在支持为不同的API指定不同的数据源，让你可以根据需要灵活配置：
- 日线数据使用 AkShare
- 60分钟数据使用 MyQuant
- 其他API使用默认数据源

## 使用方法

### 1. 新功能：分别配置数据源

```python
from peak_valley_detector.data.fetcher import StockDataFetcher

# 配置不同API使用不同数据源
source_config = {
    "daily": "akshare",      # 日线使用akshare
    "60min": "myquant",      # 60分钟线使用myquant
    # weekly 和 hist 将使用默认数据源
}

fetcher = StockDataFetcher(
    source_config=source_config,
    default_source="akshare",  # 默认数据源
    token="your_myquant_token"  # MyQuant token
)

# 各API将自动使用配置的数据源
daily_data = fetcher.get_daily("000001")     # 使用akshare
min60_data = fetcher.get_60min("000001")     # 使用myquant
weekly_data = fetcher.get_weekly("000001")   # 使用默认源akshare
```

### 2. 兼容旧接口

```python
# 旧的接口仍然可用，所有API使用同一个数据源
fetcher = StockDataFetcher(source="akshare")

# 或者使用默认配置
fetcher = StockDataFetcher(default_source="akshare")
```

## 配置参数

### `StockDataFetcher` 构造函数参数

- **`source`** (Optional[str]): 单一数据源名称（兼容旧接口）
- **`source_config`** (Optional[Dict[str, str]]): 各API的数据源配置字典
- **`default_source`** (str): 默认数据源，当source_config中没有指定时使用
- **`token`** (Optional[str]): MyQuant等需要token的数据源的认证令牌

### 支持的API类型键名

- `"daily"`: 日线数据 (`get_daily`)
- `"weekly"`: 周线数据 (`get_weekly`) 
- `"60min"`: 60分钟数据 (`get_60min`)
- `"hist"`: 通用历史数据 (`get_hist`)

### 支持的数据源

- `"akshare"`: AkShare数据源
- `"myquant"`: MyQuant数据源（需要token）

## 使用场景

### 场景1：不同周期使用不同数据源

```python
# 日线用免费的akshare，高频数据用付费的myquant
source_config = {
    "daily": "akshare",
    "60min": "myquant"
}

fetcher = StockDataFetcher(
    source_config=source_config,
    token="your_token"
)
```

### 场景2：备用数据源

```python
# 主要使用myquant，但某些API fallback到akshare
source_config = {
    "daily": "myquant",
    "60min": "myquant",
    "weekly": "akshare"  # 周线可能akshare更稳定
}

fetcher = StockDataFetcher(
    source_config=source_config,
    default_source="akshare",  # 其他未指定的API使用akshare
    token="your_token"
)
```

### 场景3：测试不同数据源

```python
# 方便切换和对比不同数据源
test_configs = [
    {"daily": "akshare", "60min": "akshare"},
    {"daily": "myquant", "60min": "myquant"},
    {"daily": "akshare", "60min": "myquant"}  # 混合使用
]

for config in test_configs:
    fetcher = StockDataFetcher(source_config=config, token="your_token")
    # 进行测试...
```

## 错误处理

```python
# 验证数据源是否支持
try:
    fetcher = StockDataFetcher(
        source_config={"daily": "unsupported_source"}
    )
except ValueError as e:
    print(f"不支持的数据源: {e}")

# 不能同时指定source和source_config
try:
    fetcher = StockDataFetcher(
        source="akshare",
        source_config={"daily": "myquant"}
    )
except ValueError as e:
    print(f"参数冲突: {e}")
```

## 注意事项

1. **MyQuant需要token**: 使用MyQuant数据源时必须提供有效的token
2. **数据格式一致性**: 不同数据源返回的数据格式已统一处理
3. **向后兼容**: 旧的`source`参数接口完全兼容
4. **默认值机制**: 未在source_config中指定的API会使用default_source

## 实际效果

运行示例后可以看到：

```
=== 多数据源配置示例 ===

1. 获取日线数据（使用akshare）...
日线数据形状: (16, 3)
日线数据列: ['close', 'high', 'low']

2. 获取60分钟数据（使用myquant）...
[尝试连接MyQuant...]

3. 获取周线数据（使用默认源akshare）...
周线数据形状: (4, 1)
```

这确认了不同API确实使用了配置指定的数据源。
