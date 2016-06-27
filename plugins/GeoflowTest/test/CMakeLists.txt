ExternalProject_Add(googlemock
	SVN_REPOSITORY http://googlemock.googlecode.com/svn/trunk
	SVN_REVISION -r 519
	TIMEOUT 120
	CMAKE_ARGS  -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
				-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG:PATH=DebugLibs
				-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE:PATH=ReleaseLibs
	INSTALL_COMMAND ""
	UPDATE_COMMAND ""
	LOG_DOWNLOAD ON
	LOG_CONFIGURE ON
	LOG_BUILD ON)

# Google Mock/Test includes
ExternalProject_Get_Property(googlemock source_dir)
include_directories(${PROJECT_SOURCE_DIR}/src ${source_dir}/include ${source_dir}/gtest/include)

add_executable(UnitTests test_main.cpp
	# This is gross, but I've already spent far too long on hacking CMake.
	# Hopefully Erik can come in and make this pretty.
	../src/Atom.cpp
	Atom_test.cpp)
	#solvationsub_test.cpp)
	#surfconcz_test.cpp)

# Need C++11.
set_property(TARGET UnitTests PROPERTY CXX_STANDARD 11)
set_property(TARGET UnitTests PROPERTY CXX_STANDARD_REQUIRED ON)

add_dependencies(UnitTests googlemock)

# Google Mock libs
ExternalProject_Get_Property(googlemock binary_dir)
target_link_libraries(UnitTests
	debug ${binary_dir}/DebugLibs/${CMAKE_FIND_LIBRARY_PREFIXES}gmock.a
	debug ${binary_dir}/gtest/DebugLibs/${CMAKE_FIND_LIBRARY_PREFIXES}gtest.a
	optimized ${binary_dir}/ReleaseLibs/${CMAKE_FIND_LIBRARY_PREFIXES}gmock.a
	optimized ${binary_dir}/gtest/ReleaseLibs/${CMAKE_FIND_LIBRARY_PREFIXES}gtest.a)

add_test(UnitTests UnitTests)

# Sort of a hack to get tests to build so that "make test" works.  But now it's called
# "make check".
# See http://stackoverflow.com/questions/733475/cmake-ctest-make-test-doesnt-build-tests
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND}
                  DEPENDS UnitTests)
