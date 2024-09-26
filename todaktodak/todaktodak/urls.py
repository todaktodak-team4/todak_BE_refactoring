from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin4242/', admin.site.urls),
    path('accounts/', include('accounts.urls')), # 추가
    path('',include('rememberTree.urls')),
    path('', include('memorialHall.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

