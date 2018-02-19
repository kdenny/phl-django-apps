from django.conf.urls import url

from maestro import views

urlpatterns = [
    url(r'^events/', views.Events.as_view()), 
    url(r'^test_query/', views.NLPQueryTest.as_view()), 
]