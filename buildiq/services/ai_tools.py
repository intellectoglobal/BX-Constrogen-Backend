import openai
from google import genai
from google.genai.types import Part
from django.conf import settings


class AIUtils:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.gemini_api_key = settings.GEMINI_API_KEY

    def extract_text_from_image(self, raw_bytes):
        client = genai.Client(api_key=self.gemini_api_key)
        print('Extracting content from image')

        prompt = """Extract the details from this bill and return only a structured JSON object without any additional text, markdown, or explanations. The JSON should include:
            - vendor_name
            - date (convert to 'YYYY-MM-DD' format, e.g., '2025-10-31', even if the original format is different)
            - vendor_invoice_no (Invoice No. or Inv. No. or Invoice No)x
            - total_bill_amount
            - sgst_percentage
            - sgst_amount
            - cgst_percentage
            - cgst_amount
            - total_tax_percentage (sum of cgst_percentage and sgst_percentage if both exist, otherwise 'UNKNOWN')
            - total_tax_amount (sum of cgst_amount and sgst_amount if both exist, otherwise 'UNKNOWN')
            - transport (packing, forwarding, delivery charges, Packing & Forwarding Charges)
            - discount (negative amounts or explicit 'discount' mentions)
            - rounded_off
            - loading_unloading_charges
            - item_details (name, quantity, uom (bags, kgs, length, nos), total_price)

            If any field is missing, return 'UNKNOWN'. Respond with only valid JSON and nothing else.
            """

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=[
                prompt,
                Part.from_bytes(
                    data=raw_bytes,
                    mime_type="image/jpeg",
                ),
            ],
        )
        response_content = response.text
        print('response_content', response_content)
        if response_content.startswith("```json") and response_content.endswith("```"):
            print("Removing Markdown code block syntax...")
            response_content = response_content[7:-3].strip() 
        print(f"Processed response content: {response_content}")
        return {"success": True, "data": response_content}

    # def extract_text_from_image(self, base64_image):
    #     try:
    #         openai.api_key = self.api_key
    #         print('Extracting content from image')

    #         prompt = """Extract the details from this bill and return only a structured JSON object without any additional text, markdown, or explanations. The JSON should include the following fields:
    #         - vendor_name
    #         - bill_category (e.g., grocery, electronics, hardware)
    #         - date (convert to 'YYYY-MM-DD' format, e.g., '2025-10-31', even if the original format is different)
    #         - vendor_invoice_no (Invoice No. or Inv. No. or Invoice No)
    #         - total_bill_amount
    #         - sgst_percentage
    #         - sgst_amount
    #         - cgst_percentage
    #         - cgst_amount
    #         - total_tax_percentage (sum of cgst_percentage and sgst_percentage if both exist, otherwise 'UNKNOWN')
    #         - total_tax_amount (sum of cgst_amount and sgst_amount if both exist, otherwise 'UNKNOWN')
    #         - transport (packing, forwarding, or delivery charges)
    #         - discount (negative amounts or explicit 'discount' mentions)
    #         - rounded_off
    #         - loading_unloading_charges
    #         - item_details (name, quantity (kgs, nos), total_price)

    #         If any field is missing, return 'UNKNOWN'. Respond with *only* valid JSON and nothing else.
    #         """

    #         chat_completion = openai.chat.completions.create(
    #             model="gpt-4o-mini",
    #             max_tokens=1000,
    #             messages=[
    #                 {
    #                     "role": "user",
    #                     "content": [
    #                         {"type": "text", "text": prompt},
    #                         {"type": "image_url", "image_url": {
    #                             "url": f"data:image/jpeg;base64,{base64_image}"}}
    #                     ]
    #                 }
    #             ]
    #         )
    #         response_content = chat_completion.choices[0].message.content
    #         return {"success": True, "data": response_content}

    #     except openai.OpenAIError as oe:
    #         return {"success": False, "error": str(oe), "type": "OpenAIError"}

    #     except Exception as e:
    #         return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def get_embedding_for_text(self, text):
        try:
            print("Creating embedding for text", text)
            if not text:
                return {"success": False, "error": "Input text cannot be empty", "type": "ValidationError"}

            openai_client = openai.OpenAI(api_key=self.api_key)
            response = openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return {"success": True, "embedding": response.data[0].embedding}

        except openai.OpenAIError as oe:
            return {"success": False, "error": str(oe), "type": "OpenAIError"}

        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}
