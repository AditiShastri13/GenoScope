"""
Views for reports app
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

from predictions.models import PredictionResult
from .models import SharedReport
from .pdf_generator import pdf_generator

logger = logging.getLogger('genoscope')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request, prediction_id):
    """
    Generate PDF report for a prediction
    GET /api/reports/pdf/{prediction_id}/
    """
    try:
        prediction = get_object_or_404(
            PredictionResult,
            id=prediction_id,
            user=request.user,
            analysis_completed=True
        )
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_report(prediction)
        
        # Create HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="genoscope_report_{prediction_id[:8]}.pdf"'
        response.write(pdf_buffer.read())
        
        logger.info(f"PDF report generated for user {request.user.email}, prediction {prediction_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"PDF generation error for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to generate PDF report'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_report(request):
    """
    Share a report via email
    POST /api/reports/share/
    """
    try:
        prediction_id = request.data.get('prediction_id')
        email = request.data.get('email')
        
        if not prediction_id or not email:
            return Response({
                'error': 'prediction_id and email are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        prediction = get_object_or_404(
            PredictionResult,
            id=prediction_id,
            user=request.user,
            analysis_completed=True
        )
        
        # Create shared report record
        expires_at = datetime.now() + timedelta(days=7)  # Expires in 7 days
        shared_report = SharedReport.objects.create(
            prediction=prediction,
            shared_by=request.user,
            shared_with_email=email,
            expires_at=expires_at
        )
        
        # Create share link
        share_link = f"{request.build_absolute_uri('/')[:-1]}/api/reports/shared/{shared_report.share_token}/"
        
        # Send email (in production, use a proper email template)
        try:
            subject = f"GenoScope Genetic Analysis Report - {prediction.predicted_disease}"
            message = f"""
Hello,

{request.user.name} has shared a GenoScope genetic analysis report with you.

Report Details:
- File: {prediction.mutation_file.original_filename}
- Analysis Date: {prediction.created_at.strftime('%B %d, %Y')}
- Primary Prediction: {prediction.predicted_disease}

You can access the report using this secure link:
{share_link}

This link will expire on {expires_at.strftime('%B %d, %Y')}.

Best regards,
GenoScope Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            logger.info(f"Report shared by {request.user.email} with {email}")
            
            return Response({
                'success': True,
                'message': f'Report shared successfully with {email}',
                'share_link': share_link,
                'expires_at': expires_at
            }, status=status.HTTP_200_OK)
            
        except Exception as email_error:
            logger.error(f"Email sending failed: {str(email_error)}")
            return Response({
                'success': True,
                'message': 'Report sharing link created, but email delivery failed',
                'share_link': share_link,
                'expires_at': expires_at
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Report sharing error for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to share report'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def view_shared_report(request, share_token):
    """
    View a shared report using share token
    GET /api/reports/shared/{share_token}/
    """
    try:
        shared_report = get_object_or_404(
            SharedReport,
            share_token=share_token,
            is_active=True,
            expires_at__gt=datetime.now()
        )
        
        # Increment access count
        shared_report.access_count += 1
        shared_report.save()
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_report(shared_report.prediction)
        
        # Create HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="shared_genoscope_report.pdf"'
        response.write(pdf_buffer.read())
        
        logger.info(f"Shared report accessed with token {share_token}")
        
        return response
        
    except Exception as e:
        logger.error(f"Shared report access error: {str(e)}")
        return Response({
            'error': 'Report not found or expired'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shared_reports(request):
    """
    Get list of reports shared by the current user
    GET /api/reports/shared/
    """
    try:
        shared_reports = SharedReport.objects.filter(
            shared_by=request.user
        ).select_related('prediction', 'prediction__mutation_file')
        
        results = []
        for report in shared_reports:
            results.append({
                'id': str(report.id),
                'prediction_id': str(report.prediction.id),
                'file_name': report.prediction.mutation_file.original_filename,
                'predicted_disease': report.prediction.predicted_disease,
                'shared_with_email': report.shared_with_email,
                'created_at': report.created_at,
                'expires_at': report.expires_at,
                'is_active': report.is_active and report.expires_at > datetime.now(),
                'access_count': report.access_count
            })
        
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching shared reports for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to fetch shared reports'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_shared_report(request, share_id):
    """
    Revoke access to a shared report
    DELETE /api/reports/shared/{share_id}/
    """
    try:
        shared_report = get_object_or_404(
            SharedReport,
            id=share_id,
            shared_by=request.user
        )
        
        shared_report.is_active = False
        shared_report.save()
        
        logger.info(f"Shared report revoked by {request.user.email}: {share_id}")
        
        return Response({
            'message': 'Shared report access revoked successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error revoking shared report for user {request.user.email}: {str(e)}")
        return Response({
            'error': 'Failed to revoke shared report'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)