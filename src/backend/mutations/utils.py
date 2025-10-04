"""
Utility functions for mutations processing
"""
import pandas as pd
import logging
from io import StringIO
from .models import MutationFile, MutationData

logger = logging.getLogger('genoscope')

def process_mutation_file(mutation_file: MutationFile):
    """
    Process uploaded CSV file and extract mutation data
    """
    try:
        # Read CSV file
        df = pd.read_csv(mutation_file.file.path)
        
        # Validate required columns
        required_columns = ['gene', 'mutation', 'consequence', 'pathogenicity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns: {', '.join(missing_columns)}"
            mutation_file.processing_error = error_msg
            mutation_file.save()
            logger.error(f"CSV processing error for {mutation_file.id}: {error_msg}")
            return False
        
        # Clean and process data
        df = df.dropna(subset=required_columns)
        df['gene'] = df['gene'].astype(str).str.upper().str.strip()
        df['mutation'] = df['mutation'].astype(str).str.strip()
        df['consequence'] = df['consequence'].astype(str).str.lower().str.strip()
        df['pathogenicity'] = df['pathogenicity'].astype(str).str.lower().str.strip()
        
        # Map pathogenicity values
        pathogenicity_mapping = {
            'pathogenic': 'pathogenic',
            'likely pathogenic': 'likely_pathogenic',
            'likely_pathogenic': 'likely_pathogenic',
            'vus': 'vus',
            'uncertain significance': 'vus',
            'likely benign': 'likely_benign',
            'likely_benign': 'likely_benign',
            'benign': 'benign'
        }
        
        df['pathogenicity'] = df['pathogenicity'].map(pathogenicity_mapping).fillna('vus')
        
        # Map consequence types
        consequence_mapping = {
            'missense': 'missense',
            'nonsense': 'nonsense',
            'frameshift': 'frameshift',
            'splice site': 'splice_site',
            'splice_site': 'splice_site',
            'synonymous': 'synonymous',
            'inframe indel': 'inframe_indel',
            'inframe_indel': 'inframe_indel',
            'in-frame indel': 'inframe_indel'
        }
        
        df['consequence'] = df['consequence'].map(consequence_mapping).fillna('missense')
        
        # Create MutationData objects
        mutation_objects = []
        for _, row in df.iterrows():
            notes = row.get('notes', '') if 'notes' in df.columns else ''
            
            mutation_data = MutationData(
                file=mutation_file,
                gene=row['gene'][:50],  # Limit length
                mutation=row['mutation'][:200],  # Limit length
                consequence=row['consequence'],
                pathogenicity=row['pathogenicity'],
                notes=str(notes)[:1000] if notes else ''  # Limit length
            )
            mutation_objects.append(mutation_data)
        
        # Bulk create mutation data
        MutationData.objects.bulk_create(mutation_objects, batch_size=1000)
        
        # Update file record
        mutation_file.mutations_count = len(mutation_objects)
        mutation_file.processed = True
        mutation_file.processing_error = None
        mutation_file.save()
        
        logger.info(f"Successfully processed {len(mutation_objects)} mutations from file {mutation_file.id}")
        return True
        
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        mutation_file.processing_error = error_msg
        mutation_file.save()
        logger.error(f"CSV processing error for {mutation_file.id}: {error_msg}")
        return False

def get_mutation_preview(mutation_file: MutationFile, limit=5):
    """
    Get a preview of mutations from the file
    """
    return mutation_file.mutations.all()[:limit]

def get_mutation_statistics(mutation_file: MutationFile):
    """
    Get statistics about mutations in the file
    """
    mutations = mutation_file.mutations.all()
    
    if not mutations.exists():
        return {
            'total_mutations': 0,
            'pathogenicity_distribution': {},
            'consequence_distribution': {},
            'top_genes': []
        }
    
    # Pathogenicity distribution
    pathogenicity_counts = {}
    for choice in MutationData.PATHOGENICITY_CHOICES:
        count = mutations.filter(pathogenicity=choice[0]).count()
        if count > 0:
            pathogenicity_counts[choice[1]] = count
    
    # Consequence distribution
    consequence_counts = {}
    for choice in MutationData.CONSEQUENCE_CHOICES:
        count = mutations.filter(consequence=choice[0]).count()
        if count > 0:
            consequence_counts[choice[1]] = count
    
    # Top genes
    top_genes = (mutations.values('gene')
                .annotate(count=models.Count('gene'))
                .order_by('-count')[:10])
    
    return {
        'total_mutations': mutations.count(),
        'pathogenicity_distribution': pathogenicity_counts,
        'consequence_distribution': consequence_counts,
        'top_genes': list(top_genes)
    }