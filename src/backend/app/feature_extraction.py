import numpy as np
from typing import Dict
import re

class GeneticFeatureExtractor:
    def __init__(self):
        self.sickle_cell_genes = [
            'HBB', 'BCL11A', 'MYB', 'HOXA9', 'HBG1', 'HBG2', 
            'CHD4', 'KLF1', 'MBD3', 'ZBTB7A', 'PGLYRP1'
        ]
        
        self.breast_cancer_genes = {
            'high_penetrance': ['BRCA1', 'BRCA2', 'TP53', 'CDH1', 'PTEN', 'STK11'],
            'moderate_penetrance': ['CHEK2', 'BRIP1', 'ATM', 'PALB2'],
            'low_penetrance': ['FGFR2', 'LSP1', 'MAP3K1', 'TGFB1', 'TOX3', 
                              'RECQL', 'MUTYH', 'MSH6', 'NF1', 'NBN']
        }

    def extract_features(self, sequence: str, disease_type: str) -> Dict[str, float]:
        features = {}
        
        # Common sequence features
        features.update(self._extract_sequence_features(sequence))
        
        # Disease-specific features
        if disease_type == "sickle_cell":
            features.update(self._extract_sickle_cell_features(sequence))
        elif disease_type == "breast_cancer":
            features.update(self._extract_breast_cancer_features(sequence))
        
        return features

    def _extract_sequence_features(self, sequence: str) -> Dict[str, float]:
        seq_len = len(sequence)
        return {
            'sequence_length': seq_len,
            'gc_content': (sequence.count('G') + sequence.count('C')) / max(seq_len, 1),
            'at_content': (sequence.count('A') + sequence.count('T')) / max(seq_len, 1),
            'g_content': sequence.count('G') / max(seq_len, 1),
            'c_content': sequence.count('C') / max(seq_len, 1),
            'a_content': sequence.count('A') / max(seq_len, 1),
            't_content': sequence.count('T') / max(seq_len, 1),
        }

    def _extract_sickle_cell_features(self, sequence: str) -> Dict[str, float]:
        features = {}
        
        # HBB mutation detection (sickle cell specific)
        normal_codon = 'GAG'
        mutant_codon = 'GTG'
        normal_count = sequence.count(normal_codon)
        mutant_count = sequence.count(mutant_codon)
        
        features['hbb_mutation_ratio'] = (
            mutant_count / max(normal_count + mutant_count, 1)
        )
        
        # Add all 16 dinucleotides (essential for trained model)
        dinucleotides = ['AA', 'AT', 'AG', 'AC', 'TA', 'TT', 'TG', 'TC',
                        'GA', 'GT', 'GG', 'GC', 'CA', 'CT', 'CG', 'CC']
        for dinuc in dinucleotides:
            count = sequence.count(dinuc)
            features[f'dinuc_{dinuc}'] = count / max(len(sequence) - 1, 1)
        
        # K-mer analysis (8 key k-mers)
        sc_kmers = ['ATG', 'GTG', 'TAG', 'TAA', 'TGA', 'GAG', 'GTT', 'GTC']
        for kmer in sc_kmers:
            features[f'kmer_{kmer}'] = sequence.count(kmer) / max(len(sequence) - 2, 1)
        
        # Advanced features
        features['sequence_entropy'] = self._calculate_entropy(sequence)
        features['cpg_islands'] = self._count_cpg_islands(sequence)
        features['homopolymer_runs'] = self._count_homopolymer_runs(sequence)
        
        # Purine/Pyrimidine ratio
        purines = sequence.count('A') + sequence.count('G')
        pyrimidines = sequence.count('C') + sequence.count('T')
        features['purine_pyrimidine_ratio'] = purines / max(pyrimidines, 1)
        
        # Transition/Transversion ratio (estimated from sequence composition)
        features['transition_transversion_ratio'] = 1.0  # Placeholder
        
        # Stop codons
        stop_codons = ['TAA', 'TAG', 'TGA']
        features['stop_codon_count'] = sum(sequence.count(codon) for codon in stop_codons)
        
        # Regulatory proximity
        window_size = 20
        proximity_score = 0
        for i in range(len(sequence) - 3 + 1):
            if sequence[i:i+3] == mutant_codon:
                window_start = max(0, i - window_size)
                window_end = min(len(sequence), i + window_size)
                window = sequence[window_start:window_end]
                for motif in ['CACCC', 'CCAAT', 'TATA']:
                    if motif in window:
                        proximity_score += 1
        features['regulatory_proximity'] = proximity_score / max(mutant_count, 1)
        
        return features
    
    def _calculate_entropy(self, sequence: str) -> float:
        """Calculate Shannon entropy of the sequence"""
        if not sequence:
            return 0.0
        bases = ['A', 'T', 'G', 'C']
        probabilities = [sequence.count(base) / len(sequence) for base in bases]
        entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probabilities)
        return entropy
    
    def _count_cpg_islands(self, sequence: str) -> int:
        """Count CpG dinucleotides (CG)"""
        return sequence.count('CG')
    
    def _count_homopolymer_runs(self, sequence: str) -> int:
        """Count runs of 3+ identical bases"""
        count = 0
        patterns = ['AAA', 'TTT', 'GGG', 'CCC']
        for pattern in patterns:
            count += sequence.count(pattern)
        return count

    def _extract_breast_cancer_features(self, sequence: str) -> Dict[str, float]:
        features = {}
        
        # BRCA related motifs
        features['brca1_motif'] = float('GGCGC' in sequence)
        features['brca2_motif'] = float('TGGAA' in sequence)
        
        # DNA repair indicators
        features['dna_repair_motifs'] = sequence.count('GG') + sequence.count('CC')
        
        # Enhanced breast cancer specific motifs
        bc_motifs = {
            'brca1_promoter': 'GATTTTCCCAGC',
            'brca2_exon': 'TCGGGTTTC',
            'tp53_hotspot': 'TGCCCCTC',
            'her2_amplicon': 'GGCTCCGCAG'
        }
        
        for name, motif in bc_motifs.items():
            features[f'{name}_present'] = float(motif in sequence)
            features[f'{name}_count'] = sequence.count(motif) / max(len(sequence) - len(motif) + 1, 1)
        
        # Mutation pattern detection
        # Common mutation patterns in breast cancer genes
        mutation_patterns = {
            'deletion_pattern': 'G' * 5,  # Homopolymer runs often have deletions
            'insertion_hotspot': 'ATATAT',  # A-T rich regions prone to insertions
            'substitution_site': 'CpG'  # CpG sites often have substitutions
        }
        
        for name, pattern in mutation_patterns.items():
            features[f'{name}_count'] = sequence.count(pattern) / max(len(sequence) - len(pattern) + 1, 1)
        
        # Structural analysis
        repeats = self._detect_tandem_repeats(sequence)
        features['tandem_repeat_count'] = len(repeats)
        features['longest_repeat_length'] = max([len(r) for r in repeats]) if repeats else 0
        
        # Promoter region analysis
        tata_box = sequence.count('TATAA')
        gc_box = sequence.count('GGGCGG')
        features['promoter_elements'] = (tata_box + gc_box) / max(len(sequence) - 5, 1)
        
        return features
        
    def _detect_tandem_repeats(self, sequence: str, min_length=4, max_length=10) -> list:
        """
        Detect tandem repeats in a DNA sequence
        """
        repeats = []
        
        for length in range(min_length, max_length + 1):
            for i in range(len(sequence) - 2*length + 1):
                pattern = sequence[i:i+length]
                if pattern == sequence[i+length:i+2*length]:
                    repeats.append(pattern)
                    
        return list(set(repeats))  # Remove duplicates
