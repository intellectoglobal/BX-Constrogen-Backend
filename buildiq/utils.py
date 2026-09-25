import fitz
import secrets
import qrcode
import string
import base64
import random
import requests
import smtplib

from PIL import Image
from io import BytesIO
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse, unquote
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework import status

from .redis import RedisHelper
from pricing.models import (Docid)
from client.models import Clientbase, Company
from project.models import Project, Projectblock, Projectfloor
from users.models import AppUser, AppUsersRole, AppUserCompany, AppRole

ENDPOINT_METHODS_DICT = {
    'GET': {'get': 'list'},
    'POST': {'post': 'create'},
    'RETRIVE': {'get': 'retrieve'},
    'DELETE': {'delete': 'delete'},

    'GET_POST': {'get': 'list', 'post': 'create'},
    'RETRIVE_UPDATE': {'get': 'retrieve', 'put': 'update'},
    'UPDATE_DELETE': {'put': 'update', 'delete': 'delete'},
    'RETRIVE_DELETE': {'get': 'retrieve', 'delete': 'delete'},

    'RETRIVE_UPDATE_DELETE': {'get': 'retrieve', 'put': 'update', 'delete': 'delete'},
}


class UtilFunctions:

    def __init__(self):
        self.UNIT_STATUS = {
            'A':  {
                "label": "Available",
                "value": "A",
            },
            'B': {
                "label": "Booked",
                "value": "B",
            },
            'S': {
                "label": "Sold",
                "value": "S",
            },
        }

        self.DOCS = {
            "VIN": "Vendor Invoice",
            "GR1": "Goods Receipt Note Project",
            "GR2": "Goods Receipt Note Purchase",
            "GR3": "Goods Receipt Note Inventory",
            "PT": "Purchase Template",
            "PO": "Purchase Order",
            "VCN": "Vendor Contract",
            "VCI": "Vendor Contract Invoice",
            "PYV": "Payment Voucher",
            "SLB": "Sale Booking",
            "SLA": "Sale Agreement",
            "SIN": "Sale Invoice",
            "CAN": "Contract Agreement Number",
            "CIN": "Contractor Invoice",
            "VN": "Voucher Number",
            "VVN": "Vendor Voucher Number",
            "CA": "Construction Agreement",
            "SR": "Sale Receipt",
            "LD": "Leads"
        }

        self.clientAndCompanyReturnMessage = {
            "INVALID_CLIENT_AND_COMPANY_ID": {
                "message": "Invalid Client ID and Company ID Found",
                "http_status": status.HTTP_400_BAD_REQUEST
            },
            "CLIENT_AND_COMPANY_ID_MISSING": {
                "message": "x-account Header Missing",
                "http_status": status.HTTP_403_FORBIDDEN
            }
        }

    def getClientInfo(self, request):
        if request.headers.get("x-account", False):

            try:
                encrpToken = request.headers.get("x-account")
                clientInfo = base64.b64decode(
                    encrpToken).decode('utf-8').split("|")
                if Company.objects.filter(client=clientInfo[0], id=clientInfo[1]).exists():
                    return True, {}, clientInfo[0], clientInfo[1]
                else:
                    return False, self.clientAndCompanyReturnMessage["INVALID_CLIENT_AND_COMPANY_ID"], None, None
            except:
                return False, self.clientAndCompanyReturnMessage["INVALID_CLIENT_AND_COMPANY_ID"], None, None

        return False, self.clientAndCompanyReturnMessage["CLIENT_AND_COMPANY_ID_MISSING"], None, None

    def getCurrentSessionUser(self, req):
        if str(req.user) == 'AnonymousUser':
            return "Unknown"
        return req.user.user_name

    def removePrefix(self, data, pref):
        return [{key.replace(pref, ''): d[key] for key in d.keys()} for d in data]

    def get_Error_Object(self, message):
        return {"error": 1, "message": message}

    def send_email(self, receiver_email, subject, context):
        try:
            smtp_server = settings.SMTP_SERVER
            smtp_port = settings.SMTP_PORT
            sender_email = settings.SENDER_EMAIL
            sender_password = settings.SENDER_PASSWORD
            html_template = 'emails/otp_template.html'

            html_body = render_to_string(html_template, context)
            plain_body = f"Your OTP is {context.get('otp', '')}. Please use it to log in. Do not share it."

            message = MIMEMultipart("alternative")
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            message.attach(MIMEText(plain_body, "plain"))
            message.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())

            return {"error": 0, "message": "Email sent successfully!"}

        except Exception as e:
            return {"error": 1, "message": f"An error occurred while sending email: {str(e)}."}


    def send_otp(self, email):
        try:
            session = ''.join(random.choices(string.ascii_uppercase + string.digits, k=28))
            if settings.ENV_VALUE ==  'prod':
                otp = str(secrets.randbelow(10**6)).zfill(6)

                subject = "OTP for logging in"
                context = {
                    'otp': otp,
                    'year': datetime.now().year,
                    'constrogen_logo_url': 'https://constrogen-storage-bucket.s3.ap-south-1.amazonaws.com/Assets/logo-no-bg.png',
                    'intellion_icon_url': 'https://constrogen-storage-bucket.s3.ap-south-1.amazonaws.com/Assets/intellion+icon.png'
                }

                email_result = self.send_email(email, subject, context)
                if email_result['error'] == 1:
                    return {"error": 1, "message": email_result['message']}

                redis = RedisHelper()
                result = redis.store_otp(email=email, otp=otp)
                if not result:
                    return {"error": 1, "message": "Error while storing the OTP sent", "sessionID": None}
                
            return {
                "error": 0,
                "message": "If the email is valid, you'll receive an OTP shortly.",
                "sessionID": session
            }
        except Exception as e:
            return {"error": 1, "message": f"An error occurred while sending OTP: {str(e)}."}


    def verify_otp(self, email, otp):
        result = True
        message = None
        if settings.ENV_VALUE ==  'prod':
            redis = RedisHelper()
            result, message = redis.verify_otp(
                email=email, otp=otp)
        if not result:
            return {"error": 1, "message": message}
        return {"error": 0, "message": message}

    def get_Custom_OTP(self):
        return {
            "otp": random.randint(10000, 99999),
            "sessionID": ''.join(random.choices(string.ascii_uppercase +
                                                string.digits, k=28))
        }

    def validateOTPGETData(self, email):
        error = False
        errorObj = {}
        if not email:
            errorObj = self.get_Error_Object("Email required")
            error = True
        if not AppUser.objects.filter(email=email).exists():
            errorObj = self.get_Error_Object(
                "No User Found With This Email")
            error = True
        return error, errorObj

    def validateOTPPOSTData(self, email, otpSID, otp):
        error = False
        errorObj = {}
        if (not email) and not error:
            errorObj = self.get_Error_Object("Valid Email required")
            error = True
        if not otpSID and not error:
            errorObj = self.get_Error_Object("Session ID required")
            error = True
        if not AppUser.objects.filter(email=email).exists() and not error:
            errorObj = self.get_Error_Object(
                "No User Found With This Email")
            error = True
        if (not otp or not isinstance(otp, int)) and not error:
            errorObj = self.get_Error_Object("Valid OTP required")
            error = True
        return error, errorObj

    def validateUserPostData(self, request):
        error = False
        errorObj = {}
        if len(AppUser.objects.filter(email=request.data['email'])) > 0:
            error = True
            errorObj = self.get_Error_Object("Email Already Exists")

        if len(AppUser.objects.filter(user_name=request.data['user_name'])) > 0:
            error = True
            errorObj = self.get_Error_Object("Username Already Taken")

        if len(AppUser.objects.filter(phone_number=request.data['phone_number'])) > 0:
            error = True
            errorObj = self.get_Error_Object("Phone Number Already Registered")
        return error, errorObj

    def isSuperAdmin(self, request):
        return self.hasAnyRole(request, ["superadmin"])

    def hasAnyRole(self, request, role_names):
        for role_name in role_names:
            role = AppRole.objects.filter(role__iexact=role_name).first()
            if role and AppUsersRole.objects.filter(user=request.user, role=role).exists():
                return True
        return False

    def isAuthenticatedUser(self, request):
         return request.user.is_authenticated


    def getPaginatedResultList(self, inputData, page, pagesize):

        if len(inputData) == 0:
            return {
                "count": 0,
                "page_count": 0,
                "next": None,
                "previous": None,
                "last_page": None,
                "results": inputData
            }

        data = Paginator(inputData, pagesize)
        paginatedData = data.page(page)

        next_page = previous_page = None
        if paginatedData.has_next():
            next_page = paginatedData.next_page_number()
        if paginatedData.has_previous():
            previous_page = paginatedData.previous_page_number()

        return {
            "count": data.count,
            "page_count": data.num_pages,
            "next": next_page,
            "previous": previous_page,
            "last_page": data.num_pages,
            "results": paginatedData.object_list
        }

    def getFullUnitStatus(self, statuscode):
        try:
            return self.UNIT_STATUS[statuscode]
        except:
            return {
                "label": "A",
                "value": "Available",
            }

    def userIdFromRequest(self, request, qtype):
        if qtype == 'FROM_QPARAM':
            username = request.GET.get('username')
        elif qtype == 'FROM_HEADER':
            username = request.header.get('username')
        elif qtype == 'FROM_BODY':
            username = request.data.get('username')

        return AppUser.objects.get(user_name__iexact=username).id

    def getCurrentDateAndTime(self):
        return datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

    def getCurrentDate(self):
        return datetime.today().strftime(
            '%Y-%m-%d')

    def obtainDOCNameFromDOCID(self, docid):
        return self.DOCS[docid]

    def getValidDocId(self, reqdocNo, docType, clientId):
        with transaction.atomic():
            docIDIns = Docid.objects.select_for_update().get(
                docid=docType,
                client_id=clientId
            )
            nextId = int(docIDIns.docnumber) + 1
            docIDIns.docnumber = nextId
            docIDIns.save(update_fields=["docnumber"])
        return nextId

    def incrementDocId(self, docType, clientId):
        docIDIns = Docid.objects.get(docid=docType, client_id=clientId)
        docIDIns.docnumber = int(docIDIns.docnumber) + 1
        docIDIns.save()

    # TODO: change the login during production to get the client and company based on the user

    def getCompanyInfo(self, user):
        if AppUserCompany.objects.filter(user=user).exists():
            appUserCompanyIns = AppUserCompany.objects.filter(
                user=user).first()
            return {
                "client_id": appUserCompanyIns.company.client.id,
                "company_id": appUserCompanyIns.company.id,
                "client_name": appUserCompanyIns.client_id.name,
                "company_name": appUserCompanyIns.company.name
            }
        else:
            return {"client_id": None, "company_id": None}

    def isNum(self, data):
        try:
            int(data)
            return True
        except ValueError:
            return False

    def generate_qr_code(self, data: str):
        try:
            if not data:
                raise ValueError("Missing required parameters: 'data'")

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill="black", back_color="white")

            response = HttpResponse(content_type="image/png")
            img.save(response, "PNG")

            return {"success": True, "response": response}

        except ValueError as ve:
            return {"success": False, "error": str(ve), "type": "ValueError"}
        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def encode_image(self, image_data, converted=False, is_raw_bytes=False):
        try:
            print('encoding image')

            if converted:
                if not isinstance(image_data, Image.Image):
                    raise ValueError(
                        "Expected a PIL Image object when 'converted' is True")

                buffered = BytesIO()
                image_data.save(buffered, format="PNG")
                img_byte_array = buffered.getvalue()

            elif is_raw_bytes:
                img_byte_array = image_data

            else:
                response = requests.get(image_data)
                if response.status_code != 200:
                    raise ValueError("Failed to download image")

                img_byte_array = response.content

            return {"success": True, "encoded_image": base64.b64encode(img_byte_array).decode("utf-8")}

        except ValueError as ve:
            return {"success": False, "error": str(ve), "type": "ValueError"}

        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def convert_pdf_to_image(self, pdf_bytes):
        try:
            print('converting pdf into image')
            pdf_file = BytesIO(pdf_bytes)
            pdf_document = fitz.open(stream=pdf_file, filetype="pdf")
            page = pdf_document[0]
            pix = page.get_pixmap()
            image = Image.frombytes(
                "RGB", [pix.width, pix.height], pix.samples)
            return {"success": True, "image": image}

        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}

    def create_s3_folder_structure(self, client_id, company_id, project_id=None, block_id=None, floor_ids=None, invoice=None):
        try:
            client = Clientbase.objects.get(id=client_id).name.strip()
            company = Company.objects.get(id=company_id).name.strip()
            base_path = f"{client}/{company}"

            if invoice:
                project = Project.objects.get(key=project_id).name.strip()
                base_path = f"{base_path}/{project}/Invoices"
            if project_id and block_id:
                project = Project.objects.get(key=project_id).name.strip()
                block = Projectblock.objects.get(key=block_id).descr.strip()

                base_path = f"{client}/{company}/{project}/{block}"

            if floor_ids:
                floor_names = list(Projectfloor.objects.filter(
                    key__in=floor_ids).values_list('descr', flat=True))
                floor_path = "_".join(name.strip() for name in floor_names)
                folder_path = f"{base_path}/{floor_path}"
            else:
                folder_path = base_path

            return folder_path

        except (Clientbase.DoesNotExist, Company.DoesNotExist, Project.DoesNotExist, Projectblock.DoesNotExist, Projectfloor.DoesNotExist) as e:
            raise ValueError(f"Data retrieval failed: {e}")

    def upload_file_to_s3(self, file_path: str, file_obj, content_type: str = None):
        try:
            if not file_obj:
                raise ValueError("No file provided for upload.")

            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            settings.S3_CLIENT.upload_fileobj(
                Fileobj=file_obj,
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_path,
                ExtraArgs=extra_args
            )

            file_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{file_path}"
            return file_url

        except (ValueError, NoCredentialsError, PartialCredentialsError, ClientError, Exception) as e:
            print(f"S3 Upload Error: {e}")
            return None

    def delete_file_from_s3(self, file_name):
        try:
            if not file_name:
                raise ValueError("Missing file name for deletion.")

            parsed_url = urlparse(file_name)
            object_key = unquote(parsed_url.path.lstrip('/'))
            settings.S3_CLIENT.delete_object(
                Bucket=settings.S3_BUCKET_NAME, Key=object_key)

            return {"success": True, "message": "File deleted successfully!"}

        except ValueError as ve:
            return {"success": False, "error": str(ve), "type": "ValueError"}

        except ClientError as ce:
            return {"success": False, "error": str(ce), "type": "ClientError"}

        except Exception as e:
            return {"success": False, "error": str(e), "type": e.__class__.__name__}
