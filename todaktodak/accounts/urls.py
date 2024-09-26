from django.urls import path,include
from .views import (
    RegisterStepOne, RegisterStepTwo, CustomAuthToken, TokenRefreshView,
    TokenVerifyView, LogoutView, ProfileUpdateView, GetUserIdFromTokenView,GetUserInfoFromTokenView,ProfileImageUpdateView,
    google_login, google_callback
)
urlpatterns = [
    path('register/step1/', RegisterStepOne.as_view(), name='register_step_one'),
    path('register/step2/', RegisterStepTwo.as_view(), name='register_step_two'),
    # path('login/', CustomAuthToken.as_view(), name='login'),
    path('login/', CustomAuthToken.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('api/update-profile-image/', ProfileImageUpdateView.as_view(), name='update-profile-image'),
    path('api/get-user-id-from-token/', GetUserIdFromTokenView.as_view(), name='get_user_id_from_token'),
    path('api/get-user-info-from-token/', GetUserInfoFromTokenView.as_view(), name='get_user_info_from_token'),
    path("account/", include("allauth.urls")),
    path("google/login/", google_login, name="google_login"),
    path("google/callback/", google_callback, name="google_callback"),
]

