from django.urls import path
from . import views




urlpatterns = [
    
    path("documents/", views.MbrDocumentsAPI.as_view(), name="member-documents"),

]