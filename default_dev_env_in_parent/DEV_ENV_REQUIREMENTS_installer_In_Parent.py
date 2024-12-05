import os
import subprocess
import sys

#samll info how to create the requirements.txt  (inside the python environment)
#pip freeze > requirements.txt


# Environment
script_dir = os.getcwd()
parent_folder_path:str = os.path.dirname(script_dir)
conda_env_path = os.path.join(parent_folder_path, "dev_env", "env")

def is_windows():
    return sys.platform.startswith("win")

def check_env():
    # If we have access to conda, we are probably in an environment
    conda_exist = run_cmd("conda", environment=True, capture_output=True).returncode == 0
    if not conda_exist:
        print("Conda is not installed. Exiting...")
        sys.exit(1)

    # Ensure this is a new environment and not the base environment
    if os.environ["CONDA_DEFAULT_ENV"] == "base":
        print("Create an environment for this project and activate it. Exiting...")
        sys.exit(1)


def clear_cache():
    run_cmd("conda clean -a -y", environment=True)
    run_cmd("python -m pip cache purge", environment=True)




def run_cmd(cmd, assert_success=False, environment=False, capture_output=False, env=None):
    # Use the conda environment
    if environment:
        if is_windows():
            conda_bat_path = os.path.join(parent_folder_path, "dev_env", "conda", "condabin", "conda.bat")
            cmd = f'"{conda_bat_path}" activate "{conda_env_path}" >nul && {cmd}'
        else:
            conda_sh_path = os.path.join(parent_folder_path, "dev_env", "conda", "etc", "profile.d", "conda.sh")
            cmd = f'. "{conda_sh_path}" && conda activate "{conda_env_path}" && {cmd}'

    # Run shell commands
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, env=env)

    # Assert the command ran successfully
    if assert_success and result.returncode != 0:
        print(f"Command '{cmd}' failed with exit status code '{str(result.returncode)}'.\n\nExiting now.\nTry running the start/update script again.")
        sys.exit(1)

    return result


if __name__ == "__main__":
    # Verifies we are in a conda environment
    check_env()
    run_cmd("python -m pip install -r REQUIREMENTS.txt --upgrade", assert_success=True, environment=True)
    clear_cache()
