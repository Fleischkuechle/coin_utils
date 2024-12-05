@echo off

@REM samll info how to create the requirements.txt  (inside the python environment)
@REM pip freeze > requirements.txt

@REM %~dp0: Breaks down as follows:
@REM %~d0: Extracts the drive letter from %0.
@REM %~p0: Extracts the path (directory) from %0.
@REM Combining the above two (%~d0 and %~p0) gives the drive and path of the batch file.

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

@REM #cd into the folder where the  BL_DEV_ENV_REQUIREMENTS_installer_In_Parent.py is saved
cd /D "%~dp0"


@rem setup installer env
@rem call python BL_DEV_ENV_REQUIREMENTS_installer_In_Parent.py %*
@REM call python DEV_ENV_REQUIREMENTS_installer_In_Parent.py %*
call python --version
@rem enter commands
cmd /k "%*"

:end
pause
