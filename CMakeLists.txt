cmake_minimum_required(VERSION 3.10)
project(cpp_ingestion)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
# pybind11 package hatane ki zaroorat nahi, bas hum include path control karenge
find_package(pybind11 REQUIRED)

# Manual module target (pybind11_add_module ki jagah)
add_library(cpp_ingestion SHARED src/pipeline.cpp)
set_target_properties(cpp_ingestion PROPERTIES PREFIX "")
set_target_properties(cpp_ingestion PROPERTIES SUFFIX ".so")

# Paths link karo
target_include_directories(cpp_ingestion PRIVATE 
    ${OpenCV_INCLUDE_DIRS} 
    ${pybind11_INCLUDE_DIRS} 
)

target_link_libraries(cpp_ingestion PRIVATE 
    ${OpenCV_LIBS} 
    Python3::Python
)
