from django.contrib import admin
from django.urls import path, include, re_path
from helpers import swagger_document


urlpatterns = [
    path('admin/', admin.site.urls),

    # Replace 'app_common' with your actual apps:
    
    path('api/member/', include('jobcard_member.urls')),
    path('api/business/', include('jobcard_business.urls')),
    

    # Swagger & ReDoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', swagger_document.schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', swagger_document.schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', swagger_document.schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
