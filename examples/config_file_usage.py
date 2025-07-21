"""示例：使用配置文件管理数据源和token"""

import sys
import os

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from peak_valley_detector.data.fetcher import StockDataFetcher
from peak_valley_detector.config import get_global_config


def config_file_example():
    """使用配置文件的示例"""
    print("=== 配置文件使用示例 ===")
    
    # 查看配置文件状态
    config = get_global_config()
    
    if config.has_config():
        print(f"✓ 找到配置文件: {config.get_config_file_path()}")
        print(f"✓ 默认数据源: {config.get_default_source()}")
        print(f"✓ 数据源配置: {config.get_source_config()}")
        
        # 检查token
        myquant_token = config.get_token('myquant')
        if myquant_token:
            print(f"✓ MyQuant token: {myquant_token[:10]}...{myquant_token[-10:]}")
        else:
            print("⚠ 未找到MyQuant token")
    else:
        print("⚠ 未找到配置文件，将使用默认配置")
    
    print("\n" + "="*50)
    
    # 使用配置文件创建数据获取器（无需手动传入token和配置）
    print("\n1. 使用配置文件创建StockDataFetcher...")
    fetcher = StockDataFetcher()  # 自动从配置文件读取
    
    symbol = "000001"
    start_date = "2023-01-01"
    end_date = "2023-01-10"
    
    print(f"\n2. 获取 {symbol} 的数据（{start_date} 到 {end_date}）:")
    
    try:
        # 获取日线数据（根据配置文件应该使用akshare）
        print("\n   获取日线数据...")
        daily_data = fetcher.get_daily(symbol, start_date, end_date)
        print(f"   日线数据形状: {daily_data.shape}")
        print(f"   数据来源: 根据配置使用 akshare")
        if not daily_data.empty:
            print(f"   数据示例:\n{daily_data.head(3)}")
        
        # 获取60分钟数据（根据配置文件应该使用myquant）
        print("\n   获取60分钟数据...")
        try:
            min60_data = fetcher.get_60min(symbol, start_date, end_date)
            print(f"   60分钟数据形状: {min60_data.shape}")
            print(f"   数据来源: 根据配置使用 myquant")
            if not min60_data.empty:
                print(f"   数据示例:\n{min60_data.head(3)}")
        except Exception as e:
            print(f"   MyQuant访问失败: {e}")
        
        # 获取周线数据（根据配置文件应该使用akshare）
        print("\n   获取周线数据...")
        weekly_data = fetcher.get_weekly(symbol, start_date, end_date)
        print(f"   周线数据形状: {weekly_data.shape}")
        print(f"   数据来源: 根据配置使用 akshare")
        if not weekly_data.empty:
            print(f"   数据示例:\n{weekly_data.head(3)}")
            
    except Exception as e:
        print(f"   错误: {e}")


def manual_override_example():
    """手动覆盖配置文件的示例"""
    print("\n=== 手动覆盖配置示例 ===")
    
    # 即使有配置文件，也可以手动覆盖配置
    print("\n1. 手动指定全部使用akshare...")
    fetcher_override = StockDataFetcher(source="akshare")
    
    symbol = "000001"
    start_date = "2023-01-01"
    end_date = "2023-01-05"
    
    try:
        daily_data = fetcher_override.get_daily(symbol, start_date, end_date)
        print(f"   日线数据形状: {daily_data.shape}")
        print("   ✓ 手动覆盖生效，使用akshare")
    except Exception as e:
        print(f"   错误: {e}")


def no_config_file_example():
    """禁用配置文件的示例"""
    print("\n=== 禁用配置文件示例 ===")
    
    # 禁用配置文件，使用程序内的配置
    print("\n1. 创建不使用配置文件的fetcher...")
    fetcher_no_config = StockDataFetcher(
        use_config_file=False,
        source_config={
            "daily": "akshare",
            "60min": "akshare"  # 强制60分钟也使用akshare
        },
        default_source="akshare"
    )
    
    symbol = "000001"
    start_date = "2023-01-01"
    end_date = "2023-01-05"
    
    try:
        daily_data = fetcher_no_config.get_daily(symbol, start_date, end_date)
        print(f"   日线数据形状: {daily_data.shape}")
        print("   ✓ 配置文件被禁用，使用程序内配置")
    except Exception as e:
        print(f"   错误: {e}")


def config_info():
    """显示当前配置信息"""
    print("\n=== 当前配置信息 ===")
    
    config = get_global_config()
    
    print(f"配置文件路径: {config.get_config_file_path()}")
    print(f"是否有配置: {config.has_config()}")
    print(f"默认数据源: {config.get_default_source()}")
    print(f"数据源配置: {config.get_source_config()}")
    
    tokens = config.get_all_tokens()
    if tokens:
        print("可用token:")
        for source, token in tokens.items():
            if token:
                print(f"  {source}: {token[:8]}...{token[-8:]}")
            else:
                print(f"  {source}: 未配置")
    else:
        print("未配置token")


if __name__ == "__main__":
    # 显示配置信息
    config_info()
    
    # 运行配置文件示例
    config_file_example()
    
    # 运行手动覆盖示例
    manual_override_example()
    
    # 运行禁用配置文件示例
    no_config_file_example()
    
    print("\n=== 使用说明 ===")
    print("1. 配置文件会自动加载，无需手动指定")
    print("2. 手动传入的参数会覆盖配置文件")
    print("3. 可以通过use_config_file=False禁用配置文件")
    print("4. 配置文件已添加到.gitignore，不会被提交")
    print("5. 其他用户需要创建自己的配置文件")
