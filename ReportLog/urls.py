from django.urls import path
from .views import ITIssueCreateView, ITIssuePatchView, ITIssueDeleteView

urlpatterns = [
    path('issues/', ITIssueCreateView.as_view(), name='issue-create'),
    path('issues/<int:pk>/', ITIssuePatchView.as_view(), name='issue-patch'),
    path('issues/<int:pk>/delete/', ITIssueDeleteView.as_view(), name='issue-delete'),
]
