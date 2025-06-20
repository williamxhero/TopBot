"""
Peak Valley Detector 多层次峰谷检测系统安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="peak-valley-detector",
    version="2.0.0",
    author="AI Assistant",
    author_email="assistant@ai.com",
    description="基于严谨 Score-Driven BOCPD 方法的多层次股票峰谷检测系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/peak-valley-detector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=5.0",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "peak-valley-detector=peak_valley_detector.main:main",
        ],
    },
    keywords="changepoint detection, time series analysis, stock analysis, BOCPD, GAS model",
    project_urls={
        "Bug Reports": "https://github.com/example/peak-valley-detector/issues",
        "Source": "https://github.com/example/peak-valley-detector",
        "Documentation": "https://peak-valley-detector.readthedocs.io/",
    },
)
