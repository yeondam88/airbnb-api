import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rooms.models import Room
from rooms.serializers import RoomSerializer
from .models import User
from .serializers import UserSerializer
from .permissions import IsSelf


class UsersView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            return Response(UserSerializer(new_user).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response()


@api_view(['GET'])
def user_detail(request, pk):

    try:
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


class FavsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = RoomSerializer(user.favs.all(), many=True).data
        return Response(serializer)

    def put(self, request):
        pk = request.data.get('pk', None)
        user = request.user
        if pk is not None:
            try:
                room = Room.objects.get(pk=pk)
                if room in user.favs.all():
                    user.favs.remove(room)
                else:
                    user.favs.add(room)
                return Response()
            except Room.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)

    if user is not None:
        encode_jwt = jwt.encode(
            {'pk': user.id}, settings.SECRET_KEY, algorithm="HS256")
        return Response(data={'token': encode_jwt})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
