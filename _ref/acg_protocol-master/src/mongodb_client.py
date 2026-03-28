from datetime import datetime
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
import pymongo
import re
import asyncio
from time import sleep

from config import Config, log
import google.generativeai as genai

genai.configure(api_key=Config.GOOGLE_API_KEY)

class MongoDBClient:
    """
    A client for interacting with MongoDB to store and retrieve document chunks,
    and handle SHI/SSR persistence and RAG operations.
    """
    
    def __init__(self):
        """
        Initializes the MongoDB client using configuration from config.py.
        """
        self.config = Config.get_db_config()
        self.client: Optional[MongoClient] = None
        
        try:
            self.client = MongoClient(self.config['uri'], serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.config['db_name']]
            self.ssr_collection = self.db[Config.MONGO_SSR_COLLECTION]
            self.rag_collection = self.db[Config.MONGO_RAG_COLLECTION]
            log.info(f"💾 [DB] Connected to MongoDB: {self.config['db_name']}")
        except (ConnectionFailure, ConfigurationError) as e:
            log.error(f"FATAL: Could not connect to MongoDB. Check MONGO_URI. Error: {e}")
            self.client = None
            raise

    def vector_search(self, query_embedding: List[float], limit: int = 2, min_score: float = 0.85, shi_filter: Optional[str] = None) -> List[Dict]:
        """
        Performs a vector similarity search on the RAG collection.
        This assumes a vector index named 'embedding' is set up in MongoDB Atlas.
        """
        if not self.client: return []
        
        log.info(f"🔍 [Search] Running vector search against RAG collection...")

        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                    "index": "embedding" 
                }
            }
        ]

        if shi_filter:
            pipeline.append({
                "$match": {
                    "shi": shi_filter
                }
            })
        
        pipeline.append({
            "$project": {
                "score": {"$meta": "vectorSearchScore"},
                "content": 1,
                "metadata": 1,
                "shi": 1,
                "chunk_id": 1,
                "_id": 0
            }
        })

        if min_score > 0:
            pipeline.append({
                "$match": {
                    "score": {"$gte": min_score}
                }
            })

        pipeline.append({
            "$sort": {
                "score": -1
            }
        })
        
        results = list(self.rag_collection.aggregate(pipeline))

        return [
            {
                "text_chunk": doc["content"],
                "source_uri": doc["metadata"]["uri"],
                "source_version": 1,
                "shi": doc["shi"],
                "loc_selector": doc["metadata"]["loc"],
                "chunk_id": doc["chunk_id"],
                "score": doc["score"]
            } for doc in results
        ]

    def insert_ssr_entry(self, entry: dict):
        """Inserts a fully verified SSR entry into a persistent store."""
        if not self.client: return
        try:
            self.ssr_collection.update_one(
                {"SHI": entry["SHI"]},
                {"$set": entry},
                upsert=True
            )
            log.info(f"💾 [DB] Upserted SSR entry for SHI: {entry['SHI'][:10]}...")
        except Exception as e:
            log.error(f"Failed to insert/update SSR entry: {e}")

    def count_rag_documents(self) -> int:
        """Counts the number of documents in the RAG collection."""
        if not self.client: return 0
        return self.rag_collection.count_documents({})

    def find_shi_metadata(self, shi_prefix: str) -> Optional[dict]:
        """Retrieves full source metadata by SHI prefix (for verification)."""
        if not self.client: return None
        return self.ssr_collection.find_one({"SHI": {"$regex": f"^{shi_prefix}"}})

    def store_chunk(self, shi: str, chunk_id: str, content: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        """
        Stores a single chunk of a document in MongoDB.
        @param shi: Source Hash Identity of the document.
        @param chunk_id: Unique identifier for the chunk within the document.
        @param content: The text content of the chunk.
        @param embedding: The vector embedding of the chunk's content.
        @param metadata: Additional metadata for the chunk (e.g., page number, paragraph number).
        """
        document = {
            "shi": shi,
            "chunk_id": chunk_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
            "timestamp": datetime.now()
        }
        self.rag_collection.update_one(
            {"shi": shi, "chunk_id": chunk_id},
            {"$set": document},
            upsert=True
        )
        log.debug(f"Successfully stored/updated chunk {chunk_id} for SHI {shi} in MongoDB.")

    def retrieve_chunk(self, shi: str, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific chunk from MongoDB.
        :param shi: Source Hash Identity.
        :param chunk_id: Chunk identifier.
        :return: The chunk document or None if not found.
        """
        return self.rag_collection.find_one({"shi": shi, "chunk_id": chunk_id})

    def retrieve_chunks_by_shi(self, shi: str) -> List[Dict[str, Any]]:
        """
        Retrieves all chunks for a given SHI.
        :param shi: Source Hash Identity.
        :return: A list of chunk documents.
        """
        return list(self.rag_collection.find({"shi": shi}).sort("chunk_id", 1))

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            log.info("MongoDB connection closed.")

def store_source_chunks(mongo_client: MongoDBClient, shi: str, chunks_to_store: List[Dict[str, Any]], embed_content_func: Any, sentences_per_chunk: int = 3) -> None:
    """
    Generates embeddings for pre-chunked content and stores them in MongoDB.
    @param mongo_client: The MongoDB client instance.
    @param shi: Source Hash Identity of the document.
    @param chunks_to_store: A list of dictionaries, each representing a chunk with 'content', 'chunk_id', 'loc_selector', and 'metadata'.
    @param embed_content_func: A function (e.g., genai.embed_content) to generate embeddings.
    @param sentences_per_chunk: The number of sentences to group into each chunk (kept for compatibility, but not directly used for splitting here).
    """
    for chunk_data in chunks_to_store:
        chunk_content = chunk_data['content']
        chunk_id = chunk_data['chunk_id']
        loc_selector = chunk_data['loc_selector']
        metadata = chunk_data['metadata']
        
        stripped_chunk_content = chunk_content.strip()
        
        if not stripped_chunk_content:
            continue

        try:
            embedding_response = embed_content_func(
                model=Config.EMBEDDING_MODEL,
                content=stripped_chunk_content,
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=Config.EMBEDDING_DIMENSION
            )
            embedding = embedding_response['embedding']
        except Exception as e:
            log.error(f"Failed to generate embedding for chunk {chunk_id} of SHI {shi}: {e}")
            embedding = []
        
        chunk_metadata = {**metadata, "loc": loc_selector}
            
        mongo_client.store_chunk(shi, chunk_id, stripped_chunk_content, embedding, chunk_metadata)
        sleep(2)
    log.info(f"Stored {len(chunks_to_store)} chunks for SHI: {shi}")
