from django.urls import path
from your_app_name.views import ItemListCreate,ItemRetrieveUpdateDestroy, home

urlpatterns = [
    path('items/', ItemListCreate.as_view(), name='item-list-create'),
    path('', home, name='home'),
    path('items/<int:pk>/', ItemRetrieveUpdateDestroy.as_view(), name='item-detail'),
]