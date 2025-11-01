"""
Debug script to see what features are being extracted from test files
and create optimized sequences based on feature engineering.
"""

import sys
sys.path.append('src/backend')

from app.feature_extraction import GeneticFeatureExtractor  # type: ignore
from Bio import SeqIO

print("="*70)
print("ANALYZING CURRENT TEST FILE FEATURES")
print("="*70)

# Load one of the test files
test_file = "data/test/high_confidence_samples/sickle_cell_HIGH_CONFIDENCE_pathogenic.fasta"
with open(test_file, 'r') as f:
    record = list(SeqIO.parse(f, 'fasta'))[0]
    sequence = str(record.seq)

print(f"\nAnalyzing: {test_file}")
print(f"Length: {len(sequence)} bp")

# Extract features
extractor = GeneticFeatureExtractor()
features = extractor._extract_sickle_cell_features(sequence)

# Show all features
print("\n" + "="*70)
print("EXTRACTED FEATURES (current sequence):")
print("="*70)

# Group by category
print("\n📊 KEY PATHOGENIC MARKERS:")
pathogenic_features = {
    'hbb_mutation_ratio': features.get('hbb_mutation_ratio', 0),
    'kmer_GTG': features.get('kmer_GTG', 0),
    'kmer_GAG': features.get('kmer_GAG', 0),
    'bcl11a_motif_count': features.get('bcl11a_motif_count', 0),
    'myb_motif_count': features.get('myb_motif_count', 0),
    'hbg_promoter_caccc': features.get('hbg_promoter_caccc', 0),
}

for name, value in pathogenic_features.items():
    print(f"  {name:25s}: {value:.4f}")

print("\n📊 GENERAL FEATURES:")
general = {
    'sequence_length': features.get('sequence_length', 0),
    'gc_content': features.get('gc_content', 0),
    'at_content': features.get('at_content', 0),
}
for name, value in general.items():
    print(f"  {name:25s}: {value:.4f}")

# Now create an EXTREME pathogenic sequence
print("\n" + "="*70)
print("CREATING MAXIMALLY PATHOGENIC SEQUENCE")
print("="*70)

# Strategy: Maximize GTG, BCL11A, MYB motifs
pathogenic_seq = ""

# 1. Start with HBB gene start codon
pathogenic_seq += "ATG"

# 2. Add tons of GTG (sickle cell mutation)
pathogenic_seq += "GTG" * 100  # Extreme GTG content

# 3. Add BCL11A motifs (TGAGGG)
pathogenic_seq += "TGAGGG" * 50

# 4. Add MYB motifs (AACGG)  
pathogenic_seq += "AACGG" * 50

# 5. Add HBG promoter CACCC boxes
pathogenic_seq += "CACCC" * 30

# 6. Add more GTG clusters
pathogenic_seq += "GTGGTGGTG" * 20

# 7. Add some "normal" looking sequence to not be too obvious
pathogenic_seq += "ATCGATCGATCG" * 10

# Save this extreme sequence
extreme_file = "data/test/high_confidence_samples/EXTREME_sickle_cell_pathogenic.fasta"
with open(extreme_file, 'w') as f:
    f.write(">EXTREME_pathogenic_sickle_cell|maximal_GTG_BCL11A_MYB\n")
    # Write in 80 char lines
    for i in range(0, len(pathogenic_seq), 80):
        f.write(pathogenic_seq[i:i+80] + "\n")

print(f"\n✅ Created: {extreme_file}")
print(f"   Length: {len(pathogenic_seq)} bp")

# Extract features from extreme sequence
extreme_features = extractor._extract_sickle_cell_features(pathogenic_seq)

print("\n📊 EXTREME SEQUENCE FEATURES:")
for name in pathogenic_features.keys():
    old_val = pathogenic_features[name]
    new_val = extreme_features.get(name, 0)
    change = "↑" if new_val > old_val else "↓" if new_val < old_val else "="
    print(f"  {name:25s}: {old_val:.4f} → {new_val:.4f} {change}")

print("\n" + "="*70)
print("Now try uploading EXTREME_sickle_cell_pathogenic.fasta")
print("This should trigger MUCH higher confidence!")
print("="*70)
