from qdrant_client import QdrantClient
import os
from dotenv import dotenv_values

config = dotenv_values(".env")
print("==================================")
print(config["qdrant_api"])


def start_qdrant_connection():
    global qdrant_client
    qdrant_client = QdrantClient(
        url="https://e4327f42-67e1-4430-98a1-8bb0ae225101.us-east4-0.gcp.cloud.qdrant.io:6333",
        api_key=config["qdrant_api"],
    )


collection_name = "resnet50_imagenet_embeddings"


def get_similar_embeddings(search_vector, num_results):
    """Gets similar embeddings according to specified distance metric. Returns num_results most similar embeddings
    Args:
        qdrant_client (qdrant_client.QdrantClient): qdrant client
        collection_name (String): Name of qdrant-colleciton
        search_vector (list): vector-list
        num_results (int): number of mist similar embeddings to be returned
    Returns:
        list: search_result
    """
    search_result = qdrant_client.search(
        collection_name=collection_name, query_vector=search_vector, limit=num_results
    )
    print("we have received data from qdrant")
    return search_result[0].payload
