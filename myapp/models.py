from django.db import models
from django.contrib.auth.models import User


class Land(models.Model):

    LAND_TYPE_CHOICES = [
       ("residential", "Residential"),
       ("commercial", "Commercial"),
       ("agricultural", "Agricultural"),
       ("plot", "Plot"),
       ("farm", "Farm"),
    ]

    # 🔥 Link with logged-in user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lands")

    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    # 🔥 ADD BELOW location field

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    property_type = models.CharField(
        max_length=20,
        choices=LAND_TYPE_CHOICES
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    area = models.CharField(max_length=100)

    description = models.TextField()

    # 🔥 OPTIONAL (keep for display)
    owner_name = models.CharField(max_length=150, blank=True)
    owner_phone = models.CharField(max_length=15, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LandImage(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="lands/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Image for {self.land.title}"


class SavedProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_properties")
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'land')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.land.title}"


class Inquiry(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name="inquiries")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inquiries_sent")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry from {self.buyer.username} for {self.land.title}"

    
class Lead(models.Model):

    # 👤 Customer details
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)

    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    # 🔗 Optional: link to property
    land = models.ForeignKey(
        "Land",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads"
    )

    # 📊 Source tracking
    source = models.CharField(max_length=100, default="website")

    # 🕒 Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"