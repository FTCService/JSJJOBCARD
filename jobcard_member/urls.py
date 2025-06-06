from django.urls import path
from .views import Documentapi
from helpers.swagger_document import schema_view
from .views import Documentapi
app_name ='jobcard_member'

urlpatterns = [
    path('upload/', Documentapi.as_view(), name='upload-document'),
  
]
