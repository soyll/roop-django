from django.urls import path
from .views import DownloadReportView, ReviewListCreateView, FaceSwapTaskCreateView, FaceSwapTaskStatusView, TemplateReplaceView, UploadReportView

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view()),
    path('faceswap/', FaceSwapTaskCreateView.as_view()),
    path('faceswap/<uuid:pk>/', FaceSwapTaskStatusView.as_view()),
    path('template-replace/', TemplateReplaceView.as_view()),
    path('report/download/', DownloadReportView.as_view()),
    path('report/upload/', UploadReportView.as_view()),
]