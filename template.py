import os
from pathlib import Path
import logging
# Here we only enale the INFO label which content time and message which will bellow print. This will print on console.
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')


project_name = "kag_platform"

list_of_files = [
    ".github/workflows/.gitkeep",
    f"src/{project_name}/__init__.py",
    f"src/{project_name}/components/__init__.py",
    f"src/{project_name}/utils/__init__.py",
    f"src/{project_name}/utils/common.py",
    f"src/{project_name}/logging/__init__.py",
    f"src/{project_name}/config/__init__.py",
    f"src/{project_name}/config/configuration.py",
    f"src/{project_name}/pipeline/__init__.py",
    f"src/{project_name}/entity/__init__.py",
    f"src/{project_name}/constants/__init__.py",
    "config/config.yaml",
    "params.yaml",
    "app.py",
    "main.py",
    "requirements.txt",
    "setup.py",
    "research/kag_research.ipynb",

]


for filepath in list_of_files:
    filepath = Path(filepath) # This initial check the environment like window or linux and then according to the environment get the current path.
    # Here we access all created file name and directory or folder.
    filedir, filename = os.path.split(filepath)

    # Here we create the director or folder
    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory:{filedir} for the file {filename}")

    # Here we create the file or directory if it is not exist or if created and it don't have any text then override.
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath,'w') as f:
            pass
            logging.info(f"Creating empty file: {filepath}")

    # Here we asume file already created and it has some text.    
    else:
        logging.info(f"{filename} is already exists")