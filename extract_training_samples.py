"""
Extract actual pathogenic samples from training data to test with
"""
import json

# Load training data
with open('data/raw/clinvar/clinvar_training_samples.json', 'r') as f:
    data = json.load(f)

print("="*70)
print("EXTRACTING ACTUAL TRAINING DATA SAMPLES")
print("="*70)

# Find pathogenic samples
pathogenic_brca = [s for s in data if s['label'] == 1 and s.get('gene') in ['BRCA1', 'BRCA2']]
pathogenic_hbb = [s for s in data if s['label'] == 1 and 'HBB' in s.get('gene', '')]

print(f"\n📊 Found in training data:")
print(f"   - BRCA1/2 pathogenic: {len(pathogenic_brca)}")
print(f"   - HBB pathogenic: {len(pathogenic_hbb)}")

# Save a few pathogenic BRCA samples
if pathogenic_brca:
    for i, sample in enumerate(pathogenic_brca[:3]):
        filename = f"data/test/high_confidence_samples/REAL_TRAINING_pathogenic_brca_{i+1}.fasta"
        with open(filename, 'w') as f:
            f.write(f">REAL_TRAINING_DATA|{sample['gene']}|{sample['variant_id']}|{sample['clinical_sig']}\n")
            seq = sample['sequence']
            for j in range(0, len(seq), 80):
                f.write(seq[j:j+80] + "\n")
        
        print(f"\n✅ Created: {filename}")
        print(f"   Gene: {sample['gene']}")
        print(f"   Variant: {sample['variant_id']}")
        print(f"   Clinical: {sample['clinical_sig']}")
        print(f"   Length: {len(sample['sequence'])} bp")

# Save a few pathogenic HBB samples
if pathogenic_hbb:
    for i, sample in enumerate(pathogenic_hbb[:3]):
        filename = f"data/test/high_confidence_samples/REAL_TRAINING_pathogenic_hbb_{i+1}.fasta"
        with open(filename, 'w') as f:
            f.write(f">REAL_TRAINING_DATA|{sample['gene']}|{sample['variant_id']}|{sample['clinical_sig']}\n")
            seq = sample['sequence']
            for j in range(0, len(seq), 80):
                f.write(seq[j:j+80] + "\n")
        
        print(f"\n✅ Created: {filename}")
        print(f"   Gene: {sample['gene']}")
        print(f"   Variant: {sample['variant_id']}")
        print(f"   Clinical: {sample['clinical_sig']}")
        print(f"   Length: {len(sample['sequence'])} bp")

print("\n" + "="*70)
print("🎯 THESE ARE ACTUAL TRAINING SAMPLES!")
print("   The models were trained on these exact sequences.")
print("   They should show 70-90% confidence (matching training accuracy)")
print("="*70)
