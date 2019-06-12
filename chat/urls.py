from django.urls import include, path
from rest_framework.authtoken import views as tokenview
from . import views

urlpatterns = [
    path('auth/', tokenview.obtain_auth_token),
    path('user/', views.UserViewSet.as_view({ 'get': 'list', 'post': 'create'})),
    path('user/<int:pk>/', views.UserViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='destroy_user'),
    path('username/check/', views.UserExistsView.as_view(), name='users'),
    path('group/', views.GroupViewSet.as_view({ 'get': 'list', 'post': 'create'})),
    path('group/create/', views.GroupViewSet.as_view({ 'post': 'create'})),
    path('group/<int:group_id>/add-user/', views.GroupViewSet.as_view({ 'post': 'add_to_group'}))
]