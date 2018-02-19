from django.conf.urls import url

from nimbus import views

urlpatterns = [
    url(r'^sheets/(?P<sheet_id>[\w\-]+)/(?P<sheet_name>[\w\-]+)/$', views.GoogleSheetDataView.as_view()),
    url(r'^sheets/(?P<sheet_id>[\w\-]+)/$', views.GoogleSheetDataView.as_view())
]