from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Todo


class TodoAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user and obtain an authentication token
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = self.client.post(reverse('api-token-auth'), {'username': 'testuser', 'password': 'testpass'}).data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        
        # Create a todo item associated with the test user
        self.todo = Todo.objects.create(title='Test Todo', description='Test Description', user=self.user)

    # Test case 1: Retrieve the list of todos for the authenticated user
    def test_get_todos(self):
        response = self.client.get(reverse('todo-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # Test case 2: Successfully create a new todo item
    def test_create_todo(self):
        data = {'title': 'New Todo', 'description': 'New Description'}
        response = self.client.post(reverse('todo-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    # Test case 3: Attempt to create a todo item with missing required fields (invalid request)
    def test_create_todo_invalid(self):
        data = {'description': 'Invalid Todo Item'} # Missing 'title' field
        response = self.client.post(reverse('todo-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # Test case 4: Retrieve a single todo item by its ID
    def test_get_single_todo(self):
        response = self.client.get(reverse('todo-detail', args=[self.todo.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # Test case 5: Attempt to retrieve a todo item that does not exist
    def test_get_nonexistent_todo(self):
        response = self.client.get(reverse('todo-detail', args=[1999])) # Nonexistent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # Test case 6: Successfully update an existing todo item
    def test_update_todo(self):
        data = {'title': 'Updated Todo', 'description': 'Updated Description', 'completed': True}
        response = self.client.put(reverse('todo-detail', args=[self.todo.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')
        
    # Test case 7: Attempt to update a todo item that does not exist
    def test_update_nonexistent_todo(self):
        data = {'title': 'Updated Todo'}
        response = self.client.put(reverse('todo-detail', args=[1999]), data) # Nonexistent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # Test case 8: Successfully delete an existing todo item
    def test_delete_todo(self):
        response = self.client.delete(reverse('todo-detail', args=[self.todo.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.count(), 0) # Ensure the todo item is deleted
        
    # Test case 9: Attempt to delete a todo item that does not exist
    def test_delete_nonexistent_todo(self):
        response = self.client.delete(reverse('todo-detail', args=[1999])) # id does not exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    # Test case 10: Attempt to access API endpoints without authentication
    def test_unauthorized_access(self):
        self.client.credentials() # Remove authentication token
        response = self.client.get(reverse('todo-list-create'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # Test case 11: Attempt to access API endpoints using an invalid authentication token
    def test_invalid_token_access(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken')
        response = self.client.get(reverse('todo-list-create'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    # Test case 12: Ensure a user cannot access another user's todo item
    def test_access_other_user_todo(self):
        user2 = User.objects.create_user(username='testuser2', password='testpass2')
        todo2 = Todo.objects.create(title='User2 Todo', description='User2 Description', user=user2)
        
        # testuser attempts to access a todo item owned by testuser2
        response = self.client.get(reverse('todo-detail', args=[todo2.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    # Test case 13: Ensure a user cannot update another user's todo item
    def test_update_other_user_todo(self):
        user2 = User.objects.create_user(username='testuser2', password='testpass2')
        todo2 = Todo.objects.create(title='User2 Todo', description='User 2 Description', user=user2)
        
        data = {'title': 'Invalid Update'}
        response = self.client.put(reverse('todo-detail', args=[todo2.id]), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # Test case 14: Ensure a user cannot delete another user's todo item
    def test_delete_other_user_todo(self):
        user2 = User.objects.create_user(username='testuser2', password='testpass2')
        todo2 = Todo.objects.create(title='User2 Todo', description='User2 Description', user=user2)
        
        response = self.client.delete(reverse('todo-detail', args=[todo2.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 