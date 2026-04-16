from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets
from .models import LandImage
from django.http import JsonResponse
from .models import Land, Lead, LandImage, SavedProperty, Inquiry
from .serializers import (
    LandSerializer, LeadSerializer, LandImageSerializer,
    SavedPropertySerializer, InquirySerializer
)

# ✅ Home API
def home(request):
    return JsonResponse({
        "status": "API is running 🚀"
    })


# ✅ Contact API (save leads)
@api_view(['POST'])
@permission_classes([AllowAny])
def contact(request):
    serializer = LeadSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Thank you! We will contact you soon."
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LandViewSet(viewsets.ModelViewSet):
    queryset = Land.objects.all().prefetch_related('images')
    serializer_class = LandSerializer
    permission_classes = [AllowAny]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_context(self):
        return {'request': self.request}
    
    # ✅ CUSTOM CREATE METHOD
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # ✅ Save without user (no login system)
            land = serializer.save(user=None)

            # ✅ Handle images
            images = request.FILES.getlist('images')

            if not images and request.FILES.get('image'):
                images = [request.FILES.get('image')]

            for image in images:
                LandImage.objects.create(land=land, image=image)

            return Response(
                {"message": "Land added successfully ✅"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LandImageViewSet(viewsets.ModelViewSet):
    queryset = LandImage.objects.all()
    serializer_class = LandImageSerializer

    def create(self, request, *args, **kwargs):
        # ✅ Convert land to integer from FormData string
        data = request.data.copy()
        if 'land' in data:
            data['land'] = int(data['land'])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

# ✅ Lead API (GET ALL LEADS)
class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by('-id')
    serializer_class = LeadSerializer
    permission_classes = [AllowAny]

    filter_backends = [SearchFilter]
    search_fields = ['name', 'email', 'phone']


# 🔒 Optional (keep for future login system)

class SavedPropertyViewSet(viewsets.ModelViewSet):
    serializer_class = SavedPropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedProperty.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InquiryViewSet(viewsets.ModelViewSet):
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Inquiry.objects.all()

    def perform_create(self, serializer):
        serializer.save()