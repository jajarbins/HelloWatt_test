__author__ = 'xavier'
from django.conf.urls import url
from dashboard import views

urlpatterns = [
    url(r'^$', views.ClientFormView.as_view(), name='client-form'),
    url(r'^results/(?P<client_id>.+)$', views.results, name='results'),
]
