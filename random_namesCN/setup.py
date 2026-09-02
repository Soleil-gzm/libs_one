from setuptools import setup, find_packages

setup(
    name="random-namesCN",  # PyPI 上的包名（可自定义）
    version="0.1.0",
    author="Soleil",
    description="随机生成中文姓名",
    packages=find_packages(),  # 自动发现 random_namesCN 包
    python_requires=">=3.6",
    install_requires=[],  # 仅依赖标准库（random/pkgutil）
    include_package_data=True,
    package_data={"random_namesCN": ["data/*.csv"]},
)
