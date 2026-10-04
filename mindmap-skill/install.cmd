@echo off
setlocal
set "ROOT=%~dp0"
set "PY=%ROOT%runtime\win-x64\python.exe"
if not exist "%PY%" (
  echo Bundled Windows x64 Python runtime is missing. 1>&2
  exit /b 1
)
"%PY%" -I -B "%ROOT%install.py" %*
exit /b %ERRORLEVEL%
