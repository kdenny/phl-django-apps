from django.conf.urls import url

from etl import views

urlpatterns = [
    url(r'^geo/by_city/$', views.MappingByCity.as_view()),
    url(r'^sheets/export/$', views.GoogleSheetsExport.as_view()),
]