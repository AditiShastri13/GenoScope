# How to Use Real Data - GenoScope

## Overview
This guide explains how to collect and use real genomic data from public databases (NCBI Gene and ClinVar) for training machine learning models in GenoScope.

---

## Step 1: Collect Gene Sequences from NCBI

### What is NCBI Gene?
The National Center for Biotechnology Information (NCBI) Gene database contains official gene sequences for all organisms.

### How to Download Gene Sequences

**Option 1: Using the Web Interface**

1. Go to https://www.ncbi.nlm.nih.gov/gene
2. Search for your gene (e.g., "BRCA1 human")
3. Click on the gene result
4. Navigate to "Genomic regions, transcripts, and products"
5. Click "FASTA" next to the gene sequence
6. Save the .fasta file

**Option 2: Using Biopython (Automated)**

```python
from Bio import Entrez, SeqIO

# Set your email (required by NCBI)
Entrez.email = "your.email@example.com"

# Gene IDs for common genes
gene_ids = {
    'HBB': '3043',      # Sickle cell
    'BRCA1': '672',     # Breast cancer
    'BRCA2': '675',     # Breast cancer
    'TP53': '7157',     # Breast cancer
    'BCL11A': '53335'   # Sickle cell modifier
}

# Download each gene
for gene_name, gene_id in gene_ids.items():
    print(f"Downloading {gene_name}...")
    
    # Fetch the gene record
    handle = Entrez.efetch(
        db="gene",
        id=gene_id,
        rettype="fasta",
        retmode="text"
    )
    
    # Save to file
    with open(f"data/raw/gene_sequences/{gene_name}_sequence.fasta", "w") as f:
        f.write(handle.read())
    
    handle.close()
    print(f"✓ Saved {gene_name}_sequence.fasta")
```

### Genes Used in GenoScope

| Gene | ID | Size | Disease | Downloaded |
|------|-----|------|---------|------------|
| HBB | 3043 | 444 bp | Sickle Cell | ✅ |
| BCL11A | 53335 | 6,085 bp | Sickle Cell (modifier) | ✅ |
| BRCA1 | 672 | 5,376 bp | Breast Cancer | ✅ |
| BRCA2 | 675 | 10,257 bp | Breast Cancer | ✅ |
| TP53 | 7157 | 2,399 bp | Breast Cancer | ✅ |

**Total**: 24,561 base pairs of real genomic data

---

## Step 2: Download ClinVar Variants

### What is ClinVar?
ClinVar is a public archive of reports of relationships among human variations and phenotypes, maintained by NIH.

### Method 1: Download Full VCF File (Recommended)

**Download the Latest Release**:
```bash
# Download ClinVar VCF (large file - 166.92 MB compressed)
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz

# Decompress
gunzip clinvar.vcf.gz
```

**Parse VCF File**:
```python
import pandas as pd
import re

def parse_clinvar_vcf(vcf_path, genes=['BRCA1', 'BRCA2', 'TP53']):
    """Parse ClinVar VCF and extract variant information"""
    variants = []
    
    with open(vcf_path, 'r') as f:
        for line in f:
            # Skip header lines
            if line.startswith('#'):
                continue
            
            # Parse VCF fields
            fields = line.strip().split('\t')
            chrom = fields[0]
            pos = fields[1]
            ref = fields[3]
            alt = fields[4]
            info = fields[7]
            
            # Extract gene symbol
            gene_match = re.search(r'GENEINFO=([^:]+)', info)
            if not gene_match:
                continue
            gene = gene_match.group(1)
            
            # Filter by target genes
            if gene not in genes:
                continue
            
            # Extract clinical significance
            clin_sig_match = re.search(r'CLNSIG=([^;]+)', info)
            if not clin_sig_match:
                continue
            clin_sig = clin_sig_match.group(1)
            
            # Extract review status
            review_match = re.search(r'CLNREVSTAT=([^;]+)', info)
            review_status = review_match.group(1) if review_match else 'no_assertion'
            
            variants.append({
                'gene': gene,
                'chrom': chrom,
                'pos': int(pos),
                'ref': ref,
                'alt': alt,
                'clinical_significance': clin_sig,
                'review_status': review_status
            })
    
    return pd.DataFrame(variants)

# Parse the file
print("Parsing ClinVar VCF...")
df = parse_clinvar_vcf('data/raw/clinvar/clinvar.vcf', genes=['BRCA1', 'BRCA2', 'TP53'])

# Save to CSV
df.to_csv('data/raw/clinvar/clinvar_breast_cancer_variants.csv', index=False)
print(f"✓ Extracted {len(df)} variants")
```

