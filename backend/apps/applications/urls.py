"""URL configuration for application endpoints."""
from django.urls import path
from .views import (
    MyApplicationView,
    CreateApplicationView,
    SubmitApplicationView,
    ApplicationStatusView,
)

app_name = 'applications'

urlpatterns = [
    path('me/', MyApplicationView.as_view(), name='my-application'),
    path('', CreateApplicationView.as_view(), name='create'),
    path('<uuid:pk>/submit/', SubmitApplicationView.as_view(), name='submit'),
    path('<uuid:pk>/status/', ApplicationStatusView.as_view(), name='status'),
]
