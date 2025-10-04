"""
Serializers for mutations app
"""
from rest_framework import serializers
from .models import MutationFile, MutationData

class MutationDataSerializer(serializers.ModelSerializer):
    """
    Serializer for MutationData model
    """
    class Meta:
        model = MutationData
        fields = ['gene', 'mutation', 'consequence', 'pathogenicity', 'notes']

class MutationFileSerializer(serializers.ModelSerializer):
    """
    Serializer for MutationFile model
    """
    mutations = MutationDataSerializer(many=True, read_only=True)
    
    class Meta:
        model = MutationFile
        fields = [
            'id', 'original_filename', 'file_size', 'mutations_count',
            'upload_date', 'processed', 'processing_error', 'mutations'
        ]
        read_only_fields = ['id', 'file_size', 'mutations_count', 'upload_date', 'processed']

class FileUploadSerializer(serializers.Serializer):
    """
    Serializer for file upload
    """
    file = serializers.FileField()
    
    def validate_file(self, value):
        """
        Validate uploaded file
        """
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed")
        
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        return value