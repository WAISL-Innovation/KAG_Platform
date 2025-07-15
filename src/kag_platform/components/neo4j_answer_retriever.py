import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_groq import ChatGroq
from typing import List, Tuple, Dict
from langchain_core.pydantic_v1 import BaseModel, Field

from src.kag_platform.logging import logger

class Entities(BaseModel):
    """Identifying information about entities."""
    names: List[str] = Field(
        ...,
        description="All the person, organization, or business entities that appear in the text",
    )


class Neo4jAnswerRetriever:
    def __init__(self, neo4j_uri, username, model_name="llama3-70b-8192"):
        try:
            logger.info("Initializing Neo4jAnswerRetriever...")
            load_dotenv()

            os.environ["NEO4J_URI"] = neo4j_uri
            os.environ["NEO4J_USERNAME"] = username

            self.graph = Neo4jGraph()
            self.llm = ChatGroq(
                temperature=0,
                model_name=model_name,
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are extracting organization and person entities from the text."),
                ("human", "Use the given format to extract information from the following input: {question}"),
            ])
            self.entity_chain = prompt | self.llm.with_structured_output(Entities)

            self.vector_index = Neo4jVector.from_existing_graph(
                HuggingFaceEmbeddings(model_name="BAAI/bge-base-en"),
                search_type="hybrid",
                node_label="Document",
                text_node_properties=["text"],
                embedding_node_property="embedding"
            )

            self.template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question,
                            in its original language.

                            Follow Up Input: {question}
                            Standalone question:"""

            self.CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(self.template)

            self.graph.query("CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")

            logger.info("Neo4jAnswerRetriever initialized successfully.")
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            raise

    def generate_full_text_query(self, input: str) -> str:
        full_text_query = ""
        words = [el for el in remove_lucene_chars(input).split() if el]
        for word in words[:-1]:
            full_text_query += f" {word}~2 AND"
        full_text_query += f" {words[-1]}~2"
        return full_text_query.strip()

    def structured_retriever(self, question: str) -> str:
        logger.info(f"Running structured retriever for question: {question}")
        try:
            result = ""
            entities = self.entity_chain.invoke({"question": question})
            logger.info(f"Entities found: {entities.names}")

            for entity in entities.names:
                query = self.generate_full_text_query(entity)
                logger.info(f"Querying fulltext index with: {query}")

                response = self.graph.query(
                    """CALL db.index.fulltext.queryNodes('entity', $query, {limit:2})
                    YIELD node,score
                    CALL {
                    WITH node
                    MATCH (node)-[r:!MENTIONS]->(neighbor)
                    RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                    UNION ALL
                    WITH node
                    MATCH (node)<-[r:!MENTIONS]-(neighbor)
                    RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
                    }
                    RETURN output LIMIT 50
                    """,
                    {"query": query},
                )
                result += "\n".join([el['output'] for el in response])
            return result
        except Exception as e:
            logger.error(f"Structured retrieval failed: {e}")
            return "Structured retrieval error"

    def retriever(self, question: str) -> str:
        logger.info(f"Retrieving vector + structured data for question: {question}")
        structured_data = self.structured_retriever(question)

        try:
            vector_results = self.vector_index.similarity_search(question)
            logger.info(f"Vector search returned {len(vector_results)} documents.")
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            vector_results = []

        unstructured_data = [el.page_content for el in vector_results]
        final_data = f"""Structured data:\n{structured_data}\nUnstructured data:\n{"#Document ".join(unstructured_data)}"""
        return final_data

    def _format_chat_history(self, chat_history: List[Tuple[str, str]]) -> List:
        buffer = []
        for human, ai in chat_history:
            buffer.append(HumanMessage(content=human))
            buffer.append(AIMessage(content=ai))
        return buffer

    def get_answer(self, query: str) -> str:
        try:
            logger.info(f"Received query: {query}")

            _search_query = RunnableBranch(
                (
                    RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(run_name="HasChatHistoryCheck"),
                    RunnablePassthrough.assign(
                        chat_history=lambda x: self._format_chat_history(x["chat_history"])
                    )
                    | self.CONDENSE_QUESTION_PROMPT
                    | self.llm
                    | StrOutputParser(),
                ),
                RunnableLambda(lambda x: x["question"]),
            )

            answer_prompt = ChatPromptTemplate.from_template(
                """Answer the question based only on the following context:
                {context}

                Question: {question}
                Use natural language and be concise.
                Answer:"""
            )

            chain = (
                RunnableParallel(
                    {
                        "context": _search_query | self.retriever,
                        "question": RunnablePassthrough(),
                    }
                )
                | answer_prompt
                | self.llm
                | StrOutputParser()
            )

            result = chain.invoke({"question": query})
            logger.info("Answer generated successfully.")
            return result
        except Exception as e:
            logger.error(f"Failed to get answer: {e}")
            raise
