# 配置文件使用指南

## 快速开始

### 1. 创建配置文件

复制模板文件并配置你的token：

```bash
cp data_sources_config.yaml.example data_sources_config.yaml
```

然后编辑 `data_sources_config.yaml` 文件，填入你的真实token。

### 2. 使用方式

```python
from peak_valley_detector.data.fetcher import StockDataFetcher

# 自动从配置文件读取所有配置（推荐方式）
fetcher = StockDataFetcher()

# 获取数据 - 自动根据配置文件使用相应的数据源
daily_data = fetcher.get_daily("000001")     # 使用配置文件中的daily数据源
min60_data = fetcher.get_60min("000001")     # 使用配置文件中的60min数据源
```

## 配置文件说明

### 配置文件格式 (`data_sources_config.yaml`)

```yaml
# 默认数据源
default_source: "akshare"

# 各API使用的数据源配置
source_config:
  daily: "akshare"      # 日线数据使用akshare
  weekly: "akshare"     # 周线数据使用akshare  
  60min: "myquant"      # 60分钟数据使用myquant
  hist: "akshare"       # 通用历史数据使用akshare

# 数据源认证token
tokens:
  myquant: "YOUR_MYQUANT_TOKEN_HERE"  # 替换为你的MyQuant token
```

### 安全特性

1. **配置文件已添加到 `.gitignore`** - 不会被提交到版本控制
2. **自动降级处理** - 其他用户没有配置文件时会使用默认配置
3. **Token隐藏显示** - 日志中只显示token的部分字符
4. **覆盖机制** - 可以手动覆盖配置文件的设置

## 优先级规则

配置的优先级（高到低）：

1. **手动传入的参数** - 直接传给`StockDataFetcher`的参数
2. **配置文件设置** - `data_sources_config.yaml`中的配置
3. **默认值** - 程序内置的默认配置

## 实际效果

### 有配置文件的用户（你）
```
✓ 找到配置文件: /path/to/data_sources_config.yaml
✓ 默认数据源: akshare
✓ MyQuant token: 5f0ed377bb...ded0aab7a1
✓ 日线数据使用akshare成功获取
✓ 60分钟数据使用myquant（按配置）
```

### 没有配置文件的用户（其他人）
```
⚠ 未找到配置文件，将使用默认配置
✓ 日线数据使用akshare成功获取（降级到免费数据源）
⚠ 60分钟数据无法获取（没有token，但不会报错）
```

## 高级用法

### 手动覆盖配置
```python
# 即使有配置文件，也可以手动覆盖
fetcher = StockDataFetcher(source="akshare")  # 强制全部使用akshare
```

### 禁用配置文件
```python
# 完全不使用配置文件
fetcher = StockDataFetcher(
    use_config_file=False,
    source_config={"daily": "akshare"},
    token="manual_token"
)
```

### 运行示例
```bash
# 查看配置文件功能演示
python examples/config_file_usage.py
```

这样你就可以在本地使用完整功能，而其他用户不会遇到错误，只是功能受限。
