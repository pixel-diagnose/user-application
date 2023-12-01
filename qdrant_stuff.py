from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)
from qdrant_client.http import models
import os
from dotenv import dotenv_values

config = dotenv_values(".env")


def start_qdrant_connection():
    global qdrant_client
    qdrant_client = QdrantClient(
        url="https://e4327f42-67e1-4430-98a1-8bb0ae225101.us-east4-0.gcp.cloud.qdrant.io:6333",
        api_key=config["qdrant_api"],
    )


collection_name = "resnet50_imagenet_embeddings"


def get_similar_embeddings(
    collection_name,
    search_vector,
    num_results,
    filter_diagnose=None,
    filter_image_type=None,
):
    """Gets similar embeddings according to specified distance metric. Returns num_results most similar embeddings

    Args:
        #### qdrant_client (qdrant_client.QdrantClient): qdrant client
        collection_name (String): Name of qdrant-colleciton
        search_vector (list): vector-list
        num_results (int): number of mist similar embeddings to be returned
        filter_diagnose (list(String), optional): diagnoses to filter - please provide a list of Strings
        filter_image_type (String, optional): image-type (t1, t2 etc.) to filter
    Returns:
        list: search_result
    """
    # Parse filter input
    if filter_diagnose and filter_image_type:
        filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="image_type",
                    match=models.MatchValue(value=filter_image_type),
                ),
                models.FieldCondition(
                    key="diagnose",
                    match=models.MatchValue(value=filter_diagnose),
                ),
            ]
        )
    elif filter_diagnose:
        filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="diagnose",
                    match=models.MatchValue(value=filter_diagnose),
                )
            ]
        )
    elif filter_image_type:
        filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="image_type",
                    match=models.MatchValue(value=filter_image_type),
                )
            ]
        )
    else:
        filter = None

    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=search_vector,
        query_filter=filter,
        limit=num_results,
    )

    # Transform so it returns a json
    search_result_dict = {}
    for counter, i in enumerate(search_result):
        payload = i.payload
        payload["score"] = i.score

        search_result_dict[counter] = payload

    return search_result_dict
