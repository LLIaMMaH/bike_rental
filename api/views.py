# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Bike, Rental
from .serializers import UserRegistrationSerializer, UserLoginSerializer, RentalSerializer, BikeSerializer
from .tasks import send_rental_notification, send_return_notification


class RegisterView(generics.CreateAPIView):
    """View для регистрации пользователя."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    """View для авторизации пользователя."""
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Method POST для авторизации пользователя."""
        # print("Authentication classes:", self.authentication_classes)
        # print("Permission classes:", self.permission_classes)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AvailableBikesView(generics.ListAPIView):
    """View для получения списка доступных велосипедов."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BikeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """Method для получения списка доступных велосипедов."""
        return Bike.objects.filter(status=Bike.STATUS_AVAILABLE)


class RentBikeView(APIView):
    """View для аренды велосипеда."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    print('Мы тут - RentBikeView !!!')

    def post(self, request, bike_id):
        """Method POST для аренды велосипеда."""

        print(f'request - {request}')
        print(f'bike_id - {bike_id}')
        try:
            bike = Bike.objects.get(id=bike_id)
            if bike.status != Bike.STATUS_AVAILABLE:
                return Response({'error': 'Велосипед не доступен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            if Rental.objects.filter(user=request.user, end_time=None).exists():
                return Response({'error': 'Вы уже арендовали велосипед'}, status=status.HTTP_400_BAD_REQUEST)

            rental = Rental.objects.create(bike=bike, user=request.user)
            send_rental_notification.delay(rental.id)
            bike.status = Bike.STATUS_RENTED
            bike.save()
            serializer = RentalSerializer(rental)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Bike.DoesNotExist:
            return Response({'error': 'Велосипед не найден'}, status=status.HTTP_404_NOT_FOUND)


class ReturnBikeView(APIView):
    """View для возвращения велосипеда."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    print('Мы тут - ReturnBikeView !!!')

    def post(self, request, rental_id):
        """Method POST для возвращения велосипеда."""

        print(f'request - {request}')
        print(f'rental_id - {rental_id}')
        try:
            rental = Rental.objects.get(id=rental_id)
            if rental.user != request.user:
                return Response({'error': 'Вы не арендовали этот велосипед'}, status=status.HTTP_400_BAD_REQUEST)
            if rental.end_time:
                return Response({'error': 'Велосипед уже возвращен'}, status=status.HTTP_400_BAD_REQUEST)

            rental.end_time = timezone.now()
            # rental.cost = (rental.end_time - rental.start_time).total_seconds() / 3600 * rental.cost
            rental.calculate_cost()
            rental.save()
            send_return_notification.delay(rental.id)

            bike = rental.bike
            bike.status = Bike.STATUS_AVAILABLE
            bike.save()

            serializer = RentalSerializer(rental)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Rental.DoesNotExist:
            return Response({'error': 'Аренда не найдена'}, status=status.HTTP_404_NOT_FOUND)


class UpdateBikeStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def patch(self, request, bike_id):
        try:
            bike = Bike.objects.get(id=bike_id)
            status = request.data.get('status')

            if status not in [Bike.STATUS_AVAILABLE, Bike.STATUS_RENTED, Bike.STATUS_MAINTENANCE]:
                return Response({'error': 'Неверный статус'}, status=status.HTTP_400_BAD_REQUEST)

            bike.status = status
            bike.save()

            serializer = BikeSerializer(bike)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Bike.DoesNotExist:
            return Response({'error': 'Велосипед не найден'}, status=status.HTTP_404_NOT_FOUND)
