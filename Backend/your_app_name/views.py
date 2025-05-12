from rest_framework import generics
from .models import Item
from .serializers import ItemSerializer
from django.http import HttpResponse
from django.shortcuts import render
from .supabase_config import supabase 

class ItemListCreate(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

def home(request):
    return render(request, 'your_app_name/home.html')

def get_items(request):
    data = supabase.table("items").select("*").execute()
    return HttpResponse(data)

