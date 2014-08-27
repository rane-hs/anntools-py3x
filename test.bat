@echo off

rem set PYDRIVE=%HOMEDRIVE%
set PYDRIVE=D:
set PYTHONPATH=%CD%

set PYTHON=%PYDRIVE%\Python24\python.exe
echo %PYTHON%
%PYTHON% tests\test_conversion.py
%PYTHON% tests\test_cooperation.py
%PYTHON% tests\test_typecheck.py
%PYTHON% tests\test_validation.py

set PYTHON=%PYDRIVE%\Python25\python.exe
echo %PYTHON%
%PYTHON% tests\test_conversion.py
%PYTHON% tests\test_cooperation.py
%PYTHON% tests\test_typecheck.py
%PYTHON% tests\test_validation.py

set PYTHON=%PYDRIVE%\Python26\python.exe
echo %PYTHON%
%PYTHON% tests\test_conversion.py
%PYTHON% tests\test_cooperation.py
%PYTHON% tests\test_typecheck.py
%PYTHON% tests\test_validation.py

set PYTHON=%PYDRIVE%\Python30\python.exe
echo %PYTHON%
%PYTHON% tests\test_conversion.py
%PYTHON% tests\test_cooperation.py
%PYTHON% tests\test_typecheck.py
%PYTHON% tests\test_validation.py
