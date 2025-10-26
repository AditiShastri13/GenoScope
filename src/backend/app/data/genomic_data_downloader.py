"""
Genomic Data Downloader Module

This module provides functionality to download and process real genomic data
from various public databases including NCBI, ClinVar, and TCGA.
"""

import os
import requests
import pandas as pd
import numpy as np
from Bio import Entrez, SeqIO
from typing import List, Dict, Tuple, Optional
import logging
import time
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenomicDataDownloader:
    """
    Downloads and processes genomic data from public databases
    """
    
    def __init__(self, email: str, data_dir: str = None):
        """
        Initialize the data downloader
        
        Args:
            email: Your email for NCBI Entrez (required by NCBI)
            data_dir: Directory to store downloaded data
        """
        self.email = email
        Entrez.email = email
        
        # Set up data directory
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(os.path.dirname(current_dir), 'data', 'raw')
        
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"GenomicDataDownloader initialized. Data will be stored in: {self.data_dir}")
    
    def download_sickle_cell_data_from_clinvar(self, max_records: int = 1000) -> pd.DataFrame:
        """
        Download sickle cell anemia related data from ClinVar database
        
        Args:
            max_records: Maximum number of records to download
            
        Returns:
            DataFrame with sickle cell genetic data
        """
        logger.info("Downloading sickle cell data from ClinVar...")
        
        try:
            # Search ClinVar for sickle cell anemia variants
            search_term = "sickle cell anemia[Disease/Phenotype] AND HBB[Gene]"
            
            # Search for records
            handle = Entrez.esearch(
                db="clinvar",
                term=search_term,
                retmax=max_records
            )
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record["IdList"]
            logger.info(f"Found {len(id_list)} ClinVar records for sickle cell anemia")
            
            # Fetch details for each record
            data = []
            for i, variant_id in enumerate(id_list[:max_records]):
                if i % 50 == 0:
                    logger.info(f"Processing record {i+1}/{len(id_list)}")
                    time.sleep(0.5)  # Be nice to NCBI servers
                
                try:
                    handle = Entrez.efetch(db="clinvar", id=variant_id, rettype="vcv", retmode="xml")
                    variant_data = Entrez.read(handle)
                    handle.close()
                    
                    # Extract relevant information
                    variant_info = self._parse_clinvar_record(variant_data, "sickle_cell")
                    if variant_info:
                        data.append(variant_info)
                        
                except Exception as e:
                    logger.warning(f"Error processing variant {variant_id}: {e}")
                    continue
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Save to file
            output_file = os.path.join(self.data_dir, 'sickle_cell_clinvar_data.csv')
            df.to_csv(output_file, index=False)
            logger.info(f"Saved {len(df)} sickle cell records to {output_file}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error downloading sickle cell data: {e}")
            return pd.DataFrame()
    
    def download_breast_cancer_data_from_clinvar(self, max_records: int = 1000) -> pd.DataFrame:
        """
        Download breast cancer related data from ClinVar database
        
        Args:
            max_records: Maximum number of records to download
            
        Returns:
            DataFrame with breast cancer genetic data
        """
        logger.info("Downloading breast cancer data from ClinVar...")
        
        try:
            # Search ClinVar for breast cancer variants in BRCA1 and BRCA2
            genes = ["BRCA1", "BRCA2", "TP53", "PTEN", "CHEK2"]
            all_data = []
            
            for gene in genes:
                logger.info(f"Downloading variants for {gene}...")
                search_term = f"breast cancer[Disease/Phenotype] AND {gene}[Gene]"
                
                # Search for records
                handle = Entrez.esearch(
                    db="clinvar",
                    term=search_term,
                    retmax=max_records // len(genes)
                )
                record = Entrez.read(handle)
                handle.close()
                
                id_list = record["IdList"]
                logger.info(f"Found {len(id_list)} ClinVar records for {gene}")
                
                # Fetch details for each record
                for i, variant_id in enumerate(id_list):
                    if i % 50 == 0:
                        time.sleep(0.5)  # Be nice to NCBI servers
                    
                    try:
                        handle = Entrez.efetch(db="clinvar", id=variant_id, rettype="vcv", retmode="xml")
                        variant_data = Entrez.read(handle)
                        handle.close()
                        
                        # Extract relevant information
                        variant_info = self._parse_clinvar_record(variant_data, "breast_cancer", gene)
                        if variant_info:
                            all_data.append(variant_info)
                            
                    except Exception as e:
                        logger.warning(f"Error processing variant {variant_id}: {e}")
                        continue
            
            # Convert to DataFrame
            df = pd.DataFrame(all_data)
            
            # Save to file
            output_file = os.path.join(self.data_dir, 'breast_cancer_clinvar_data.csv')
            df.to_csv(output_file, index=False)
            logger.info(f"Saved {len(df)} breast cancer records to {output_file}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error downloading breast cancer data: {e}")
            return pd.DataFrame()
    
    def download_gene_sequences_from_ncbi(self, gene_symbols: List[str], 
                                          species: str = "Homo sapiens") -> Dict[str, str]:
        """
        Download gene sequences from NCBI Gene database
        
        Args:
            gene_symbols: List of gene symbols (e.g., ['BRCA1', 'BRCA2'])
            species: Species name
            
        Returns:
            Dictionary mapping gene symbols to sequences
        """
        logger.info(f"Downloading gene sequences from NCBI for genes: {gene_symbols}")
        
        sequences = {}
        
        for gene in gene_symbols:
            try:
                # Search for the gene
                search_term = f"{gene}[Gene Name] AND {species}[Organism]"
                handle = Entrez.esearch(db="gene", term=search_term, retmax=1)
                record = Entrez.read(handle)
                handle.close()
                
                if not record["IdList"]:
                    logger.warning(f"No records found for gene {gene}")
                    continue
                
                gene_id = record["IdList"][0]
                
                # Get gene details
                handle = Entrez.efetch(db="gene", id=gene_id, rettype="gene_table", retmode="text")
                gene_data = handle.read()
                handle.close()
                
                # Now get the nucleotide sequence
                # Link from gene to nucleotide
                handle = Entrez.elink(dbfrom="gene", db="nuccore", id=gene_id)
                link_record = Entrez.read(handle)
                handle.close()
                
                if link_record[0]["LinkSetDb"]:
                    nuccore_ids = [link["Id"] for link in link_record[0]["LinkSetDb"][0]["Link"]]
                    
                    # Fetch the first nucleotide sequence
                    if nuccore_ids:
                        handle = Entrez.efetch(db="nuccore", id=nuccore_ids[0], 
                                             rettype="fasta", retmode="text")
                        fasta_data = handle.read()
                        handle.close()
                        
                        # Parse the FASTA to get just the sequence
                        lines = fasta_data.split('\n')
                        sequence = ''.join(lines[1:])  # Skip header
                        sequences[gene] = sequence
                        
                        logger.info(f"Downloaded sequence for {gene} (length: {len(sequence)})")
                        
                        # Save to file
                        output_file = os.path.join(self.data_dir, f'{gene}_sequence.fasta')
                        with open(output_file, 'w') as f:
                            f.write(fasta_data)
                
                time.sleep(0.5)  # Be nice to NCBI servers
                
            except Exception as e:
                logger.error(f"Error downloading sequence for gene {gene}: {e}")
                continue
        
        return sequences
    
    def _parse_clinvar_record(self, record: dict, disease_type: str, 
                             gene: str = None) -> Optional[Dict]:
        """
        Parse a ClinVar record and extract relevant information
        
        Args:
            record: ClinVar record from Entrez
            disease_type: Type of disease (sickle_cell or breast_cancer)
            gene: Gene name
            
        Returns:
            Dictionary with extracted information
        """
        try:
            # This is a simplified parser - ClinVar XML structure is complex
            # You may need to adjust based on actual data structure
            
            variant_info = {
                'disease_type': disease_type,
                'gene': gene or 'Unknown',
                'variant_id': str(record.get('id', 'Unknown')),
                'clinical_significance': 'Unknown',
                'variant_type': 'Unknown',
                'has_mutation': 0  # Default to no mutation (normal)
            }
            
            # Try to extract clinical significance
            # Note: The actual structure depends on ClinVar XML format
            # This is a placeholder that you'll need to adjust
            
            # For demo purposes, assign pathogenic/likely pathogenic as positive cases
            clinical_sig = str(record).lower()
            if 'pathogenic' in clinical_sig or 'likely pathogenic' in clinical_sig:
                variant_info['has_mutation'] = 1
                variant_info['clinical_significance'] = 'Pathogenic'
            elif 'benign' in clinical_sig or 'likely benign' in clinical_sig:
                variant_info['has_mutation'] = 0
                variant_info['clinical_significance'] = 'Benign'
            else:
                variant_info['clinical_significance'] = 'Uncertain'
                variant_info['has_mutation'] = 0
            
            return variant_info
            
        except Exception as e:
            logger.warning(f"Error parsing ClinVar record: {e}")
            return None
    
    def download_1000genomes_data(self, chromosome: str = "11", 
                                  start: int = 5200000, 
                                  end: int = 5300000) -> pd.DataFrame:
        """
        Download data from 1000 Genomes Project
        
        Args:
            chromosome: Chromosome number
            start: Start position
            end: End position
            
        Returns:
            DataFrame with variant data
        """
        logger.info("Downloading data from 1000 Genomes Project...")
        
        # 1000 Genomes FTP URL
        base_url = f"http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"
        vcf_file = f"ALL.chr{chromosome}.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz"
        
        url = base_url + vcf_file
        
        logger.info(f"Note: 1000 Genomes VCF files are very large (several GB).")
        logger.info(f"For research purposes, consider downloading specific regions or using tabix.")
        logger.info(f"URL: {url}")
        
        # For this implementation, we'll return instructions rather than download
        # You would need pysam and tabix for efficient region queries
        
        instructions = {
            'url': url,
            'method': 'Use pysam.TabixFile for efficient querying',
            'example': f'tabix {vcf_file} {chromosome}:{start}-{end}'
        }
        
        return pd.DataFrame([instructions])
    
    def create_training_dataset_from_fasta_files(self, fasta_dir: str, 
                                                  labels_file: str) -> pd.DataFrame:
        """
        Create a training dataset from FASTA files with corresponding labels
        
        Args:
            fasta_dir: Directory containing FASTA files
            labels_file: CSV file with sequence IDs and labels
            
        Returns:
            DataFrame ready for model training
        """
        logger.info(f"Creating training dataset from FASTA files in {fasta_dir}")
        
        # Load labels
        labels_df = pd.read_csv(labels_file)
        
        # Process FASTA files
        data = []
        for fasta_file in Path(fasta_dir).glob("*.fasta"):
            try:
                for record in SeqIO.parse(fasta_file, "fasta"):
                    sequence_id = record.id
                    sequence = str(record.seq)
                    
                    # Find label for this sequence
                    label_row = labels_df[labels_df['sequence_id'] == sequence_id]
                    
                    if not label_row.empty:
                        label = label_row.iloc[0]['label']
                        disease_type = label_row.iloc[0].get('disease_type', 'unknown')
                        
                        data.append({
                            'sequence_id': sequence_id,
                            'sequence': sequence,
                            'label': label,
                            'disease_type': disease_type,
                            'sequence_length': len(sequence)
                        })
                        
            except Exception as e:
                logger.error(f"Error processing {fasta_file}: {e}")
                continue
        
        df = pd.DataFrame(data)
        logger.info(f"Created dataset with {len(df)} sequences")
        
        return df


