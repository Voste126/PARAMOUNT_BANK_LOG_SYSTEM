from django.urls import path
from .views import ITIssueListCreateView, ITIssueRetrieveUpdateDestroyView, CategoryChoicesView, StaffUpdateIssueView

urlpatterns = [
    path('issues/', ITIssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<int:pk>/', ITIssueRetrieveUpdateDestroyView.as_view(), name='issue-detail'),
    path('categories/', CategoryChoicesView.as_view(), name='category-choices'),
    path('issues/<int:pk>/update/', StaffUpdateIssueView.as_view(), name='staff-update-issue'),
]
