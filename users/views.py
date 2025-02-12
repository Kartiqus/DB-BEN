from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Profile, User
from .serializers import UserSerializer, ProfileSerializer, RegisterSerializer
from orders.models import Order

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def top_customers(request):
    customers = User.objects.annotate(
        total_orders=Count('order'),
        total_spent=Sum('order__total_amount')
    ).order_by('-total_spent')[:10]
    
    return Response(UserSerializer(customers, many=True).data)