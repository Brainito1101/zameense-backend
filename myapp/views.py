from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Land, Lead, LandImage, SavedProperty, Inquiry
from .serializers import (
    LandSerializer, LeadSerializer, LandImageSerializer, 
    SavedPropertySerializer, InquirySerializer, RegisterSerializer
)
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import EmailTokenObtainPairSerializer
from django.shortcuts import render
from django.http import JsonResponse

from django.shortcuts import render

def frontend(request):
    return render(request, "index.html")


def home(request):
    return JsonResponse({
        "status": "API is running 🚀"
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def contact(request):
    serializer = LeadSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Thank you for contacting us. We will be in touch soon."}, status=201)
    return Response(serializer.errors, status=400)




class LandViewSet(viewsets.ModelViewSet):
    queryset = Land.objects.all().prefetch_related('images', 'saved_by', 'inquiries')
    serializer_class = LandSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Land.objects.all()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset

    def perform_create(self, serializer):
        land = serializer.save(user=self.request.user)
        images = self.request.FILES.getlist('images')
        if not images and self.request.FILES.get('image'):
            images = [self.request.FILES.get('image')]
        for image in images:
            LandImage.objects.create(land=land, image=image)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_properties(self, request):
        lands = Land.objects.filter(user=request.user)[:20]
        serializer = self.get_serializer(lands, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_images(self, request, pk=None):
        land = self.get_object()
        
        # Check ownership
        if land.user != request.user:
            return Response(
                {'detail': 'You can only upload images to your own properties'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        files = request.FILES.getlist('images')
        if not files:
            return Response(
                {'detail': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for file in files:
            img = LandImage.objects.create(land=land, image=file)
            created_images.append(LandImageSerializer(img).data)
        
        return Response(created_images, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_image(self, request, pk=None):
        try:
            image_id = request.query_params.get('image_id')
            image = LandImage.objects.get(id=image_id, land_id=pk)
            
            if image.land.user != request.user:
                return Response(
                    {'detail': 'You can only delete images from your own properties'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LandImage.DoesNotExist:
            return Response(
                {'detail': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, *args, **kwargs):
        land = self.get_object()
        if land.user != request.user:
            return Response(
                {'detail': 'You can only delete your own properties'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        land = self.get_object()
        if land.user != request.user:
            return Response(
                {'detail': 'You can only update your own properties'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class SavedPropertyViewSet(viewsets.ModelViewSet):
    serializer_class = SavedPropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedProperty.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_save(self, request):
        land_id = request.data.get('land_id')
        
        if not land_id:
            return Response(
                {'detail': 'land_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            land = Land.objects.get(id=land_id)
        except Land.DoesNotExist:
            return Response(
                {'detail': 'Land not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        saved, created = SavedProperty.objects.get_or_create(
            user=request.user,
            land=land
        )
        
        if not created:
            saved.delete()
            return Response(
                {'detail': 'Property unsaved'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            SavedPropertySerializer(saved).data,
            status=status.HTTP_201_CREATED
        )


class InquiryViewSet(viewsets.ModelViewSet):
    serializer_class = InquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get inquiries received (as seller) and sent (as buyer)
        return Inquiry.objects.filter(land__user=user) | Inquiry.objects.filter(buyer=user)

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def received(self, request):
        inquiries = Inquiry.objects.filter(land__user=request.user)
        serializer = self.get_serializer(inquiries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def sent(self, request):
        inquiries = Inquiry.objects.filter(buyer=request.user)
        serializer = self.get_serializer(inquiries, many=True)
        return Response(serializer.data)


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Land.objects.all()[:20]
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]