from django.urls import re_path, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login.as_view(), name='login'),
    path('publish/', views.publish_message, name='publish'),
    path('get-all-topics/', views.get_all_topics, name='get-all-topics'),
    re_path(r'^data/(?P<topic>.+)/(?P<qos>.+)/(?P<content_hex>.+)/$', views.show_data),
]