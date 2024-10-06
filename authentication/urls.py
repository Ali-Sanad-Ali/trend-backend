from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairSerializer, DisplayList, DisplayDetail, PasswordResetRequestView, VerifyOtpCodeView, SetNewPasswordView, UserRegisterView, BlockCreateView, BlockListView, UnblockUserView

urlpatterns = [
    path('login/', MyTokenObtainPairSerializer.as_view(), name='login'),
    path('token_refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegisterView.as_view(), name='register'),
    # reset-password endpoints 
    path('PasswordResetRequest/', PasswordResetRequestView.as_view(), name='PasswordResetRequest'),
    path('VerifyOtp/', VerifyOtpCodeView.as_view(), name='VerifyOtp'),
    path('SetNewPasswordView/', SetNewPasswordView.as_view(), name='SetNewPasswordView'),
    # path('users/', DisplayList.as_view(), name='users'), 
    # path('users/<int:pk>/', DisplayDetail.as_view(), name='users'),


    # URL pattern for listing all block relationships or creating a new block relationship
    path('blocks/', BlockCreateView.as_view(), name='block-list-create'),
    path('block-list/', BlockListView.as_view(), name='block-list'),
    # URL pattern for retrieving or deleting a specific block relationship
    path('unblockuser/<int:blocked_id>/', UnblockUserView.as_view(), name='unblockuser'), 

]