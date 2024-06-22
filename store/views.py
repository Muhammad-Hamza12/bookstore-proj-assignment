from django.shortcuts import render,redirect
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework import viewsets
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .models import Book, Author, Category
from .serializers import BookSerializer, AuthorSerializer, CategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from store.tasks import send_email_task
from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenRefreshView


# Create your views here.
# api/views.py


# class UserRegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'success': 1,'message':'user registered'}, status=status.HTTP_201_CREATED)
    return JsonResponse({'success': 0,'message':'bad request'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        response = redirect('homepage')
        # response.set_cookie('refresh', str(refresh), httponly=True, secure=settings.SESSION_COOKIE_SECURE)
        response.set_cookie('refresh', str(refresh))
        # response.set_cookie('access', str(refresh.access_token), httponly=True, secure=settings.SESSION_COOKIE_SECURE)
        response.set_cookie('access', str(refresh.access_token))
        return response
    return JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout(request):
    response = redirect('login_view')
    response.delete_cookie('refresh')
    response.delete_cookie('access')
    return response

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # This will invoke the overridden update method in BookSerializer
        return Response({'success': True, 'message': 'Book updated successfully'}, status=status.HTTP_200_OK)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        # Perform login logic
        return login(request)
    return render(request, 'login.html')

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        # Perform registration logic
        return register(request)
    return render(request, 'register.html')

# @csrf_exempt
# def logout_view(request):
#     if request.method == 'POST':
#         return logout.as_view()(request)
#     return render(request, 'logout.html')

@csrf_exempt
def homepage_view(request):
    if request.COOKIES.get('access'):
        return render(request, 'homepage.html')
    return redirect('login_view')


def send_email_view(request):
    subject = 'Hello from Celery!'
    message = 'This is a test email sent asynchronously with Celery.'
    recipient_list = ['recipient@example.com']

    # Trigger the Celery task to send the email asynchronously
    send_email_task.delay(subject, message, recipient_list)

    return JsonResponse({'success': 1,'message':'email starting to send email'}, status=status.HTTP_200_OK)

