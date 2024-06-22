from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet, CategoryViewSet,register, login, logout,register_view,login_view,homepage_view,send_email_task

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    # for registering a user
    path('auth/register/', register_view, name='register_view'),
    #for login into bookstore
    path('auth/login/', login_view, name='login_view'),
    #for homepage where books , authors , shoppingcart are there
    path('homepage/', homepage_view, name='homepage'),
    # for sending email to user on purchase button click using celery
    path('email/', send_email_task, name='send_email_task'),
]+ router.urls