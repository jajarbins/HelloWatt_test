"""joole URL Configuration

The `urlpatterns` list routes URLs to viewsBuilder. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function viewsBuilder
    1. Add an import:  from my_app import viewsBuilder
    2. Add a URL to urlpatterns:  url(r'^$', viewsBuilder.home, name='home')
Class-based viewsBuilder
    1. Add an import:  from other_app.viewsBuilder import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'', include('dashboard.urls', namespace="dashboard")),
    url(r'^admin/', admin.site.urls),
]

