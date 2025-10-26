"""
Script to download and prepare real genomic data for model training

This script will:
1. Download sickle cell and breast cancer data from ClinVar
2. Download reference gene sequences from NCBI
3. Prepare the data for model training
4. Save processed datasets
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

from app.data.genomic_data_downloader import GenomicDataDownloader, RealDataModelTrainer
from app.feature_extraction import GeneticFeatureExtractor

def main(email: str, max_records: int = 500, download_type: str = "all"):
    """
    Main function to download and prepare genomic data
    
    Args:
        email: Your email address (required by NCBI)
        max_records: Maximum number of records to download per disease
        download_type: Type of data to download ('sickle_cell', 'breast_cancer', or 'all')
    """
    
    print("="*70)
    print("Genoscope Real Data Downloader")
    print("="*70)
    print()
    
    # Initialize downloader
    print(f"Initializing data downloader (email: {email})...")
    downloader = GenomicDataDownloader(email=email)
    
    print(f"Data will be saved to: {downloader.data_dir}")
    print()
    
    # Download sickle cell data
    if download_type in ["sickle_cell", "all"]:
        print("\n" + "="*70)
        print("STEP 1: Downloading Sickle Cell Anemia Data from ClinVar")
        print("="*70)
        print(f"Requesting up to {max_records} records...")
        print("This may take several minutes depending on NCBI server response...")
        print()
        
        try:
            sickle_cell_df = downloader.download_sickle_cell_data_from_clinvar(
                max_records=max_records
            )
            
            if len(sickle_cell_df) > 0:
                print(f"\n✓ Successfully downloaded {len(sickle_cell_df)} sickle cell records")
                print(f"  - Pathogenic variants: {len(sickle_cell_df[sickle_cell_df['has_mutation'] == 1])}")
                print(f"  - Benign variants: {len(sickle_cell_df[sickle_cell_df['has_mutation'] == 0])}")
            else:
                print("\n✗ No sickle cell data was downloaded")
                
        except Exception as e:
            print(f"\n✗ Error downloading sickle cell data: {e}")
            print("  This might be due to NCBI server issues or API rate limiting.")
            print("  Try again later or reduce max_records.")
    
    # Download breast cancer data
    if download_type in ["breast_cancer", "all"]:
        print("\n" + "="*70)
        print("STEP 2: Downloading Breast Cancer Data from ClinVar")
        print("="*70)
        print(f"Requesting up to {max_records} records...")
        print("This may take several minutes depending on NCBI server response...")
        print()
        
        try:
            breast_cancer_df = downloader.download_breast_cancer_data_from_clinvar(
                max_records=max_records
            )
            
            if len(breast_cancer_df) > 0:
                print(f"\n✓ Successfully downloaded {len(breast_cancer_df)} breast cancer records")
                print(f"  - Pathogenic variants: {len(breast_cancer_df[breast_cancer_df['has_mutation'] == 1])}")
                print(f"  - Benign variants: {len(breast_cancer_df[breast_cancer_df['has_mutation'] == 0])}")
                
                # Show gene distribution
                print(f"\n  Gene distribution:")
                gene_counts = breast_cancer_df['gene'].value_counts()
                for gene, count in gene_counts.items():
                    print(f"    - {gene}: {count} variants")
            else:
                print("\n✗ No breast cancer data was downloaded")
                
        except Exception as e:
            print(f"\n✗ Error downloading breast cancer data: {e}")
            print("  This might be due to NCBI server issues or API rate limiting.")
            print("  Try again later or reduce max_records.")
    
    # Download reference gene sequences
    print("\n" + "="*70)
    print("STEP 3: Downloading Reference Gene Sequences from NCBI")
    print("="*70)
    
    all_genes = []
    if download_type in ["sickle_cell", "all"]:
        all_genes.extend(['HBB', 'BCL11A'])
    if download_type in ["breast_cancer", "all"]:
        all_genes.extend(['BRCA1', 'BRCA2', 'TP53'])
    
    print(f"Downloading sequences for genes: {', '.join(all_genes)}")
    print()
    
    try:
        sequences = downloader.download_gene_sequences_from_ncbi(all_genes)
        
        if sequences:
            print(f"\n✓ Successfully downloaded {len(sequences)} gene sequences:")
            for gene, seq in sequences.items():
                print(f"  - {gene}: {len(seq)} base pairs")
        else:
            print("\n✗ No gene sequences were downloaded")
            
    except Exception as e:
        print(f"\n✗ Error downloading gene sequences: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE")
    print("="*70)
    print()
    print(f"All data has been saved to: {downloader.data_dir}")
    print()
    print("Next steps:")
    print("1. Review the downloaded data files")
    print("2. Run the model training script with real data:")
    print("   python train_with_real_data.py")
    print()
    print("For research papers, you can now:")
    print("- Document the data sources and number of samples")
    print("- Compare model performance with synthetic vs real data")
    print("- Report the class distribution (pathogenic vs benign)")
    print()


def print_usage_instructions():
    """Print instructions for using public genomic databases"""
    
    print("\n" + "="*70)
    print("ADDITIONAL DATA SOURCES FOR RESEARCH")
    print("="*70)
    print()
    
    print("1. NCBI ClinVar (Clinical Variants)")
    print("   - URL: https://www.ncbi.nlm.nih.gov/clinvar/")
    print("   - Contains clinically relevant genetic variants")
    print("   - Can be searched by gene, disease, or variant type")
    print("   - ✓ Automated download implemented in this script")
    print()
    
    print("2. The Cancer Genome Atlas (TCGA)")
    print("   - URL: https://portal.gdc.cancer.gov/")
    print("   - Large-scale cancer genomics data")
    print("   - Requires data access request")
    print("   - Download: Use GDC Data Transfer Tool")
    print()
    
    print("3. 1000 Genomes Project")
    print("   - URL: https://www.internationalgenome.org/")
    print("   - Population-scale genomic variation data")
    print("   - VCF files available via FTP")
    print("   - Use: pysam/tabix for querying specific regions")
    print()
    
    print("4. UK Biobank")
    print("   - URL: https://www.ukbiobank.ac.uk/")
    print("   - Large-scale biomedical database")
    print("   - Requires research application and approval")
    print("   - Data access: Through approved research projects only")
    print()
    
    print("5. NCBI Gene Database")
    print("   - URL: https://www.ncbi.nlm.nih.gov/gene")
    print("   - Reference gene sequences and annotations")
    print("   - ✓ Automated download implemented in this script")
    print()
    
    print("For your research paper, consider:")
    print("- Documenting all data sources with proper citations")
    print("- Reporting data preprocessing steps")
    print("- Describing quality control measures")
    print("- Discussing any data limitations or biases")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download real genomic data for Genoscope model training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all data types (default 500 records each)
  python download_real_data.py --email your.email@example.com

  # Download only sickle cell data with more records
  python download_real_data.py --email your.email@example.com --type sickle_cell --max-records 1000

  # Download only breast cancer data
  python download_real_data.py --email your.email@example.com --type breast_cancer

  # Show information about data sources
  python download_real_data.py --info

Note: NCBI requires an email address for API access. This helps them contact you
if there are problems with your queries. Your email is not used for any other purpose.
        """
    )
    
    parser.add_argument(
        "--email",
        type=str,
        help="Your email address (required by NCBI Entrez)"
    )
    
    parser.add_argument(
        "--max-records",
        type=int,
        default=500,
        help="Maximum number of records to download per disease type (default: 500)"
    )
    
    parser.add_argument(
        "--type",
        choices=["all", "sickle_cell", "breast_cancer"],
        default="all",
        help="Type of data to download (default: all)"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Display information about genomic data sources and exit"
    )
    
    args = parser.parse_args()
    
    # Show info and exit
    if args.info:
        print_usage_instructions()
        sys.exit(0)
    
    # Check for required email
    if not args.email:
        print("Error: --email is required for downloading data from NCBI")
        print()
        print("Usage: python download_real_data.py --email your.email@example.com")
        print()
        print("For more information, run: python download_real_data.py --help")
        print("Or to see data sources info: python download_real_data.py --info")
        sys.exit(1)
    
    # Run the download
    try:
        main(email=args.email, max_records=args.max_records, download_type=args.type)
        print_usage_instructions()
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
