"""
Models for reports app
"""
from django.db import models
from django.conf import settings
from predictions.models import PredictionResult
import uuid

class SharedReport(models.Model):
    """
    Model for shared reports
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction = models.ForeignKey(PredictionResult, on_delete=models.CASCADE, related_name='shared_reports')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shared_with_email = models.EmailField()
    share_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    access_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'reports_shared_report'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report shared with {self.shared_with_email}"