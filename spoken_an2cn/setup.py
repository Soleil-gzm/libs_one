from setuptools import setup, find_packages

setup(
    name="spoken-an2cn",  # PyPI 上的包名（可自定义）
    version="0.1.0",
    author="Soleil",
    description="将阿拉伯数字转化为口语化中文数字",
    packages=find_packages(),  # 自动发现 spoken_an2cn 包
    python_requires=">=3.6",
    install_requires=[],  # 仅依赖标准库（re/decimal/typing/warnings）
)
