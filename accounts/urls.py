from django.urls import path
from .views import LoginUserView, RegisterUserView, UserProfileView

urlpatterns = [
    path('registration/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
    
    
]
