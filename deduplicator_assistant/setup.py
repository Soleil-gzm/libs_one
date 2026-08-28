from setuptools import setup, find_packages

setup(
    name="deduplicator-assistant",  # PyPI 上的包名（可自定义）
    version="0.1.0",
    author="Soleil",
    description="去除对话中相邻重复的 user-assistant 轮次",
    packages=find_packages(),  # 自动发现 deduplicator_assistant 包
    python_requires=">=3.6",
    install_requires=[],  # 无外部依赖
)
