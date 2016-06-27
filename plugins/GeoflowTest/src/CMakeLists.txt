project (geoflow_c)

option(ENABLE_GEOFLOW_APBS "geoflow APBS" OFF)
if(ENABLE_GEOFLOW_APBS)
   add_definitions(-DGEOFLOW_APBS)
   include_directories(
         ../../../src/ 
         ../../../tools/windows/configuration\ headers/
         ../../../externals/fetk/maloc/src/base
         ../../../externals/fetk/maloc/src/vsys
         ../../../externals/fetk/maloc/src/vsh
         ../../../externals/fetk/maloc/src/psh
         )
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

SET(geoflow_standalone_CMAKE_DIR "${geoflow_standalone_SOURCE_DIR}/cmake")

set(GOOGLE_LIBS -L$(GMOCK_HOME)/osx -L$(GMOCK_HOME)/osx/gtest 
           -lgtest -lgmock)

set(GOOGLE_INCLUDE -I$(GMOCK_HOME)/include 
	   -I$(GMOCK_HOME)/gtest/include -std=c++11)

#
#  build geoflow library
#
add_library(GeometricFlowLib 
     GeometricFlowWrap.cpp
     GeometricFlow.cpp
     Atom.cpp
     )

#
#  build standalone C++ example
#
add_executable(GeometricFlow 
     runGeometricFlow.cpp
     GeometricFlow.cpp
     Atom.cpp
     )

#
#  build standalone C example
#
add_executable(GeometricFlowWrap
     runGeometricFlowWrap.c
)

target_link_libraries(GeometricFlowWrap GeometricFlowLib)
add_dependencies(GeometricFlow eigen3 boost)
add_dependencies(GeometricFlowLib eigen3 boost)
add_dependencies(GeometricFlowWrap eigen3 boost)

