from django.urls import path
from . import views


urlpatterns=[
    path('view_profile',views.view_profile, name='viewprofile'),
    path('add_profile',views.add_profile, name='addprofile'),
    path('edit_profile/<int:id>/',views.edit_profile, name='editprofile'),
    path('dele_profile',views.delete_profile, name='deleteprofile'),





    ]