from setuptools import setup, Extension

# Define the Objective-C extension module
extension_module = Extension(
    "hello",
    sources=["hello.m"],
    extra_link_args=["-framework", "Foundation"],
    extra_compile_args=["-ObjC"],
)

# Setup the package
setup(
    name="hello",
    version="1.0",
    ext_modules=[extension_module],
)
