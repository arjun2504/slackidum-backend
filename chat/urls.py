from django.urls import include, path, re_path
from django.conf.urls import url
from .views import CustomObtainAuthToken
from . import views

urlpatterns = [
    path('auth/', CustomObtainAuthToken.as_view()),
    path('user/', views.UserViewSet.as_view({ 'get': 'list', 'post': 'create'})),
    path('user/<int:pk>/', views.UserViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='destroy_user'),
    path('username/check/', views.UserExistsView.as_view(), name='users'),

    path('group/', views.GroupViewSet.as_view({ 'get': 'list', 'post': 'create'})),
    path('group/create/', views.GroupViewSet.as_view({ 'post': 'create'})),
    path('group/<int:group_id>/add-user/', views.GroupViewSet.as_view({ 'post': 'add_to_group'})),

    path('current-user/', views.CurrentUserDetails.as_view()),
    path('add-contact/', views.ContactBookViewSet.as_view({'post': 'create'})),
    path('user-detail/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('get-convo/', views.ConversationView.as_view()),


    re_path(r'^chat/$', views.index, name='index'),
    re_path(r'^chat/(?P<room_name>[^/]+)/$', views.room, name='room')
]