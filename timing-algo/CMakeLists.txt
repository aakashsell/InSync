cmake_minimum_required(VERSION 3.0)
project(example)

set(CMAKE_CXX_STANDARD 14)

# Find pybind11 package
find_package(pybind11 REQUIRED)

# Create a Python module
pybind11_add_module(test algo.cpp)

