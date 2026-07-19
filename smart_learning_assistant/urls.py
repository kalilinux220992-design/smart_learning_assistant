"""
URL configuration for smart_learning_assistant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from .views import attendance_page, clear_today_watch_stats, favicon, home, watch_stats_api, watch_stats_page, watch_stats_reset_token

urlpatterns = [
    path('', home, name='home'),
    path('watch-stats/', watch_stats_page, name='watch_stats_page'),
    path('watch-stats/clear-today/', clear_today_watch_stats, name='clear_today_watch_stats'),
    path('attendance/', attendance_page, name='attendance_page'),
    path('api/watch-stats/', watch_stats_api, name='watch_stats_api'),
    path('api/watch-stats/reset-token/', watch_stats_reset_token, name='watch_stats_reset_token'),
    path('favicon.ico', favicon),
    path('', include('converter.urls')),
    path('placement/', include(('predictor.urls', 'predictor'), namespace='predictor')),
    path('admin/', admin.site.urls),
]
