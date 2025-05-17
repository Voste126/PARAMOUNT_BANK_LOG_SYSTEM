from django.urls import path
from .views import ITIssueListCreateView, ITIssueRetrieveUpdateDestroyView

urlpatterns = [
    path('issues/', ITIssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<int:pk>/', ITIssueRetrieveUpdateDestroyView.as_view(), name='issue-detail'),
]
