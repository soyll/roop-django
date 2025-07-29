from django.urls import path
from .views import DownloadReportView, ReviewListCreateView, FaceSwapTaskCreateView, FaceSwapTaskStatusView, TemplateReplaceView, UploadReportView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view()),
    path('faceswap/', FaceSwapTaskCreateView.as_view()),
    path('faceswap/<uuid:pk>/', FaceSwapTaskStatusView.as_view()),
    path('template-replace/', TemplateReplaceView.as_view()),
    path('report/download/', DownloadReportView.as_view()),
    path('report/upload/', UploadReportView.as_view()),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]