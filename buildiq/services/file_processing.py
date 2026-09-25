import json
import requests
from io import BytesIO
from .ai_tools import AIUtils
from buildiq.utils import UtilFunctions
from buildiq.services.vector_db_helper import VectorDBUtils


class FileProcessingService:
    def __init__(self):
        self.util = UtilFunctions()
        self.ai_tool = AIUtils()
        self.vector_db = VectorDBUtils()

    def process_file(self, file, file_type, uploaded_from):

        try:
            if file_type not in ["image/jpeg", "application/pdf"]:
                return {"success": False, "error": "Unsupported file type"}

            if uploaded_from == "mobile":
                response = requests.get(file)
                if response.status_code != 200:
                    return {"success": False, "error": "Unable to download file"}
                file = response.content

            else:
                file = file.read()

            raw_bytes = file

            if file_type == "application/pdf":
                pdf_bytes = file
                pdf_image_result = self.util.convert_pdf_to_image(pdf_bytes)
                if not pdf_image_result["success"]:
                    return pdf_image_result

                image = pdf_image_result["image"]
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='JPEG')  # Convert image to raw bytes
                raw_bytes = img_byte_arr.getvalue()

            extracted_text_result = self.ai_tool.extract_text_from_image(
                raw_bytes)
            if not extracted_text_result["success"]:
                return extracted_text_result

            try:
                extracted_data = json.loads(extracted_text_result["data"])
                print('extracted data as json', extracted_data)
            except json.JSONDecodeError:
                return {"success": False, "error": "Extracted text is not a valid JSON format"}

            search_results = self.search_items_in_vector_db(extracted_data)

            if not search_results.get("success"):
                return search_results

            vector_results_dict = {
                item["item_name"]: item["similar_items"]
                for item in search_results["results"]
            }

            all_items_matched = True

            for item in extracted_data["item_details"]:
                item_name = item["name"]
                similar_items = vector_results_dict.get(item_name, [])

                item["similar_items"] = similar_items
                item["match_found"] = bool(similar_items)

                if not similar_items:
                    all_items_matched = False

            extracted_data["all_items_matched"] = all_items_matched

            return {"success": True, "data": extracted_data}

        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def search_items_in_vector_db(self, extracted_data):
        try:
            item_details = extracted_data.get("item_details", [])
            if not item_details:
                print("No items found in the bill.")
                return {"success": True, "results": []}

            search_results = []
            collection_name = "item_collection"

            for item in item_details:
                item_name = item.get("name")
                if item_name:
                    print(
                        f"Passing item {item_name} to search for similar items")

                    similar_items = self.vector_db.search_similar_items(
                        collection_name, item_name
                    )

                    if not similar_items.get("success"):
                        return {
                            "success": False,
                            "error": similar_items.get("error"),
                            "type": similar_items.get("type"),
                        }

                    search_results.append({
                        "item_name": item_name,
                        "similar_items": similar_items.get("matches", [])
                    })
            print('returning the json from file processing service', search_results)
            return {"success": True, "results": search_results}

        except Exception as e:
            print(f"Error searching vector DB: {e}")
            return {"success": False, "error": str(e), "type": e.__class__.__name__}
