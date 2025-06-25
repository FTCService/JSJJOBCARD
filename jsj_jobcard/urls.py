from django.contrib import admin
from django.urls import path, include
from helpers import swagger_documentation

urlpatterns = [
    path('admin/', include('jobcard_admin.urls')),
    path('business/', include('jobcard_business.urls')),
    path('staff/', include('jobcard_staff.urls')),
    path('goverment/', include('goverment.urls')),
    path('member/', include('jobcard_member.urls')),
    path('swagger/', swagger_documentation.schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', swagger_documentation.schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]