### Method 2: Use Our Download Script

```bash
python src/scripts/download_clinvar_variants.py
```

This script automatically:
1. Downloads the latest ClinVar VCF
2. Filters variants by target genes
3. Extracts relevant fields
4. Saves to CSV format

---

## Step 3: Filter and Process Variants

### Filter by Clinical Significance

```python
import pandas as pd

# Load variants
df = pd.read_csv('data/raw/clinvar/clinvar_breast_cancer_variants.csv')

print(f"Total variants: {len(df)}")

# Filter for pathogenic and benign variants
pathogenic_variants = df[
    df['clinical_significance'].str.contains('Pathogenic', case=False, na=False) &
    ~df['clinical_significance'].str.contains('Conflicting', case=False, na=False)
]

benign_variants = df[
    df['clinical_significance'].str.contains('Benign', case=False, na=False) &
    ~df['clinical_significance'].str.contains('Conflicting', case=False, na=False)
]

print(f"Pathogenic variants: {len(pathogenic_variants)}")
print(f"Benign variants: {len(benign_variants)}")

# Combine
filtered_df = pd.concat([pathogenic_variants, benign_variants])

# Save
filtered_df.to_csv('data/processed/breast_cancer_clinvar_filtered.csv', index=False)
```

### Create Training Samples

```python
from Bio import SeqIO

def create_training_sample(gene_seq, variant_pos, ref, alt, label):
    """
    Create a training sample by applying variant to gene sequence
    
    Args:
        gene_seq: Full gene sequence
        variant_pos: Position of variant
        ref: Reference allele
        alt: Alternate allele
        label: 'pathogenic' or 'benign'
    
    Returns:
        Dictionary with sequence and label
    """
    # Extract region around variant (±500 bp)
    start = max(0, variant_pos - 500)
    end = min(len(gene_seq), variant_pos + 500)
    
    # Get sequence
    seq = str(gene_seq[start:end])
    
    # Apply variant (simplified - real version more complex)
    variant_offset = variant_pos - start
    if variant_offset >= 0 and variant_offset < len(seq):
        if seq[variant_offset:variant_offset+len(ref)] == ref:
            # Substitute
            seq = seq[:variant_offset] + alt + seq[variant_offset+len(ref):]
    
    return {
        'sequence': seq,
        'label': 1 if label == 'pathogenic' else 0,
        'gene': 'BRCA1',
        'position': variant_pos,
        'ref': ref,
        'alt': alt
    }

# Load gene sequences
gene_sequences = {}
for gene in ['BRCA1', 'BRCA2', 'TP53']:
    record = SeqIO.read(f"data/raw/gene_sequences/{gene}_sequence.fasta", "fasta")
    gene_sequences[gene] = record.seq

# Load filtered variants
variants_df = pd.read_csv('data/processed/breast_cancer_clinvar_filtered.csv')

# Create training samples
training_samples = []
for _, row in variants_df.iterrows():
    gene_seq = gene_sequences.get(row['gene'])
    if not gene_seq:
        continue
    
    label = 'pathogenic' if 'Pathogenic' in row['clinical_significance'] else 'benign'
    
    sample = create_training_sample(
        gene_seq,
        row['pos'],
        row['ref'],
        row['alt'],
        label
    )
    training_samples.append(sample)

# Save training samples
import json
with open('data/raw/clinvar/clinvar_training_samples.json', 'w') as f:
    json.dump(training_samples, f, indent=2)

print(f"✓ Created {len(training_samples)} training samples")
```

---

## Step 4: Extract Features

Use the feature extraction pipeline:

```python
from src.backend.app.feature_extraction import GeneticFeatureExtractor

extractor = GeneticFeatureExtractor()

# Load training samples
with open('data/raw/clinvar/clinvar_training_samples.json', 'r') as f:
    samples = json.load(f)

# Extract features for each sample
features_list = []
labels = []

for sample in samples:
    # Determine disease type based on gene
    disease_type = 'breast_cancer' if sample['gene'] in ['BRCA1', 'BRCA2', 'TP53'] else 'sickle_cell'
    
    # Extract features
    features = extractor.extract_features(sample['sequence'], disease_type)
    features_list.append(features)
    labels.append(sample['label'])

# Convert to DataFrame
features_df = pd.DataFrame(features_list)
features_df['label'] = labels

# Save
features_df.to_csv('data/processed/breast_cancer_clinvar_features.csv', index=False)
print(f"✓ Extracted features for {len(features_df)} samples")
```

