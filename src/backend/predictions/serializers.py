"""
Serializers for predictions app
"""
from rest_framework import serializers
from mutations.serializers import MutationDataSerializer
from .models import PredictionResult, DiseaseProbability, MutationDistribution

class DiseaseProbabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for DiseaseProbability model
    """
    class Meta:
        model = DiseaseProbability
        fields = ['disease', 'confidence']

class MutationDistributionSerializer(serializers.ModelSerializer):
    """
    Serializer for MutationDistribution model
    """
    class Meta:
        model = MutationDistribution
        fields = ['type', 'count', 'percentage']

class PredictionResultSerializer(serializers.ModelSerializer):
    """
    Serializer for PredictionResult model
    """
    file_name = serializers.CharField(source='mutation_file.original_filename', read_only=True)
    upload_date = serializers.DateTimeField(source='mutation_file.upload_date', read_only=True)
    mutations_count = serializers.IntegerField(source='mutation_file.mutations_count', read_only=True)
    mutations = serializers.SerializerMethodField()
    disease_probabilities = DiseaseProbabilitySerializer(many=True, read_only=True)
    mutation_distribution = MutationDistributionSerializer(many=True, read_only=True)
    
    class Meta:
        model = PredictionResult
        fields = [
            'id', 'file_name', 'upload_date', 'predicted_disease', 
            'confidence_score', 'key_mutation', 'mutations_count',
            'mutations', 'disease_probabilities', 'mutation_distribution',
            'created_at', 'analysis_completed', 'analysis_error'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_mutations(self, obj):
        """
        Get top mutations from the associated file
        """
        # Return top 5 most significant mutations
        top_mutations = obj.mutation_file.mutations.filter(
            pathogenicity__in=['pathogenic', 'likely_pathogenic']
        )[:5]
        
        return MutationDataSerializer(top_mutations, many=True).data

class PredictionSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for prediction summary (for lists)
    """
    file_name = serializers.CharField(source='mutation_file.original_filename', read_only=True)
    upload_date = serializers.DateTimeField(source='mutation_file.upload_date', read_only=True)
    mutations_count = serializers.IntegerField(source='mutation_file.mutations_count', read_only=True)
    
    class Meta:
        model = PredictionResult
        fields = [
            'id', 'file_name', 'upload_date', 'predicted_disease', 
            'confidence_score', 'key_mutation', 'mutations_count',
            'created_at', 'analysis_completed'
        ]