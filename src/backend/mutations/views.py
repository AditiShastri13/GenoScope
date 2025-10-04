"""
Views for mutations app
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging

from .models import MutationFile, MutationData
from .serializers import MutationFileSerializer, FileUploadSerializer, MutationDataSerializer
from .utils import process_mutation_file, get_mutation_preview

logger = logging.getLogger('genoscope')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_mutation_file(request):
    """
    Upload and process mutation CSV file
    POST /api/mutations/upload/
    """
    try:
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = serializer.validated_data['file']
        
        # Create MutationFile record
        mutation_file = MutationFile.objects.create(
            user=request.user,
            original_filename=uploaded_file.name,
            file=uploaded_file,
            file_size=uploaded_file.size
        )
        
        # Process the file
        success = process_mutation_file(mutation_file)
        
        if not success:
            return Response({
                'error': 'File processing failed',
                'details': mutation_file.processing_error
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get preview data
        preview_mutations = get_mutation_preview(mutation_file)
        preview_data = MutationDataSerializer(preview_mutations, many=True).data
        
        logger.info(f"File uploaded successfully by {request.user.email}: {uploaded_file.name}")
        
        return Response({
            'success': True,
            'file_id': str(mutation_file.id),
            'preview_data': preview_data,
            'mutations_count': mutation_file.mutations_count
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"File upload error for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'File upload failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_files(request):
    """
    Get all mutation files for the current user
    GET /api/mutations/files/
    """
    try:
        files = MutationFile.objects.filter(user=request.user)
        serializer = MutationFileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching files for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to fetch files'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_file_details(request, file_id):
    """
    Get detailed information about a specific file
    GET /api/mutations/files/{file_id}/
    """
    try:
        mutation_file = get_object_or_404(
            MutationFile, 
            id=file_id, 
            user=request.user
        )
        
        serializer = MutationFileSerializer(mutation_file)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching file details for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to fetch file details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_id):
    """
    Delete a mutation file
    DELETE /api/mutations/files/{file_id}/
    """
    try:
        mutation_file = get_object_or_404(
            MutationFile, 
            id=file_id, 
            user=request.user
        )
        
        filename = mutation_file.original_filename
        mutation_file.delete()
        
        logger.info(f"File deleted by {request.user.email}: {filename}")
        
        return Response({
            'message': 'File deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting file for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to delete file'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_file_mutations(request, file_id):
    """
    Get all mutations for a specific file with pagination
    GET /api/mutations/files/{file_id}/mutations/
    """
    try:
        mutation_file = get_object_or_404(
            MutationFile, 
            id=file_id, 
            user=request.user
        )
        
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 per page
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get mutations with pagination
        mutations = mutation_file.mutations.all()[offset:offset + page_size]
        total_count = mutation_file.mutations.count()
        
        serializer = MutationDataSerializer(mutations, many=True)
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching mutations for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to fetch mutations'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)