# Works with Python 2.7 and 3.2+. Seems more reliable that FindPythonLibs, and
# makes sure our include directory matches the Python executable and Cython.
if(NOT PYTHON_INCLUDE_DIR)
	find_package(PythonInterp)

	if(PYTHON_EXECUTABLE)
		execute_process(COMMAND "${PYTHON_EXECUTABLE}" -c
					"import sysconfig; print(sysconfig.get_path('include'));"
				OUTPUT_VARIABLE _PythonInclude_OUTPUT
				RESULT_VARIABLE _PythonInclude_RESULT)
		
		if(_PythonInclude_RESULT EQUAL 0)
			string(STRIP "${_PythonInclude_OUTPUT}" _PythonInclude_OUTPUT)
		else()
			set(exec_output PythonInclude-NOTFOUND)
		endif()

		set(PYTHON_INCLUDE_DIR "${_PythonInclude_OUTPUT}" CACHE PATH
				"Path to where Python.h is found")
	endif()
endif()

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(PythonInclude
		REQUIRED_VARS PYTHON_INCLUDE_DIR
		VERSION_VAR PYTHON_VERSION_STRING)

mark_as_advanced(PYTHON_INCLUDE_DIR)
