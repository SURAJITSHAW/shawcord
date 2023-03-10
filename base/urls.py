from django.urls import path
from . import views

urlpatterns = [
    # Login route
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    
    path('register/', views.registerPage, name='register'),

    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),

    # CRUD routes
    path('create-room/', views.create_room, name='create-room'),
    path('update-room/<str:pk>', views.update_room, name='update-room'),
    path('delete-room/<str:pk>', views.delete_room, name='delete-room'),

    # Delete message
    path('delete-message/<str:pk>', views.delete_message, name='delete-message'),

    # user profile
    path('profile/<str:pk>', views.UserProfile, name='userProfile'),

    # edit user profile
    path('edit-user/', views.UserEdit, name='userEdit'),

    # mobile / topics 
    path('topics/', views.topics, name='topics'),
    # mobile / activity 
    path('activity/', views.activity, name='activity'),
]
