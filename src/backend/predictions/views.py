"""
Views for predictions app
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from mutations.models import MutationFile
import logging

from .models import PredictionResult, DiseaseProbability, MutationDistribution
from .serializers import PredictionResultSerializer, PredictionSummarySerializer
from .ml_engine import ml_engine

logger = logging.getLogger('genoscope')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_mutations(request):
    """
    Run ML analysis on uploaded mutation file
    POST /api/predictions/analyze/
    """
    try:
        file_id = request.data.get('file_id')
        if not file_id:
            return Response({
                'error': 'file_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the mutation file
        mutation_file = get_object_or_404(
            MutationFile,
            id=file_id,
            user=request.user,
            processed=True
        )
        
        # Check if prediction already exists
        existing_prediction = PredictionResult.objects.filter(
            mutation_file=mutation_file,
            user=request.user
        ).first()
        
        if existing_prediction:
            serializer = PredictionResultSerializer(existing_prediction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create prediction record
        prediction = PredictionResult.objects.create(
            user=request.user,
            mutation_file=mutation_file,
            predicted_disease='Analyzing...',
            confidence_score=0.0,
            key_mutation='Processing...'
        )
        
        try:
            # Run ML analysis
            analysis_results = ml_engine.analyze_mutations(mutation_file)
            
            # Update prediction with results
            prediction.predicted_disease = analysis_results['predicted_disease']
            prediction.confidence_score = analysis_results['confidence_score']
            prediction.key_mutation = analysis_results['key_mutation']
            prediction.analysis_completed = True
            prediction.save()
            
            # Create disease probabilities
            for prob_data in analysis_results['disease_probabilities']:
                DiseaseProbability.objects.create(
                    prediction=prediction,
                    disease=prob_data['disease'],
                    confidence=prob_data['confidence']
                )
            
            # Create mutation distribution
            for dist_data in analysis_results['mutation_distribution']:
                MutationDistribution.objects.create(
                    prediction=prediction,
                    type=dist_data['type'],
                    count=dist_data['count'],
                    percentage=dist_data['percentage']
                )
            
            logger.info(f"ML analysis completed for user {request.user.email}, file {mutation_file.id}")
            
            # Return complete prediction result
            serializer = PredictionResultSerializer(prediction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Update prediction with error
            prediction.analysis_error = str(e)
            prediction.save()
            
            logger.error(f"ML analysis failed for user {request.user.email}: {str(e)}")
            return Response({
                'error': 'Analysis failed. Please try again.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Prediction request error for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to start analysis'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prediction_history(request):
    """
    Get prediction history for the current user
    GET /api/predictions/history/
    """
    try:
        predictions = PredictionResult.objects.filter(
            user=request.user,
            analysis_completed=True
        ).select_related('mutation_file')
        
        serializer = PredictionSummarySerializer(predictions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching prediction history for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to fetch prediction history'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prediction_details(request, prediction_id):
    """
    Get detailed information about a specific prediction
    GET /api/predictions/{prediction_id}/
    """
    try:
        prediction = get_object_or_404(
            PredictionResult,
            id=prediction_id,
            user=request.user,
            analysis_completed=True
        )
        
        serializer = PredictionResultSerializer(prediction)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching prediction details for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to fetch prediction details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_prediction(request, prediction_id):
    """
    Delete a prediction result
    DELETE /api/predictions/{prediction_id}/
    """
    try:
        prediction = get_object_or_404(
            PredictionResult,
            id=prediction_id,
            user=request.user
        )
        
        filename = prediction.mutation_file.original_filename
        prediction.delete()
        
        logger.info(f"Prediction deleted by {request.user.email}: {filename}")
        
        return Response({
            'message': 'Prediction deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting prediction for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to delete prediction'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """
    Get dashboard statistics for the current user
    GET /api/predictions/dashboard/stats/
    """
    try:
        user_files = MutationFile.objects.filter(user=request.user)
        user_predictions = PredictionResult.objects.filter(user=request.user, analysis_completed=True)
        
        # Calculate statistics
        total_files = user_files.count()
        total_predictions = user_predictions.count()
        total_mutations = sum(f.mutations_count for f in user_files)
        
        # Recent activity
        recent_predictions = user_predictions.order_by('-created_at')[:5]
        recent_activity = []
        
        for prediction in recent_predictions:
            recent_activity.append({
                'id': str(prediction.id),
                'file_name': prediction.mutation_file.original_filename,
                'predicted_disease': prediction.predicted_disease,
                'confidence_score': prediction.confidence_score,
                'created_at': prediction.created_at.isoformat()
            })
        
        # Disease distribution
        disease_counts = {}
        for prediction in user_predictions:
            disease = prediction.predicted_disease
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        return Response({
            'total_files_uploaded': total_files,
            'total_predictions': total_predictions,
            'total_mutations_analyzed': total_mutations,
            'recent_activity': recent_activity,
            'disease_distribution': disease_counts
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to fetch dashboard statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)