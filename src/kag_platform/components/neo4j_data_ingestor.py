import os
from langchain.text_splitter import TokenTextSplitter
from langchain_community.graphs import Neo4jGraph
from langchain.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from sqlalchemy import text
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_groq import ChatGroq
from src.kag_platform.logging import logger  # ✅ updated logger import

'''
NOTE: We need to configure the neo4j database with the following steps:
1. Go to plugin store and install APOC plugin.
2. Add the below lines to the local neo4j.conf file:

dbms.security.procedures.unrestricted=apoc.*
dbms.security.procedures.allowlist=apoc.meta.data,apoc.*  (Already exists, just update the value)
dbms.security.procedures.whitelist=allowlist
'''


class Neo4jDataIngestor:
    def __init__(self, neo4j_uri, username, model_name="llama3-70b-8192"):
        try:
            os.environ["NEO4J_URI"] = neo4j_uri
            os.environ["NEO4J_USERNAME"] = username

            self.graph = Neo4jGraph()
            self.text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
            self.llm = ChatGroq(
                temperature=0,
                model_name=model_name,
            )
            self.llm_transformer = LLMGraphTransformer(llm=self.llm)
            logger.info("Neo4j connection initialized.")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def load_file(self, file_path):
        try:
            if file_path.endswith(".txt"):
                loader = TextLoader(file_path)
            elif file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            else:
                raise ValueError("Unsupported file format. Use .txt, .pdf, or .docx.")

            documents = loader.load()
            logger.info(f"Loaded {len(documents)} document(s) from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"File loading failed: {e}")
            raise

    def ingest_to_graph(self, file_path):
        try:
            extracted_documents = self.load_file(file_path)
            full_text = " ".join([doc.page_content for doc in extracted_documents])
            # chunks = self.text_splitter.split_text(full_text)
            documents = self.text_splitter.create_documents([full_text])
            graph_documents = self.llm_transformer.convert_to_graph_documents(documents)
            self.graph.add_graph_documents(
                graph_documents,
                baseEntityLabel=True,
                include_source=True
            )
            logger.info("Data inserted into Neo4j successfully.")
            return "inserted successfully"
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            return f"Error: {e}"
