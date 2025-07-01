# Peak Valley Detector 文档

## 快速开始

### 安装

```bash
# 从源码安装
pip install -e .

# 或者直接安装依赖
pip install -r requirements.txt
```

### 基本使用

```python
from peak_valley_detector import (
    StockDataFetcher,
    HybridChangePointDetector,
    MultiLayerVisualizer
)

# 获取股票数据
data_fetcher = StockDataFetcher(
    "000001",
    "2024-06-01",
    end_date=None,
    source="akshare",
)
weekly_data = data_fetcher.get_weekly()

# 变点检测
detector = HybridChangePointDetector()
changepoints = detector.detect_comprehensive(weekly_data.values)

# 可视化结果
visualizer = MultiLayerVisualizer()
visualizer.plot_changepoint_analysis(weekly_data, changepoints)
```

## API 文档

### 核心模块 (core)

#### HybridChangePointDetector
混合变点检测器，集成多种算法：
- `detect_comprehensive()`: 综合检测方法
- `detect_ruptures_dynp()`: Ruptures Dynp 算法
- `detect_sd_bocpd()`: Score-Driven BOCPD 算法

#### ExtremaClassifier
极值点分类器：
- `classify_changepoints()`: 将变点分类为峰值或谷值
- `classify_extrema()`: 单点极值分类

### 数据模块 (data)

#### StockDataFetcher
股票数据获取器：
- `get_daily()`: 获取日线数据
- `get_weekly()`: 获取周线数据
- `get_60min()`: 获取60分钟数据
- 所有函数支持 `start_date` 与 `end_date` 参数，可覆盖初始化设置
- `source` 参数在插件式架构下选择数据接口，默认支持 `akshare` 与 `myquant`，可扩展

### 可视化模块 (visualization)

#### MultiLayerVisualizer
多层次可视化器：
- `plot_multi_layer_results()`: 绘制综合结果
- `plot_changepoint_analysis()`: 绘制变点分析
- `plot_score_driven_diagnostics()`: 绘制模型诊断

## 算法说明

### Score-Driven BOCPD
基于 GAS (Generalized Autoregressive Score) 模型的贝叶斯在线变点检测算法。

核心特点：
- 学生t分布建模
- 动态方差更新
- 贝叶斯推断框架

### Ruptures 集成
集成专业变点检测库 Ruptures：
- Dynamic Programming (Dynp)
- BottomUp 算法
- 多种代价函数

## 示例

查看 `examples/` 目录获取更多使用示例。

## 高级参数调节

在需要更快速的峰谷确认时，可以调整 `ExtremaClassifier.classify_changepoints`
 的 `window` 和 `check_right` 参数：

```python
peaks, troughs = ExtremaClassifier.classify_changepoints(
    weekly_data,
    changepoints,
    window=0,        # 只检查左侧数据
    check_right=False
)
```

## 测试

```bash
# 运行测试
pytest tests/

# 运行特定测试
pytest tests/test_core.py -v
