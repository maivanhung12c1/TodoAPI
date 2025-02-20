from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from todos import views as todo_views

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('todos/', todo_views.TodoListCreateView.as_view(), name='todo-list-create'),
    path('todos/<int:pk>/', todo_views.TodoDetailView.as_view(), name='todo-detail'),
]