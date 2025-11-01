"""
Simple ClinVar Data Downloader
Downloads pathogenic and benign variants for breast cancer genes
"""

import requests
from Bio import Entrez
import time
import os

# REQUIRED: Set your email for NCBI
Entrez.email = "shwetayeola23@gmail.com"

print("="*70)
print("Simple ClinVar Variant Downloader")
print("="*70)
print()

# Create output directory
os.makedirs("data/test", exist_ok=True)

# Breast cancer genes
genes = {
    'BRCA1': '672',
    'BRCA2': '675',
    'TP53': '7157'
}

print("Downloading gene sequences from NCBI...")
print()

for gene_name, gene_id in genes.items():
    print(f"📥 Downloading {gene_name} (Gene ID: {gene_id})...")
    
    try:
        # First, get the gene record to find the sequence accession
        handle = Entrez.esummary(db="gene", id=gene_id)
        record = Entrez.read(handle)
        handle.close()
        
        # Now fetch from nuccore database for actual sequence
        # Use efetch with db="nuccore" and search for mRNA
        search_term = f"{gene_name}[Gene Name] AND Homo sapiens[Organism] AND mRNA[Filter]"
        handle = Entrez.esearch(db="nuccore", term=search_term, retmax=1)
        search_results = Entrez.read(handle)
        handle.close()
        
        if search_results['IdList']:
            seq_id = search_results['IdList'][0]
            
            # Fetch the sequence
            handle = Entrez.efetch(db="nuccore", id=seq_id, rettype="fasta", retmode="text")
            sequence_data = handle.read()
            handle.close()
            
            if sequence_data and len(sequence_data) > 100:
                # Save to file
                filename = f"data/test/{gene_name}_reference.fasta"
                with open(filename, "w") as f:
                    f.write(sequence_data)
                
                # Count sequence length (excluding header)
                seq_length = sum(len(line.strip()) for line in sequence_data.split('\n') if not line.startswith('>'))
                
                print(f"   ✅ Saved {filename}")
                print(f"   📊 Sequence length: {seq_length} bp")
            else:
                print(f"   ⚠️  No sequence data found for {gene_name}")
        else:
            print(f"   ⚠️  No mRNA sequence found for {gene_name}")
        
        # Be nice to NCBI servers
        time.sleep(1)
        
    except Exception as e:
        print(f"   ❌ Error downloading {gene_name}: {e}")
    
    print()

print("="*70)
print("Download Complete!")
print("="*70)
print()
print("Files saved to: data/test/")
print()
print("Next steps:")
print("1. Check the downloaded .fasta files in data/test/")
print("2. Upload them through your frontend at http://localhost:3000")
print("3. The models will analyze them for pathogenic variants")
print()
print("Note: These are reference sequences. To test pathogenic variants,")
print("you'll need to manually edit them or download specific variants")
print("from ClinVar: https://www.ncbi.nlm.nih.gov/clinvar/")