class RealDataModelTrainer:
    """
    Train models using real genomic data downloaded from public databases
    """
    
    def __init__(self, downloader: GenomicDataDownloader, feature_extractor):
        """
        Initialize the trainer
        
        Args:
            downloader: GenomicDataDownloader instance
            feature_extractor: GeneticFeatureExtractor instance
        """
        self.downloader = downloader
        self.feature_extractor = feature_extractor
        
    def prepare_training_data(self, sequences_df: pd.DataFrame, 
                             disease_type: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data by extracting features from sequences
        
        Args:
            sequences_df: DataFrame with 'sequence' and 'label' columns
            disease_type: Type of disease for feature extraction
            
        Returns:
            Tuple of (features DataFrame, labels Series)
        """
        logger.info(f"Preparing training data for {disease_type}...")
        
        features_list = []
        labels = []
        
        for idx, row in sequences_df.iterrows():
            try:
                sequence = row['sequence']
                label = row['label']
                
                # Extract features
                features = self.feature_extractor.extract_features(sequence, disease_type)
                features_list.append(features)
                labels.append(label)
                
                if idx % 100 == 0:
                    logger.info(f"Processed {idx}/{len(sequences_df)} sequences")
                    
            except Exception as e:
                logger.warning(f"Error processing sequence at index {idx}: {e}")
                continue
        
        X = pd.DataFrame(features_list)
        y = pd.Series(labels)
        
        logger.info(f"Prepared {len(X)} training samples with {len(X.columns)} features")
        
        return X, y


# Example usage script
def example_download_workflow():
    """
    Example workflow for downloading and preparing real genomic data
    """
    
    # Initialize downloader with your email
    downloader = GenomicDataDownloader(email="your.email@example.com")
    
    # Download sickle cell data
    print("\n=== Downloading Sickle Cell Data ===")
    sickle_cell_df = downloader.download_sickle_cell_data_from_clinvar(max_records=500)
    print(f"Downloaded {len(sickle_cell_df)} sickle cell records")
    
    # Download breast cancer data
    print("\n=== Downloading Breast Cancer Data ===")
    breast_cancer_df = downloader.download_breast_cancer_data_from_clinvar(max_records=500)
    print(f"Downloaded {len(breast_cancer_df)} breast cancer records")
    
    # Download gene sequences
    print("\n=== Downloading Gene Sequences ===")
    sickle_cell_genes = ['HBB', 'BCL11A']
    breast_cancer_genes = ['BRCA1', 'BRCA2']
    
    sc_sequences = downloader.download_gene_sequences_from_ncbi(sickle_cell_genes)
    bc_sequences = downloader.download_gene_sequences_from_ncbi(breast_cancer_genes)
    
    print(f"Downloaded {len(sc_sequences)} sickle cell gene sequences")
    print(f"Downloaded {len(bc_sequences)} breast cancer gene sequences")
    
    print("\n=== Data Download Complete ===")
    print(f"All data saved to: {downloader.data_dir}")


if __name__ == "__main__":
    # Run example workflow
    example_download_workflow()
