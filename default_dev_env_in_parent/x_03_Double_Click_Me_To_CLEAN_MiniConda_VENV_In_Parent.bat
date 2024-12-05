@echo off

@REM samll info how to create the requirements.txt  (inside the python environment)
@REM pip freeze > requirements.txt


@REM REM this is getting the path where the bat file is.
@REM cd /D "%~dp0"

REM this is getting the parent path fro where the bat file is.
cd /D "%~dp0.."

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo This script relies on Miniconda which can not be silently installed under a path with spaces. && goto end

@rem fix failed install when installing to a separate drive
set TMP=%cd%\dev_env
set TEMP=%cd%\dev_env

@rem deactivate existing conda envs as needed to avoid conflicts
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set CONDA_ROOT_PREFIX=%cd%\dev_env\conda
set INSTALL_ENV_DIR=%cd%\dev_env\env

@rem environment isolation
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )
@rem setup installer env
@REM call python reqirement_installer.py %*
@REM call conda clean --packages %*
call conda clean --all %*

@rem enter commands
cmd /k "%*"

:end
pause
