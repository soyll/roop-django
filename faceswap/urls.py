from django.urls import path
from .views import ReviewListCreateView, FaceSwapTaskCreateView, FaceSwapTaskStatusView

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view()),
    path('faceswap/', FaceSwapTaskCreateView.as_view()),
    path('faceswap/<uuid:pk>/', FaceSwapTaskStatusView.as_view()),
]
