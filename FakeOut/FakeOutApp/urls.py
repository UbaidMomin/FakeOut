from django.urls import path
from . import views

app_name = 'FakeOutApp'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help_view, name='help'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('report/', views.report_view, name='report'),
    path('api/analyze/', views.analyze_api, name='analyze_api'),
]