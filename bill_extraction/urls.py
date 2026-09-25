from django.urls import path
from . import views

urlpatterns = [
    path("generate-qr/<str:session_id>/",
         views.GenerateQRCodeView.as_view(), name="generate_qr"),
    path("session/status/<str:session_id>/",
         views.CheckSessionStatusView.as_view(), name="check_session_status"),
    path("session/all/",
         views.AllSessionStatusView.as_view(), name="all_session"),
    path("upload/<str:session_id>/",
         views.FileUploadView.as_view(), name="upload_file"),
    path("delete/<str:session_id>/",
         views.FileUploadView.as_view(), name="delete_file"),
    path("extract/", views.FileProcessingView.as_view(), name="extract_from_file"),
    path("update-item/",
         views.UpdateItemInVectorDBView.as_view(), name="update_item_in_vector_db"),
]
