"""URL configuration for document endpoints."""
from django.urls import path
from .views import DocumentListCreateView, DocumentDeleteView, DocumentServeView

app_name = 'documents'

urlpatterns = [
    path('', DocumentListCreateView.as_view(), name='list-create'),
    path('<uuid:pk>/', DocumentDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/download/', DocumentServeView.as_view(), name='download'),
]
