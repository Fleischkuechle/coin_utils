this bat files create a minniconda virtual environment with the requirements needed to start
programming in blender.

It installs the devenv in the parent folder of the Folder where the files are stored.
Example: the files are inside
C\MyProject\Bl_dev_env_in_parent\1_Double_Click_Me_To_INSTALL_MiniConda_dev_env_python_version_310__In_Parent.bat

if you now click on 1_Double_Click_Me_To_INSTALL_MiniConda_dev_env_python_version_310__In_Parent.bat
the miniconda environment will be installed 
paralell to the Bl_dev_env_in_parent folder which will look like this:
C\MyProject\Bl_dev_env_in_parent\
C\MyProject\Bl_dev_env\....here will be the new generated miniconda virtual environment.....

to change the name of the dev_env
you need to go through all files and serach replace the folder name


with 2_Double_Click_Me_To_INSTALL_MiniConda_dev_env_REQUIREMENTS___In_Parent.bat
it will install the requirements listed in 
REQUIREMENTS.txt
into that dev env 


--------------------------------------------------------------------------

TO get the requirements.txt that only shows the requirements of your project 
you can use 5_Double_Click_Me_To_Create_PIPREQUES_REQUIREMENTS_TXT_from_PIPREQUES_PATH_TXT_pipreqs.bat

this looks into this file where you put the path to your project in it
something like: D:\02\05\36\my_project_folder\
PIPREQUES_PATH.txt 

what is does:
it creates a text file called: PIPREQUES_REQUIREMENTS.txt
inside you project path from PIPREQUES_PATH.txt 
in this example you will find the file here:
D:\02\05\36\my_project_folder\PIPREQUES_REQUIREMENTS.txt

Here is an example:
![alt text](image-5.png)


A terminal window (we are on windows) will open and show this:
![alt text](image-6.png)

To understand: This is not a pip freeze result this only shows the dependencies you have in the 
project.

For comarision here is a pip freeze (created with 4_Double_Click_Me_To_Create_dev_env_PIP_freeze .bat):
![alt text](image-7.png)

