import uuid
import qdrant_client
from .ai_tools import AIUtils
from django.conf import settings
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)



class VectorDBUtils:
    def __init__(self, host=settings.VECTOR_DB_HOST, port=settings.VECTOR_DB_PORT):
        self.client = qdrant_client.QdrantClient(host=host, port=port)
        self.ai_utils = AIUtils()

    def create_collection(self, collection_name, vector_size=1536, distance=Distance.COSINE):
        try:
            print(f"Checking if collection '{collection_name}' exists...")
            already_exists = self.client.collection_exists(collection_name)
            if not already_exists:
                print(
                    f"Collection '{collection_name}' doesn't exist. Creating it now...")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size, distance=distance),
                )
                print(f"Collection '{collection_name}' created successfully.")
            else:
                print(f"Collection '{collection_name}' already exists.")
            return {"success": True, "already_exists": already_exists}
        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def insert_documents(self, collection_name, documents):
        try:
            print("Checking for existing items before insertion...")
            for doc in documents:
                existing_points = self.client.scroll(
                    collection_name=collection_name,
                    limit=1,
                    scroll_filter=Filter(
                        must=[FieldCondition(
                            key="id", match=MatchValue(value=doc["id"]))]
                    )
                )

                if existing_points[0]:
                    print(
                        f"Item with ID {doc['id']} already exists. Skipping insertion.")
                    continue

                embedding_result = self.ai_utils.get_embedding_for_text(
                    doc["text"])
                if embedding_result["success"]:
                    embedding = embedding_result["embedding"]
                    point = PointStruct(
                        id=doc["id"],
                        vector=embedding,
                        payload={**doc["metadata"],
                                 "id": doc["id"], "text": doc["text"]}
                    )
                    self.client.upsert(
                        collection_name=collection_name, points=[point])
                    print(f"Inserted item with ID {doc['id']} successfully.")
                else:
                    print(
                        f"Error generating embedding for ID {doc['id']}: {embedding_result['error']}")

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def search_similar_items(self, collection_name, query_text, limit=5, threshold=0.95):
        try:
            print(f"Searching for metadata match for: {query_text}")

            # Step 1: Try metadata (payload) search
            metadata_result = self.client.scroll(
                collection_name=collection_name,
                limit=1,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="similar_item_names",
                            match=MatchValue(value=query_text)
                        )
                    ]
                )
            )
            matched_points = metadata_result[0]

            if matched_points:
                point = matched_points[0]
                confidence = 100.0  # Full confidence on metadata match
                print(f"Found metadata match: {point.payload}")

                return {
                    "success": True,
                    "match_found": True,
                    "matches": [{
                        "id": point.id,
                        "item_key": point.payload["item_key"],
                        "text": point.payload["db_item_name"],
                        "confidence": confidence
                    }]
                }

            # Step 2: Fallback to vector similarity
            print("No metadata match found. Falling back to vector search...")
            query_vector_result = self.ai_utils.get_embedding_for_text(
                query_text)
            if not query_vector_result["success"]:
                return {"success": False, "error": query_vector_result["error"]}

            query_vector = query_vector_result["embedding"]

            result = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                with_vectors=False,
                with_payload=True,
                limit=limit
            )

            matches = []
            for point in result.points:
                confidence = round(point.score * 100, 2)

                if confidence >= threshold * 100:
                    print(
                        f"Valid Match: ID={point.id}, DB Text='{point.payload['db_item_name']}', Confidence={confidence}%"
                    )
                    matches.append({
                        "id": point.id,
                        "item_key": point.payload["item_key"],
                        "text": point.payload["db_item_name"],
                        "confidence": confidence
                    })

            matches.sort(key=lambda x: x["confidence"], reverse=True)

            return {
                "success": True,
                "match_found": bool(matches),
                "matches": matches
            }

        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def get_or_create_similar_item_vector(self, db_item_name, scanned_item_name, item_key, collection='item_collection'):
        try:
            # Step 1: Ensure the collection exists
            result = self.create_collection(collection_name=collection)
            if result["success"]:
                print(
                    f"Collection status: {'already existed' if result['already_exists'] else 'created'}")
            else:
                return {"success": False, "error": result["error"]}

            # Step 2: Search for an existing point with this db_item_name
            scroll_result = self.client.scroll(
                collection_name=collection,
                limit=1,
                scroll_filter=Filter(
                    must=[FieldCondition(
                        key="db_item_name", match=MatchValue(value=db_item_name))]
                )
            )

            existing_points = scroll_result[0]
            if existing_points:
                point = existing_points[0]
                point_id = point.id
                payload = point.payload
                similar_names = set(payload.get("similar_item_names", []))

                if scanned_item_name not in similar_names:
                    # Step 3a: Update existing vector's payload with new scanned name
                    similar_names.add(scanned_item_name)
                    updated_payload = {
                        "item_key": item_key,
                        "db_item_name": db_item_name,
                        "similar_item_names": list(similar_names)
                    }

                    self.client.set_payload(
                        collection_name=collection,
                        payload=updated_payload,
                        points=[point_id]
                    )
                    print(
                        f"Updated payload with new similar name: {scanned_item_name}")
                else:
                    print(
                        f"Scanned item already associated with db_item_name: {db_item_name}")

                return {"success": True, "item_key": payload["item_key"], "match_found": True}

            else:
                # Step 3b: Create new vector for db_item_name with scanned_item_name
                embedding_result = self.ai_utils.get_embedding_for_text(
                    db_item_name)
                if not embedding_result["success"]:
                    return {"success": False, "error": embedding_result["error"]}

                embedding = embedding_result["embedding"]
                new_point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "item_key": item_key,
                        "db_item_name": db_item_name,
                        "similar_item_names": [scanned_item_name]
                    }
                )
                self.client.upsert(
                    collection_name=collection, points=[new_point])
                print(f"Inserted new vector for db_item_name: {db_item_name}")

                return {"success": True, "item_key": item_key, "match_found": False}

        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}
