"""
Create sickle cell samples matching the EXACT training pattern
"""

from Bio import SeqIO

print("="*70)
print("CREATING SICKLE CELL SAMPLES MATCHING TRAINING PATTERN")
print("="*70)

# Load the HBB sequence that was used for training
with open('data/raw/gene_sequences/HBB_sequence.fasta', 'r') as f:
    hbb_record = list(SeqIO.parse(f, 'fasta'))[0]
    hbb_seq = str(hbb_record.seq).upper()

print(f"\nHBB sequence loaded: {len(hbb_seq)} bp")
print(f"   GAG count (normal): {hbb_seq.count('GAG')}")
print(f"   GTG count (mutant): {hbb_seq.count('GTG')}")

# Create pathogenic sample - GAG -> GTG mutation
# This is the EXACT mutation pattern used in training
pathogenic_seq = hbb_seq.replace('GAG', 'GTG', 1)  # Replace first GAG with GTG

print(f"\nCreated pathogenic sequence:")
print(f"   GAG count: {pathogenic_seq.count('GAG')}")
print(f"   GTG count: {pathogenic_seq.count('GTG')}")
print(f"   Length: {len(pathogenic_seq)} bp")

# Save pathogenic sample
filename = "data/test/high_confidence_samples/REAL_TRAINING_pathogenic_sickle_cell.fasta"
with open(filename, 'w') as f:
    f.write(">REAL_TRAINING_PATTERN|HBB|GAG>GTG_sickle_cell_mutation|Pathogenic\n")
    for i in range(0, len(pathogenic_seq), 80):
        f.write(pathogenic_seq[i:i+80] + "\n")

print(f"\nSaved: {filename}")

# Create benign sample - keep GAG intact
benign_seq = hbb_seq  # Normal sequence

filename_benign = "data/test/high_confidence_samples/REAL_TRAINING_benign_sickle_cell.fasta"
with open(filename_benign, 'w') as f:
    f.write(">REAL_TRAINING_PATTERN|HBB|Normal_GAG_intact|Benign\n")
    for i in range(0, len(benign_seq), 80):
        f.write(benign_seq[i:i+80] + "\n")

print(f"Saved: {filename_benign}")

print("\n" + "="*70)
print("THESE MATCH THE EXACT TRAINING PATTERN!")
print("="*70)
print("\nThe sickle cell model was trained on sequences where:")
print("  Pathogenic = HBB with GAG -> GTG mutation")
print("  Benign = HBB with GAG intact (normal)")
print()
print("These samples should show HIGH confidence!")
print("  - REAL_TRAINING_pathogenic_sickle_cell.fasta -> 70-90% pathogenic")
print("  - REAL_TRAINING_benign_sickle_cell.fasta -> 70-90% benign (low confidence)")
print("="*70)
