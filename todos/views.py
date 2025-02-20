from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Todo
from .serializers import TodoSerializer
from rest_framework import generics

class TodoListCreateView(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve all todos belonging to the authenticated user.
        """
        return Todo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new todo item for the authenticated user.
        """
        serializer.save(user=self.request.user)

class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single todo item.
    Requires authentication.
    """
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve todos belonging to the authenticated user.
        """
        return Todo.objects.filter(user=self.request.user)
    
    def get_object(self):
        """
        Retrieve a single todo item by ID that belongs to the authenticated user.
        """
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        return obj