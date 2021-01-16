from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'queuemining'


urlpatterns = [
    path('', views.get_data, name='get_data'),
    path('view_table', views.view_table, name='view_table'),
    path('view_analysis', views.view_analysis, name='view_analysis')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
