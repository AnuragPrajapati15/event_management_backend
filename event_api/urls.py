from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from event_api.views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('setup-profile/', SetupProfileView.as_view(), name='setup-profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('events/', EventAPIView.as_view(), name='events'),
    path('events/<int:id>/purchase/', TicketPurchaseAPIView.as_view(), name='ticket-purchase'),

]
