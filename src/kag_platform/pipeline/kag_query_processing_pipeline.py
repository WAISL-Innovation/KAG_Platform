from src.kag_platform.config.configuration import ConfigurationManager
from src.kag_platform.components.neo4j_answer_retriever import Neo4jAnswerRetriever
from src.kag_platform.components.neo4j_data_ingestor import Neo4jDataIngestor
from src.kag_platform.logging import logger

class KagQueryProcessingPipeline:

    def __init__(self):
        logger.info("Initializing KagQueryProcessingPipeline")
        try:
            logger.info("Initializing Configuration Manager")
            self.config_manager = ConfigurationManager()
            logger.info("Configuration Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ConfigurationManager: {e}")
            raise

    def data_ingestion(self, file_path: str) -> str:
        """
        Ingests data from the specified file path into the KAG system.
        """
        logger.info(f"Starting data ingestion for file: {file_path}")
        try:
            neo4j_config = self.config_manager.get_neo4j_config()
            model_cfg = self.config_manager.get_model_info()

            logger.debug(f"Neo4j URI: {neo4j_config.neo4j_uri}, Username: {neo4j_config.username}")
            logger.debug(f"RAG Model Name: {model_cfg.groq_model_name}")

            ingestor = Neo4jDataIngestor(
                neo4j_uri=neo4j_config.neo4j_uri,
                username=neo4j_config.username,
                model_name=model_cfg.groq_model_name
            )

            result = ingestor.ingest_to_graph(file_path)
            if "Error" in result:
                logger.error(f"Data ingestion failed: {result}")
                raise Exception(f"Data ingestion failed: {result}")

            logger.info("Data ingestion completed successfully")
            return result if result else "No data ingested in Graph DB."
        
        except Exception as e:
            logger.exception(f"Exception occurred during data ingestion: {e}")
            raise

    def process_query(self, query: str) -> str:
        logger.info(f"Processing query: {query}")
        try:
            neo4j_config = self.config_manager.get_neo4j_config()
            model_cfg = self.config_manager.get_model_info()

            logger.debug(f"Neo4j URI: {neo4j_config.neo4j_uri}, Username: {neo4j_config.username}")
            logger.debug(f"RAG Model Name: {model_cfg.groq_model_name}")

            retriever = Neo4jAnswerRetriever(
                neo4j_uri=neo4j_config.neo4j_uri,
                username=neo4j_config.username,
                model_name=model_cfg.groq_model_name
            )

            result = retriever.get_answer(query)
            if "Error" in result:
                logger.error(f"Query processing failed: {result}")
                raise Exception(f"Query processing failed: {result}")

            logger.info("Query processed successfully")
            return result if result else "No answer found in Graph DB."

        except Exception as e:
            logger.exception(f"Exception occurred during query processing: {e}")
            raise
