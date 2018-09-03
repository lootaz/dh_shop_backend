from django.contrib.auth.models import User
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView

from .models import Shop, Schedule, TimeRange
from .permissions import IsOwnerOrReadOnly, IsScheduleOwnerOrReadOnly, IsTimeRangeOwnerOrReadOnly
from .serializers import ShopSerializer, ScheduleSerializer, TimeRangeSerializer, UserSerializer, ShopListSerializer


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({'error': 'Please provide both username and pasword'},
                        status=HTTP_400_BAD_REQUEST)
    if (User.objects.filter(username=username).exists()):
        return Response({'error': f'User with name \'{username}\' already exists'},
                        status=HTTP_400_BAD_REQUEST)
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()

    return Response(status=HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=request.user)
    user = {
        'id': request.user.id,
        'username': request.user.username
    }
    return Response({'user': user, 'token': token.key}, status=HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny,))
@authentication_classes([])
def logout(request):
    if request.user.is_authenticated:
        request.user.auth_token.delete()
    return Response(status=HTTP_200_OK)


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    list_serializer_class = ShopListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            if hasattr(self, 'list_serializer_class'):
                return self.list_serializer_class
        return super().get_serializer_class()


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsScheduleOwnerOrReadOnly)


class TimeRangeViewSet(viewsets.ModelViewSet):
    queryset = TimeRange.objects.all()
    serializer_class = TimeRangeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTimeRangeOwnerOrReadOnly)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            raise Http404


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.initial_data['password']
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
