"""
PDF report generation utilities
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
import logging
from datetime import datetime

logger = logging.getLogger('genoscope')

class GenoScopeReportGenerator:
    """
    PDF report generator for GenoScope genetic analysis results
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """
        Create custom paragraph styles
        """
        styles = {}
        
        # Title style
        styles['CustomTitle'] = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.Color(0.169, 0.298, 0.494),  # #2B4C7E
            alignment=1  # Center
        )
        
        # Heading style
        styles['CustomHeading'] = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.Color(0.424, 0.388, 1.0),  # #6C63FF
        )
        
        # Body style
        styles['CustomBody'] = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14
        )
        
        return styles
    
    def generate_report(self, prediction_result) -> BytesIO:
        """
        Generate PDF report for prediction result
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build report content
            story = []
            
            # Header
            story.extend(self._create_header(prediction_result))
            
            # Summary
            story.extend(self._create_summary(prediction_result))
            
            # Disease Probabilities
            story.extend(self._create_disease_probabilities(prediction_result))
            
            # Key Mutations
            story.extend(self._create_key_mutations(prediction_result))
            
            # Mutation Distribution
            story.extend(self._create_mutation_distribution(prediction_result))
            
            # Recommendations
            story.extend(self._create_recommendations(prediction_result))
            
            # Footer
            story.extend(self._create_footer())
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info(f"PDF report generated for prediction {prediction_result.id}")
            return buffer
            
        except Exception as e:
            logger.error(f"PDF generation error for prediction {prediction_result.id}: {str(e)}")
            raise
    
    def _create_header(self, prediction_result):
        """
        Create report header
        """
        story = []
        
        # Title
        title = Paragraph("GenoScope Genetic Analysis Report", self.custom_styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Patient/File info
        info_data = [
            ['File Name:', prediction_result.mutation_file.original_filename],
            ['Upload Date:', prediction_result.mutation_file.upload_date.strftime('%B %d, %Y')],
            ['Analysis Date:', prediction_result.created_at.strftime('%B %d, %Y')],
            ['Report ID:', str(prediction_result.id)[:8]],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_summary(self, prediction_result):
        """
        Create analysis summary
        """
        story = []
        
        story.append(Paragraph("Analysis Summary", self.custom_styles['CustomHeading']))
        
        # Key findings
        summary_text = f"""
        <b>Primary Disease Prediction:</b> {prediction_result.predicted_disease}<br/>
        <b>Confidence Score:</b> {prediction_result.confidence_score}%<br/>
        <b>Key Mutation:</b> {prediction_result.key_mutation}<br/>
        <b>Total Mutations Analyzed:</b> {prediction_result.mutation_file.mutations_count}
        """
        
        story.append(Paragraph(summary_text, self.custom_styles['CustomBody']))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_disease_probabilities(self, prediction_result):
        """
        Create disease probabilities section
        """
        story = []
        
        story.append(Paragraph("Disease Risk Probabilities", self.custom_styles['CustomHeading']))
        
        # Create table
        prob_data = [['Disease', 'Confidence (%)']]
        for prob in prediction_result.disease_probabilities.all()[:5]:
            prob_data.append([prob.disease, f"{prob.confidence}%"])
        
        prob_table = Table(prob_data, colWidths=[4*inch, 2*inch])
        prob_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.169, 0.298, 0.494)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.965, 0.969, 0.988)]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(prob_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_key_mutations(self, prediction_result):
        """
        Create key mutations section
        """
        story = []
        
        story.append(Paragraph("Key Pathogenic Mutations", self.custom_styles['CustomHeading']))
        
        # Get pathogenic mutations
        pathogenic_mutations = prediction_result.mutation_file.mutations.filter(
            pathogenicity__in=['pathogenic', 'likely_pathogenic']
        )[:10]
        
        if pathogenic_mutations.exists():
            mut_data = [['Gene', 'Mutation', 'Consequence', 'Pathogenicity']]
            for mut in pathogenic_mutations:
                mut_data.append([
                    mut.gene,
                    mut.mutation,
                    mut.get_consequence_display(),
                    mut.get_pathogenicity_display()
                ])
            
            mut_table = Table(mut_data, colWidths=[1.2*inch, 2*inch, 1.5*inch, 1.3*inch])
            mut_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.424, 0.388, 1.0)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.965, 0.969, 0.988)]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(mut_table)
        else:
            story.append(Paragraph("No pathogenic mutations identified.", self.custom_styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_mutation_distribution(self, prediction_result):
        """
        Create mutation distribution section
        """
        story = []
        
        story.append(Paragraph("Mutation Type Distribution", self.custom_styles['CustomHeading']))
        
        # Create distribution table
        dist_data = [['Mutation Type', 'Count', 'Percentage']]
        for dist in prediction_result.mutation_distribution.all():
            dist_data.append([dist.type, str(dist.count), f"{dist.percentage}%"])
        
        dist_table = Table(dist_data, colWidths=[2*inch, 2*inch, 2*inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.169, 0.298, 0.494)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.965, 0.969, 0.988)]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(dist_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_recommendations(self, prediction_result):
        """
        Create recommendations section
        """
        story = []
        
        story.append(Paragraph("Clinical Recommendations", self.custom_styles['CustomHeading']))
        
        recommendations = [
            "Consult with a genetic counselor to discuss these results",
            "Consider additional genetic testing if recommended by your healthcare provider",
            "Discuss family history and screening recommendations with your physician",
            "Consider lifestyle modifications based on identified risk factors"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.custom_styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_footer(self):
        """
        Create report footer
        """
        story = []
        
        story.append(PageBreak())
        
        disclaimer = """
        <b>IMPORTANT DISCLAIMER:</b><br/>
        This report is for research and educational purposes only. 
        The results should not be used for clinical decision-making without consultation 
        with qualified healthcare professionals. GenoScope analysis is based on computational 
        predictions and should be validated through appropriate clinical testing.
        """
        
        story.append(Paragraph(disclaimer, self.custom_styles['CustomBody']))
        
        footer_text = f"Generated by GenoScope on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Spacer(1, 20))
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        return story

# Global PDF generator instance
pdf_generator = GenoScopeReportGenerator()