---

## Step 5: Train Model with Real Data

```python
from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier
import joblib

# Load features
df = pd.read_csv('data/processed/breast_cancer_clinvar_features.csv')

# Separate features and labels
X = df.drop('label', axis=1)
y = df['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
model = XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    gamma=0.1,
    random_state=42
)

print("Training model...")
model.fit(X_train, y_train)

# Evaluate
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')

print(f"Train Accuracy: {train_score:.4f}")
print(f"Test Accuracy: {test_score:.4f}")
print(f"CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Save model
joblib.dump(model, 'models/production/breast_cancer_clinvar_model.pkl')
print("✓ Model saved")
```

---

## Data Statistics

### GenoScope Real Data

**Gene Sequences**:
- Source: NCBI Gene
- Total: 5 genes, 24,561 base pairs
- Format: FASTA

**ClinVar Variants**:
- Source: NIH ClinVar
- Total: 20,637 variants (BRCA1, BRCA2, TP53)
- Filtered: 1,134 training samples
- Distribution: 418 pathogenic (36.9%), 716 benign (63.1%)

**Training Data**:
- Sickle Cell: 800 samples (synthetic + real sequences)
- Breast Cancer: 1,134 samples (ClinVar variants)
- Format: CSV with 40 genomic features

---

## Quality Control

### Variant Filtering Criteria

✅ **Include**:
- Pathogenic, Likely pathogenic
- Benign, Likely benign
- Review status ≥ 1 star
- Single nucleotide variants (SNVs)
- Small insertions/deletions (<50 bp)

❌ **Exclude**:
- Conflicting interpretations
- Uncertain significance (VUS)
- Review status: no assertion
- Structural variants (>50 bp)
- Poor quality annotations

### Data Validation

```python
def validate_training_data(df):
    """Validate training data quality"""
    
    issues = []
    
    # Check class balance
    class_counts = df['label'].value_counts()
    imbalance_ratio = class_counts.max() / class_counts.min()
    if imbalance_ratio > 3:
        issues.append(f"Class imbalance: {imbalance_ratio:.2f}:1")
    
    # Check for missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        issues.append(f"Missing values: {missing}")
    
    # Check sequence lengths
    if 'sequence_length' in df.columns:
        if df['sequence_length'].min() < 50:
            issues.append("Very short sequences detected")
    
    # Check feature variance
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    low_variance = [col for col in numeric_cols if df[col].std() < 0.01]
    if low_variance:
        issues.append(f"Low variance features: {len(low_variance)}")
    
    if issues:
        print("⚠️  Data quality issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ Data validation passed")
    
    return len(issues) == 0

# Validate
validate_training_data(features_df)
```

---

## Best Practices

### 1. Always Use Latest Data
```bash
# Update ClinVar monthly
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
```

### 2. Document Data Sources
```python
metadata = {
    'clinvar_version': '2024-12',
    'clinvar_download_date': '2024-12-15',
    'genes': ['BRCA1', 'BRCA2', 'TP53'],
    'total_variants': 20637,
    'training_samples': 1134,
    'filters_applied': [
        'Pathogenic/Benign only',
        'No conflicting interpretations',
        'Review status >= 1 star'
    ]
}
```

### 3. Version Your Datasets
```
data/
├── v1.0_2024-11/
│   ├── clinvar_variants.csv
│   └── training_samples.json
├── v1.1_2024-12/
│   ├── clinvar_variants.csv
│   └── training_samples.json
└── latest/ -> v1.1_2024-12/
```

### 4. Keep Raw Data
- Never modify original downloaded files
- Apply transformations to copies
- Document all processing steps

---

## Troubleshooting

### Issue: Download Fails
```bash
# Use resume flag
wget -c https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
```

### Issue: Too Many Variants
```python
# Sample if dataset is too large
df_sampled = df.sample(n=5000, random_state=42, stratify=df['label'])
```

### Issue: Class Imbalance
```python
from imblearn.over_sampling import SMOTE

# Balance classes
smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X, y)
```

---

## Next Steps

After collecting real data:
1. ✅ Extract features (40 genomic features)
2. ✅ Train models (XGBoost, Gradient Boosting)
3. ✅ Evaluate with cross-validation
4. ✅ Save models to `models/production/`
5. ✅ Update web application

---

**Last Updated**: December 2024  
**Related Docs**: REAL_DATA_GUIDE.md, OPTIMIZATION_PIPELINE.md  
**Scripts**: `download_clinvar_variants.py`, `train_with_real_sequences.py`
