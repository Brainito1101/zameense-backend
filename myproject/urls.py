from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from lands.sitemap import LandSitemap

sitemaps = {
    'lands': LandSitemap,
}


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
]


# Serve static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)