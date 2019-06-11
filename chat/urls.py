from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^users/', views.UserViewSet.as_view({'get': 'list'}), name='users'),
    url(r'^username/check/', views.UserExistsView.as_view(), name='users')
]