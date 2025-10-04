"""
Models for predictions app
"""
from django.db import models
from django.conf import settings
from mutations.models import MutationFile
import uuid

class PredictionResult(models.Model):
    """
    Model for ML prediction results
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='predictions')
    mutation_file = models.ForeignKey(MutationFile, on_delete=models.CASCADE, related_name='predictions')
    
    # Prediction results
    predicted_disease = models.CharField(max_length=200)
    confidence_score = models.FloatField()
    key_mutation = models.CharField(max_length=200)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    analysis_completed = models.BooleanField(default=False)
    analysis_error = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'predictions_result'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prediction for {self.mutation_file.original_filename} - {self.predicted_disease}"

class DiseaseProbability(models.Model):
    """
    Model for disease probability results
    """
    prediction = models.ForeignKey(PredictionResult, on_delete=models.CASCADE, related_name='disease_probabilities')
    disease = models.CharField(max_length=200)
    confidence = models.FloatField()
    
    class Meta:
        db_table = 'predictions_disease_probability'
        ordering = ['-confidence']
    
    def __str__(self):
        return f"{self.disease}: {self.confidence}%"

class MutationDistribution(models.Model):
    """
    Model for mutation type distribution
    """
    MUTATION_TYPES = [
        ('SNP', 'Single Nucleotide Polymorphism'),
        ('Indel', 'Insertion/Deletion'),
        ('Deletion', 'Deletion'),
        ('Insertion', 'Insertion'),
        ('CNV', 'Copy Number Variation'),
    ]
    
    prediction = models.ForeignKey(PredictionResult, on_delete=models.CASCADE, related_name='mutation_distribution')
    type = models.CharField(max_length=20, choices=MUTATION_TYPES)
    count = models.PositiveIntegerField()
    percentage = models.FloatField()
    
    class Meta:
        db_table = 'predictions_mutation_distribution'
        ordering = ['-percentage']
    
    def __str__(self):
        return f"{self.type}: {self.count} ({self.percentage}%)"