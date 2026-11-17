from django.urls import path
from .views import tool_calling

urlpatterns = [
    path("tool-calling/", tool_calling, name="tool-calling"),
]