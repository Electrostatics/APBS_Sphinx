# Determines whether the Cython package is installed for the Python interpreter
# we are using.

find_package(PythonInterp)

if(PYTHON_EXECUTABLE)
	execute_process(COMMAND "${PYTHON_EXECUTABLE}" -m cython --version
			OUTPUT_VARIABLE _CYTHON_VERSION_STRING
			ERROR_VARIABLE _CYTHON_VERSION_STRING
			RESULT_VARIABLE _CYTHON_VERSION_RESULT)

	if(_CYTHON_VERSION_RESULT EQUAL 0)
		string(REGEX REPLACE "^.* ([^ \n]+)\n?$" "\\1" Cython_VERSION "${_CYTHON_VERSION_STRING}")
	else()
		set(Cython_VERSION Cython-NOTFOUND)
	endif()
endif()

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Cython REQUIRED_VARS Cython_VERSION
		VERSION_VAR Cython_VERSION)
