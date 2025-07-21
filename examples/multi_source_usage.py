"""示例：为不同API使用不同数据源"""

import sys
import os

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from peak_valley_detector.data.fetcher import StockDataFetcher

def main():
    print("=== 多数据源配置示例 ===")
    
    # 配置：日线使用akshare，60分钟线使用myquant
    source_config = {
        "daily": "akshare",
        "60min": "myquant", 
        # weekly使用默认数据源（akshare）
        # hist使用默认数据源（akshare）
    }
    
    # 创建数据获取器（需要myquant token）
    # 注意：这里需要替换为真实的token
    token = "YOUR_MYQUANT_TOKEN_HERE"
    
    try:
        fetcher = StockDataFetcher(
            source_config=source_config,
            default_source="akshare",  # 默认使用akshare
            token=token
        )
        
        symbol = "000001"
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        print(f"\n获取 {symbol} 的数据（{start_date} 到 {end_date}）:")
        
        # 获取日线数据（使用akshare）
        print("\n1. 获取日线数据（使用akshare）...")
        daily_data = fetcher.get_daily(symbol, start_date, end_date)
        print(f"日线数据形状: {daily_data.shape}")
        print(f"日线数据列: {list(daily_data.columns)}")
        if not daily_data.empty:
            print(f"日线数据示例:\n{daily_data.head()}")
        
        # 获取60分钟数据（使用myquant）
        print("\n2. 获取60分钟数据（使用myquant）...")
        try:
            min60_data = fetcher.get_60min(symbol, start_date, end_date)
            print(f"60分钟数据形状: {min60_data.shape}")
            print(f"60分钟数据列: {list(min60_data.columns)}")
            if not min60_data.empty:
                print(f"60分钟数据示例:\n{min60_data.head()}")
        except ImportError as e:
            print(f"MyQuant不可用: {e}")
            print("请先安装gm.api包并配置token")
        
        # 获取周线数据（使用默认源akshare）
        print("\n3. 获取周线数据（使用默认源akshare）...")
        weekly_data = fetcher.get_weekly(symbol, start_date, end_date)
        print(f"周线数据形状: {weekly_data.shape}")
        if not weekly_data.empty:
            print(f"周线数据示例:\n{weekly_data.head()}")
            
    except Exception as e:
        print(f"错误: {e}")


def compatibility_example():
    """兼容性示例：使用旧接口"""
    print("\n=== 兼容性示例（旧接口）===")
    
    # 旧接口：所有API都使用同一个数据源
    fetcher = StockDataFetcher(source="akshare")
    
    symbol = "000001"
    start_date = "2023-01-01"
    end_date = "2023-01-10"
    
    print(f"\n获取 {symbol} 的日线数据（全部使用akshare）:")
    daily_data = fetcher.get_daily(symbol, start_date, end_date)
    print(f"数据形状: {daily_data.shape}")
    if not daily_data.empty:
        print(f"数据示例:\n{daily_data.head()}")


def simple_config_example():
    """简单配置示例：只使用默认数据源"""
    print("\n=== 简单配置示例 ===")
    
    # 不指定任何source，全部使用默认数据源
    fetcher = StockDataFetcher()
    
    symbol = "000001"
    start_date = "2023-01-01"
    end_date = "2023-01-10"
    
    print(f"\n获取 {symbol} 的数据（全部使用默认源akshare）:")
    daily_data = fetcher.get_daily(symbol, start_date, end_date)
    print(f"日线数据形状: {daily_data.shape}")
    if not daily_data.empty:
        print(f"日线数据示例:\n{daily_data.head()}")


if __name__ == "__main__":
    # 运行主示例
    main()
    
    # 运行兼容性示例  
    compatibility_example()
    
    # 运行简单配置示例
    simple_config_example()
    
    print("\n=== 使用说明 ===")
    print("1. 新功能：使用source_config参数为不同API指定不同数据源")
    print("2. 兼容性：旧的source参数仍然可用")
    print("3. 默认值：未指定的API会使用default_source")
    print("4. MyQuant：需要安装gm.api包并配置有效token")
