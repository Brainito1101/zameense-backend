from django.contrib.sitemaps import Sitemap
from .models import Land

class LandSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Land.objects.all()

    def location(self, obj):
        return f"https://zameense-frontend.vercel.app/land/{obj.id}/"