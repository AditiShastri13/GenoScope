"""
Machine Learning engine for genetic predictions
"""
import random
import logging
from typing import Dict, List, Tuple
from mutations.models import MutationFile, MutationData
from .models import PredictionResult, DiseaseProbability, MutationDistribution

logger = logging.getLogger('genoscope')

class GeneticMLEngine:
    """
    Mock ML engine for genetic disease prediction
    In production, this would use real ML models (scikit-learn, TensorFlow, PyTorch)
    """
    
    # Disease prediction mappings based on key genes
    DISEASE_GENE_MAPPING = {
        'BRCA1': ['Breast Cancer', 'Ovarian Cancer'],
        'BRCA2': ['Breast Cancer', 'Ovarian Cancer', 'Prostate Cancer'],
        'TP53': ['Li-Fraumeni Syndrome', 'Breast Cancer', 'Colorectal Cancer'],
        'PTEN': ['Cowden Syndrome', 'Breast Cancer'],
        'ATM': ['Ataxia Telangiectasia', 'Breast Cancer'],
        'APOE': ["Alzheimer's Disease", 'Cardiovascular Disease'],
        'CHEK2': ['Breast Cancer', 'Colorectal Cancer'],
        'MLH1': ['Lynch Syndrome', 'Colorectal Cancer'],
        'PALB2': ['Breast Cancer', 'Pancreatic Cancer'],
        'EGFR': ['Lung Cancer', 'Colorectal Cancer'],
    }
    
    COMMON_DISEASES = [
        'Breast Cancer', 'Colorectal Cancer', 'Lung Cancer', 
        'Prostate Cancer', 'Ovarian Cancer', 'Pancreatic Cancer',
        "Alzheimer's Disease", 'Cardiovascular Disease',
        'Diabetes Type 2', 'Melanoma'
    ]
    
    def analyze_mutations(self, mutation_file: MutationFile) -> Dict:
        """
        Perform ML analysis on mutation data
        """
        try:
            mutations = mutation_file.mutations.all()
            
            if not mutations.exists():
                raise ValueError("No mutations found in file")
            
            # Analyze key mutations
            pathogenic_mutations = mutations.filter(
                pathogenicity__in=['pathogenic', 'likely_pathogenic']
            )
            
            # Find the most significant mutation
            key_mutation = self._find_key_mutation(pathogenic_mutations)
            
            # Predict disease based on key genes
            predicted_disease, confidence = self._predict_disease(pathogenic_mutations)
            
            # Generate disease probabilities
            disease_probabilities = self._generate_disease_probabilities(
                pathogenic_mutations, predicted_disease, confidence
            )
            
            # Calculate mutation distribution
            mutation_distribution = self._calculate_mutation_distribution(mutations)
            
            return {
                'predicted_disease': predicted_disease,
                'confidence_score': confidence,
                'key_mutation': key_mutation,
                'disease_probabilities': disease_probabilities,
                'mutation_distribution': mutation_distribution
            }
            
        except Exception as e:
            logger.error(f"ML analysis error for file {mutation_file.id}: {str(e)}")
            raise
    
    def _find_key_mutation(self, pathogenic_mutations) -> str:
        """
        Find the most significant mutation
        """
        if not pathogenic_mutations.exists():
            return "No pathogenic mutations found"
        
        # Prioritize known cancer genes
        priority_genes = ['BRCA1', 'BRCA2', 'TP53', 'PTEN', 'ATM']
        
        for gene in priority_genes:
            mutation = pathogenic_mutations.filter(gene=gene).first()
            if mutation:
                return f"{mutation.gene} {mutation.mutation}"
        
        # Return first pathogenic mutation
        first_mutation = pathogenic_mutations.first()
        return f"{first_mutation.gene} {first_mutation.mutation}"
    
    def _predict_disease(self, pathogenic_mutations) -> Tuple[str, float]:
        """
        Predict primary disease and confidence
        """
        if not pathogenic_mutations.exists():
            # Random disease for demonstration
            disease = random.choice(self.COMMON_DISEASES)
            confidence = random.uniform(20, 40)
            return disease, confidence
        
        # Count genes and their associated diseases
        disease_scores = {}
        gene_count = {}
        
        for mutation in pathogenic_mutations:
            gene = mutation.gene
            gene_count[gene] = gene_count.get(gene, 0) + 1
            
            if gene in self.DISEASE_GENE_MAPPING:
                for disease in self.DISEASE_GENE_MAPPING[gene]:
                    weight = 2.0 if mutation.pathogenicity == 'pathogenic' else 1.5
                    disease_scores[disease] = disease_scores.get(disease, 0) + weight
        
        if not disease_scores:
            disease = random.choice(self.COMMON_DISEASES)
            confidence = random.uniform(30, 50)
            return disease, confidence
        
        # Find top disease
        top_disease = max(disease_scores.items(), key=lambda x: x[1])
        disease = top_disease[0]
        
        # Calculate confidence based on score and number of mutations
        base_confidence = min(top_disease[1] * 15, 95)  # Max 95%
        mutation_bonus = min(len(pathogenic_mutations) * 2, 10)
        confidence = min(base_confidence + mutation_bonus, 98)
        
        return disease, round(confidence, 1)
    
    def _generate_disease_probabilities(self, pathogenic_mutations, primary_disease: str, primary_confidence: float) -> List[Dict]:
        """
        Generate probabilities for multiple diseases
        """
        probabilities = [{'disease': primary_disease, 'confidence': primary_confidence}]
        
        # Add other diseases with lower probabilities
        other_diseases = [d for d in self.COMMON_DISEASES if d != primary_disease]
        random.shuffle(other_diseases)
        
        for i, disease in enumerate(other_diseases[:4]):  # Top 4 other diseases
            # Decreasing probability for other diseases
            confidence = max(primary_confidence - (i + 1) * 15 - random.uniform(5, 15), 5)
            probabilities.append({
                'disease': disease,
                'confidence': round(confidence, 1)
            })
        
        return probabilities
    
    def _calculate_mutation_distribution(self, mutations) -> List[Dict]:
        """
        Calculate distribution of mutation types
        """
        total_mutations = mutations.count()
        
        if total_mutations == 0:
            return []
        
        # Simplified mutation type classification
        snp_count = int(total_mutations * random.uniform(0.6, 0.7))
        indel_count = int(total_mutations * random.uniform(0.2, 0.3))
        deletion_count = total_mutations - snp_count - indel_count
        
        distribution = [
            {
                'type': 'SNP',
                'count': snp_count,
                'percentage': round((snp_count / total_mutations) * 100, 1)
            },
            {
                'type': 'Indel',
                'count': indel_count,
                'percentage': round((indel_count / total_mutations) * 100, 1)
            },
            {
                'type': 'Deletion',
                'count': deletion_count,
                'percentage': round((deletion_count / total_mutations) * 100, 1)
            }
        ]
        
        return distribution

# Global ML engine instance
ml_engine = GeneticMLEngine()