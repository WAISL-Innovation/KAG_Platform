import os
import sys
from typing import List

import yaml
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from kag_platform.constants import CONFIG_FILE_PATH
from kag_platform.entity import ModelInfo, Neo4jConfig
from kag_platform.utils.common import create_directories, read_yaml






class ConfigurationManager:
    
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
      
        ):
        self.config = read_yaml(config_filepath)
        create_directories([self.config.artifacts_root])
        kb_dir = f"{self.config.artifacts_root}/kb"
        create_directories([kb_dir])
        # model_dir = f"{self.config.artifacts_root}/model"
        # create_directories([model_dir])


    def get_neo4j_config(self) -> Neo4jConfig:
        '''
        Get the Neo4j database info.
        '''
        try:
            neo4j_config = self.config.neo4j_db_info
            if neo4j_config is None:
                return None
            else:
                neo4j_cfg = Neo4jConfig(
                    neo4j_uri=neo4j_config.neo4j_uri,
                    username=neo4j_config.username,
                    
                )

                return neo4j_cfg
        except Exception as e:
            print(f"Error in get_neo4j_config: {e}")
            return None

    def get_model_info(self) -> ModelInfo:
        '''
        Get the Neo4j database info.
        '''
        try:
            model_info = self.config.model_info
            if model_info is None:
                return None
            else:
                model_info = ModelInfo(
                    groq_model_name=model_info.groq_model_name,
                )

                return model_info
        except Exception as e:
            print(f"Error in get_model_info: {e}")
            return None
               