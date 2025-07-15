import os
import sys


from box.exceptions import BoxValueError # Instead of create the custome exception we can use the Box exception for exception handling it is also working as the same.
import yaml # to access the yaml feature.
# from main.logging import logger  # Here textSummarizerEndToEnd is the project name in which logging directory are there and since __init__.py are constructor class so if we don't pass any class name then by default it will search in it.
from ensure import ensure_annotations # To restrict any function's data type by adding the @ensure_annotations. For details see the research/trials.ipynb file.
from box import ConfigBox # To access the dictionary kind of value very conveniant. for more details check the 'research/trials.ipynb' file.
from pathlib import Path
from typing import Any

from src.kag_platform.logging import logger
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# this function take the yaml file path and return the ConfigBox. In this function we handle the Box exception for custome exception
@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """reads yaml file and returns

    Args:
        path_to_yaml (str): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: ConfigBox type
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("yaml file is empty")
    except Exception as e:
        raise e
    


@ensure_annotations
def create_directories(path_to_directories: list, verbose=True):
    """create list of directories

    Args:
        path_to_directories (list): list of path of directories
        ignore_log (bool, optional): ignore if multiple dirs is to be created. Defaults to False.
    """
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            logger.info(f"created directory at: {path}")





    