from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_statement, name='upload_statement'),  # Define a URL pattern for the root path
    path('upload/', views.upload_statement, name='upload'),
    path('query_transactions/', views.query_transactions, name='query_transactions'),
    path('tax/',views.tax,name='tax')
]




    # path('query/', views.query_transactions, name='query_transactions'),
