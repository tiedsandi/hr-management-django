from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('v1/', include(('api.v1.urls', 'v1'), namespace='v1')),
    path('v2/', include(('api.v2.urls', 'v2'), namespace='v2')),
]
