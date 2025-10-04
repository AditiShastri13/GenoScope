"""
Models for mutations app
"""
from django.db import models
from django.conf import settings
import uuid

class MutationFile(models.Model):
    """
    Model for uploaded mutation files
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mutation_files')
    original_filename = models.CharField(max_length=500)
    file = models.FileField(upload_to='mutations/')
    file_size = models.PositiveIntegerField()
    mutations_count = models.PositiveIntegerField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'mutations_file'
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.original_filename} by {self.user.name}"

class MutationData(models.Model):
    """
    Model for individual mutation data entries
    """
    PATHOGENICITY_CHOICES = [
        ('pathogenic', 'Pathogenic'),
        ('likely_pathogenic', 'Likely Pathogenic'),
        ('vus', 'VUS'),
        ('likely_benign', 'Likely Benign'),
        ('benign', 'Benign'),
    ]
    
    CONSEQUENCE_CHOICES = [
        ('missense', 'Missense'),
        ('nonsense', 'Nonsense'),
        ('frameshift', 'Frameshift'),
        ('splice_site', 'Splice Site'),
        ('synonymous', 'Synonymous'),
        ('inframe_indel', 'In-frame Indel'),
    ]
    
    file = models.ForeignKey(MutationFile, on_delete=models.CASCADE, related_name='mutations')
    gene = models.CharField(max_length=50)
    mutation = models.CharField(max_length=200)
    consequence = models.CharField(max_length=50, choices=CONSEQUENCE_CHOICES)
    pathogenicity = models.CharField(max_length=50, choices=PATHOGENICITY_CHOICES)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mutations_data'
        ordering = ['gene', 'mutation']
    
    def __str__(self):
        return f"{self.gene} {self.mutation}"