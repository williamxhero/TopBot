# 多层次峰谷检测系统 - 严谨 Score-Driven BOCPD 版本

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/example/peak-valley-detector)

## 项目概述

本项目实现了基于严谨 Score-Driven BOCPD (Bayesian Online Change Point Detection) 方法的多层次股票峰谷检测系统。采用学术级别的变点检测算法和专业库集成，提供模块化的Python包架构。

## 核心技术

- **GAS (Generalized Autoregressive Score) 模型**: 基于学生t分布的动态参数更新
- **贝叶斯在线变点检测**: 运行长度分布的贝叶斯推断
- **Ruptures 专业库**: 集成动态规划、BottomUp等先进算法
- **多层次融合**: 宏观(周线)、中观(日线)、微观(60分钟)的综合分析

## 项目结构

```
TopBot_proj/
├── peak_valley_detector/          # 主要Python包
│   ├── __init__.py               # 包初始化
│   ├── core/                     # 核心算法模块
│   │   ├── __init__.py
│   │   ├── score_driven_bocpd.py # Score-Driven BOCPD算法
│   │   └── changepoint_detector.py # 变点检测器
│   ├── data/                     # 数据获取模块
│   │   ├── __init__.py
│   │   └── fetcher.py           # 股票数据获取器
│   ├── visualization/            # 可视化模块
│   │   ├── __init__.py
│   │   └── visualizer.py        # 多层次可视化器
│   └── utils/                    # 工具函数模块
│       └── __init__.py
├── tests/                        # 测试文件
│   ├── __init__.py
│   └── test_core.py             # 核心模块测试
├── examples/                     # 使用示例
│   └── basic_usage.py           # 基本使用示例
├── docs/                         # 文档目录
│   └── README.md                # 详细文档
├── main.py                       # 主程序入口
├── setup.py                      # 安装配置
├── pyproject.toml               # 现代Python项目配置
├── requirements.txt              # 依赖库列表
├── .gitignore                   # Git忽略文件
└── README.md                     # 项目说明
```

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/example/peak-valley-detector.git
cd peak-valley-detector

# 安装依赖
pip install -r requirements.txt

# 或者以开发模式安装包
pip install -e .
```

### 基本使用

```python
from peak_valley_detector import (
    StockDataFetcher,
    HybridChangePointDetector,
    ExtremaClassifier,
    MultiLayerVisualizer,
    create_summary_report
)

# 1. 数据获取
data_fetcher = StockDataFetcher(
    "000001",
    "2024-06-01",
    end_date=None,  # 可选结束日期
    source="akshare",
)
weekly_data = data_fetcher.get_weekly()

# 2. 变点检测
detector = HybridChangePointDetector()
changepoints = detector.detect_comprehensive(weekly_data.values)

# 3. 峰谷分类
classifier = ExtremaClassifier()
peaks, troughs = classifier.classify_changepoints(
    weekly_data,
    changepoints,
    window=1,        # 较小窗口更快确认
    check_right=False  # 仅检查左侧，提前锁定极值
)

# 4. 可视化
visualizer = MultiLayerVisualizer()
visualizer.plot_changepoint_analysis(weekly_data, changepoints)
```

### 运行完整示例

```bash
# 运行主程序
python main.py

# 或运行示例
python examples/basic_usage.py
```

## 模块说明

### 核心模块 (`peak_valley_detector.core`)

#### `HybridChangePointDetector`
混合变点检测器，集成多种专业算法：
- `detect_comprehensive()`: 综合检测方法，自动选择最佳算法
- `detect_ruptures_dynp()`: Ruptures Dynp 动态规划算法
- `detect_sd_bocpd()`: Score-Driven BOCPD 算法
- `detect_volatility_based()`: 基于波动率的简单检测

#### `ExtremaClassifier`
极值点分类器：
- `classify_changepoints()`: 将变点分类为峰值或谷值
- `classify_extrema()`: 单点极值分类

#### `ScoreDrivenModel`
GAS模型实现：
- 基于学生t分布的得分函数
- 动态方差更新方程
- 贝叶斯推断框架

### 数据模块 (`peak_valley_detector.data`)

#### `StockDataFetcher`
股票数据获取器：
- `get_daily()`: 获取日线数据
- `get_weekly()`: 获取周线数据
- `get_60min()`: 获取60分钟数据
- 所有函数均支持 `start_date` 与 `end_date` 参数，便于灵活截取数据
- 自动处理复权和时间索引
- `source` 参数在插件式架构下选择数据接口，默认支持 `akshare` 与 `myquant`，可按需扩展

### 可视化模块 (`peak_valley_detector.visualization`)

#### `MultiLayerVisualizer`
多层次可视化器：
- `plot_multi_layer_results()`: 绘制综合多层次结果
- `plot_changepoint_analysis()`: 绘制变点检测分析
- `plot_score_driven_diagnostics()`: 绘制模型诊断图

## 技术优势

### 相比传统方法的改进：

1. **理论严谨性**
   - 真正的GAS模型方差更新方程
   - 基于学生t分布的得分函数
   - 贝叶斯推断框架

2. **算法专业性**
   - Ruptures库的动态规划算法
   - BottomUp统计方法
   - 多算法融合策略

3. **代码质量**
   - 模块化架构设计
   - 类型注解支持
   - 完整的测试覆盖
   - 详细的文档说明

4. **实用性**
   - 多层回退策略
   - 参数自适应调整
   - 丰富的可视化功能

## 运行结果示例

系统支持多层次分析：
- **宏观层(周线)**: 15个变点，2个峰值，2个谷值
- **中观层(日线)**: 171个峰值，175个谷值  
- **微观层(60分钟)**: 6个峰值，4个谷值

## 开发和测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_core.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=peak_valley_detector --cov-report=html
```

### 代码格式化

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 格式化代码
black peak_valley_detector/
isort peak_valley_detector/

# 代码检查
flake8 peak_valley_detector/
```

## 自定义配置

在使用时可以灵活调整参数：

```python
# 自定义SD-BOCPD参数
detector = HybridChangePointDetector()
changepoints = detector.detect_sd_bocpd(
    series,
    nu=4.0,           # 学生t分布自由度
    omega=0.001,      # 基础方差
    alpha=0.06,       # 短期冲击系数
    beta=0.90,        # 方差持续性
    hazard_rate=1/25, # 变点先验概率
    threshold=0.3     # 检测阈值
)

# 调整峰谷分类窗口与方向
peaks, troughs = ExtremaClassifier.classify_changepoints(
    series,
    changepoints,
    window=0,        # 仅判定左侧
    check_right=False
)
```

## 依赖库

- `akshare`: 股票数据获取
- `pandas`: 数据处理和分析
- `numpy`: 数值计算
- `scipy`: 统计分析和信号处理
- `matplotlib`: 数据可视化
- `ta`: 技术指标计算
- `ruptures`: 专业变点检测库
- `filterpy`: 滤波算法库

## 学术背景

本实现基于以下重要理论文献：
- Creal, Koopman & Lucas (2013) 的 GAS 模型理论
- Adams & MacKay (2007) 的 BOCPD 算法框架
- 现代时间序列变点检测理论

## 贡献指南

欢迎贡献代码和改进建议：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: https://github.com/example/peak-valley-detector
- 问题反馈: https://github.com/example/peak-valley-detector/issues
- 文档: https://peak-valley-detector.readthedocs.io/

---

**版本**: 2.0.0 (模块化架构版本)  
**最后更新**: 2025年6月20日
