from django.urls import path

from . import views

urlpatterns = [
    path('', views.view_profile, name="view_profile"),
    path('edit', views.edit_profile, name="edit_profile"),
    path('create_profile', views.edit_profile, name="create_profile"),
    path('profile_settings', views.profile_settings, name="profile_settings"),
    path('delete_profile', views.delete_profile, name="delete_profile"),
    path('edit_email', views.edit_email, name="edit_email"),
    path('verify_email', views.verify_email, name="verify_email"),
]
