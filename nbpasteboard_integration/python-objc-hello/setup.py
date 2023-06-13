from setuptools import setup, Extension, find_packages

hello_module = Extension(
    "objc_hello._hello",
    sources=["src/objc_hello/_hello.m"],
    language="objc",
)

setup(
    name="objc_hello",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    ext_modules=[hello_module],
)
