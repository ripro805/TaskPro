from django.urls import path

from users.views import admin_dashboard, assign_role, create_group, group_list, sign_in, sign_up, activate_account, CustomLoginView, ProfileView, CustomLogoutView, CustomPasswordChangeView, CustomPasswordChangeDoneView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, EditProfileView

urlpatterns = [
    path('sign-up/', sign_up, name='sign_up'),
    # path('sign-in/', sign_in, name='sign_in'),
     path('sign-in/', CustomLoginView.as_view(), name='sign_in'),
    path('sign-out/', CustomLogoutView.as_view(), name='sign_out'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('assign-role/<int:user_id>/', assign_role, name='assign_role'),
    path('admin/create-group/', create_group, name='create_group'),
    path('admin/group-list/', group_list, name='group_list'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
