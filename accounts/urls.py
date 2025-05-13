from django.urls import path
from .views import LoginUserView, RegisterUserView, UserProfileView, BusinessProfileView, CustomerProfileView

urlpatterns = [
    path('registration/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
    path('profiles/business/', BusinessProfileView.as_view(), name='business-profile-list'),
    path('profiles/customer/', CustomerProfileView.as_view(), name='customer-profile-list'),
]
