"""
Train Breast Cancer Model with Real ClinVar Variants

This script trains the breast cancer model using REAL pathogenic and benign
variants from ClinVar instead of synthetic mutations.

Expected improvement: +10-15% accuracy
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib

# Add parent directory to path
current_dir = Path(__file__).parent
backend_dir = current_dir.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from app.feature_extraction import GeneticFeatureExtractor

# Create enhanced extractor inline (optimize_features.py may not exist)
class EnhancedFeatureExtractor:
    def __init__(self, base_extractor):
        self.base_extractor = base_extractor
    
    def extract_features(self, sequence: str, disease_type: str = 'breast_cancer') -> dict:
        features = self.base_extractor.extract_features(sequence, disease_type)
        
        # Add enhanced features
        seq_upper = sequence.upper()
        
        # Sequence complexity (entropy)
        from collections import Counter
        counts = Counter(seq_upper)
        total = len(seq_upper)
        entropy = -sum((count/total) * np.log2(count/total) for count in counts.values() if count > 0)
        features['sequence_entropy'] = entropy
        
        # CpG islands
        cpg_count = seq_upper.count('CG')
        features['cpg_islands'] = cpg_count / max(len(seq_upper) - 1, 1)
        
        # Homopolymer runs
        max_run = 1
        current_run = 1
        for i in range(1, len(seq_upper)):
            if seq_upper[i] == seq_upper[i-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        features['homopolymer_runs'] = max_run
        
        # k-mer frequencies (k=3)
        for i in range(len(seq_upper) - 2):
            kmer = seq_upper[i:i+3]
            if len(kmer) == 3 and all(c in 'ATGC' for c in kmer):
                key = f'kmer_{kmer}'
                features[key] = features.get(key, 0) + 1
        
        # Normalize k-mer counts
        total_kmers = len(seq_upper) - 2
        for key in list(features.keys()):
            if key.startswith('kmer_'):
                features[key] /= max(total_kmers, 1)
        
        # Transition/transversion ratio
        transitions = seq_upper.count('AG') + seq_upper.count('GA') + seq_upper.count('CT') + seq_upper.count('TC')
        transversions = seq_upper.count('AC') + seq_upper.count('CA') + seq_upper.count('GT') + seq_upper.count('TG') + \
                       seq_upper.count('AT') + seq_upper.count('TA') + seq_upper.count('GC') + seq_upper.count('CG')
        features['transition_transversion_ratio'] = transitions / max(transversions, 1)
        
        # Deletion/insertion patterns
        features['deletion_pattern_count'] = seq_upper.count('-')
        features['insertion_pattern_count'] = seq_upper.count('+')
        
        return features

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_clinvar_samples(samples_file: str) -> tuple:
    """Load real ClinVar training samples"""
    
    logger.info(f"Loading ClinVar samples from: {samples_file}")
    
    with open(samples_file, 'r') as f:
        samples = json.load(f)
    
    logger.info(f"✓ Loaded {len(samples)} samples")
    
    # Show distribution
    labels = [s['label'] for s in samples]
    pathogenic = sum(labels)
    benign = len(labels) - pathogenic
    
    logger.info(f"  Pathogenic: {pathogenic} ({pathogenic/len(labels)*100:.1f}%)")
    logger.info(f"  Benign:     {benign} ({benign/len(labels)*100:.1f}%)")
    
    # Show molecular consequences
    mol_consequences = pd.Series([s['mol_consequence'] for s in samples]).value_counts()
    logger.info(f"\n  Molecular consequences:")
    for mc, count in mol_consequences.head(5).items():
        logger.info(f"    {mc}: {count}")
    
    return samples


def extract_features_from_samples(samples: list, enhanced_extractor) -> tuple:
    """Extract features from ClinVar samples"""
    
    logger.info("\nExtracting features from real variants...")
    
    features_list = []
    labels = []
    sample_info = []
    
    for i, sample in enumerate(samples):
        if (i + 1) % 100 == 0:
            logger.info(f"  Processing sample {i+1}/{len(samples)}")
        
        try:
            # Extract enhanced features
            features = enhanced_extractor.extract_features(sample['sequence'], 'breast_cancer')
            
            features_list.append(features)
            labels.append(sample['label'])
            sample_info.append({
                'gene': sample['gene'],
                'variant_id': sample['variant_id']
            })
            
        except Exception as e:
            logger.warning(f"Error processing sample {i}: {e}")
            continue
    
    X = pd.DataFrame(features_list)
    y = pd.Series(labels)
    
    logger.info(f"\n✓ Extracted features for {len(X)} samples")
    logger.info(f"  Feature count: {len(X.columns)}")
    logger.info(f"  Final class balance: {sum(y==1)/len(y)*100:.1f}% pathogenic")
    
    return X, y, sample_info


def train_with_clinvar_data(X, y, sample_info):
    """Train model with real ClinVar variants"""
    
    # Get random seed from environment
    import os as os_module
    random_seed = int(os_module.environ.get('RANDOM_SEED', 42))
    
    logger.info(f"\n{'='*70}")
    logger.info(f"TRAINING WITH REAL CLINVAR VARIANTS")
    logger.info(f"{'='*70}")
    
    # Load selected features from previous optimization
    features_file = os.path.join('trained_models', 'breast_cancer_selected_features.json')
    
    if os.path.exists(features_file):
        with open(features_file, 'r') as f:
            selected_features = json.load(f)
        
        # Keep only features that exist
        selected_features = [f for f in selected_features if f in X.columns]
        X = X[selected_features]
        logger.info(f"Using {len(selected_features)} selected features")
    
    # Load optimized hyperparameters
    params_file = os.path.join('trained_models', 'breast_cancer_optimized_metrics.json')
    
    if os.path.exists(params_file):
        with open(params_file, 'r') as f:
            saved_results = json.load(f)
        params = saved_results.get('parameters', {})
        logger.info(f"Using optimized parameters: {params}")
    else:
        params = {
            'n_estimators': 347,
            'learning_rate': 0.135,
            'max_depth': 11,
            'min_samples_leaf': 2
        }
    
    # Split data (use random seed from environment or default 42)
    X_train, X_test, y_train, y_test, info_train, info_test = train_test_split(
        X, y, sample_info, test_size=0.2, random_state=random_seed, stratify=y
    )
    
    logger.info(f"\nDataset split:")
    logger.info(f"  Train: {len(X_train)} samples ({sum(y_train==1)} pathogenic)")
    logger.info(f"  Test:  {len(X_test)} samples ({sum(y_test==1)} pathogenic)")
    
    # Try XGBoost if available
    try:
        import xgboost as xgb
        logger.info(f"\n✓ XGBoost available - using XGBClassifier")
        
        model = xgb.XGBClassifier(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=8,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=random_seed,
            n_jobs=-1,
            eval_metric='logloss'
        )
        model_name = 'XGBoost'
        
    except ImportError:
        logger.info(f"\n✓ Using GradientBoosting")
        model = GradientBoostingClassifier(random_state=random_seed, **params)
        model_name = 'GradientBoosting'
    
    # Train
    logger.info(f"\nTraining {model_name}...")
    model.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"TEST SET RESULTS (REAL CLINVAR VARIANTS)")
    logger.info(f"{'='*70}")
    logger.info(f"\nTest Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    
    logger.info(f"\n{classification_report(y_test, y_pred, target_names=['Benign', 'Pathogenic'])}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"Confusion Matrix:")
    logger.info(f"  True Benign, Pred Benign:     {cm[0][0]}")
    logger.info(f"  True Benign, Pred Pathogenic: {cm[0][1]}")
    logger.info(f"  True Pathogenic, Pred Benign: {cm[1][0]}")
    logger.info(f"  True Pathogenic, Pred Path:   {cm[1][1]}")
    
    # Cross-validation
    logger.info(f"\nRunning 5-fold cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_seed)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy', n_jobs=-1)
    
    logger.info(f"\nCross-Validation Results:")
    logger.info(f"  Fold accuracies: {[f'{s:.4f}' for s in cv_scores]}")
    logger.info(f"  Mean CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    logger.info(f"  This is: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")
    
    # Error analysis - show misclassified variants
    logger.info(f"\n{'='*70}")
    logger.info(f"ERROR ANALYSIS")
    logger.info(f"{'='*70}")
    
    misclassified = []
    for i, (true, pred) in enumerate(zip(y_test, y_pred)):
        if true != pred:
            test_idx = y_test.index[i]
            misclassified.append({
                'variant': info_test[i]['variant_id'],
                'gene': info_test[i]['gene'],
                'true_label': 'Pathogenic' if true == 1 else 'Benign',
                'pred_label': 'Pathogenic' if pred == 1 else 'Benign'
            })
    
    logger.info(f"\nMisclassified variants: {len(misclassified)}/{len(y_test)}")
    
    if len(misclassified) > 0:
        logger.info(f"\nFirst 10 misclassifications:")
        for i, mc in enumerate(misclassified[:10], 1):
            logger.info(f"  {i}. {mc['gene']}: {mc['variant']} - True: {mc['true_label']}, Pred: {mc['pred_label']}")
    
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"\nTop 10 Most Important Features:")
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']:30s}: {row['importance']:.4f}")
    
    # Save model and metrics
    project_root = Path(__file__).parent.parent.parent
    models_dir = project_root / 'models' / 'production'
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_file = models_dir / 'breast_cancer_clinvar_model.pkl'
    joblib.dump(model, model_file)
    logger.info(f"\n✓ Saved model: {model_file}")
    
    metrics = {
        'model_name': model_name,
        'data_source': 'ClinVar_real_variants',
        'test_accuracy': test_accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'features_used': len(X.columns)
    }
    
    metadata_dir = project_root / 'models' / 'metadata'
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = metadata_dir / 'breast_cancer_clinvar_metrics.json'
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    logger.info(f"✓ Saved metrics: {metrics_file}")
    
    if hasattr(model, 'feature_importances_'):
        fi_file = metadata_dir / 'breast_cancer_clinvar_feature_importance.csv'
        feature_importance.to_csv(fi_file, index=False)
        logger.info(f"✓ Saved feature importance: {fi_file}")
    
    return model, metrics


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("Train Breast Cancer Model with Real ClinVar Variants")
    print("="*70)
    print()
    print("This uses REAL pathogenic and benign variants from ClinVar")
    print("Expected improvement: +10-15% accuracy")
    print("="*70)
    print()
    
    # Setup
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent  # Go up to genoscope root
    data_dir = project_root / 'data' / 'raw'
    
    # Load ClinVar samples
    samples_file = data_dir / 'clinvar' / 'clinvar_training_samples.json'
    
    if not samples_file.exists():
        logger.error(f"ClinVar samples not found: {samples_file}")
        logger.error("Please run: python download_clinvar_variants.py first")
        return
    
    samples = load_clinvar_samples(str(samples_file))
    
    # Initialize extractors
    base_extractor = GeneticFeatureExtractor()
    enhanced_extractor = EnhancedFeatureExtractor(base_extractor)
    
    # Extract features
    X, y, sample_info = extract_features_from_samples(samples, enhanced_extractor)
    
    # Train model
    model, metrics = train_with_clinvar_data(X, y, sample_info)
    
    # Final summary
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print()
    print(f"Model: {metrics['model_name']}")
    print(f"Data Source: Real ClinVar Variants")
    print(f"Training Samples: {metrics['training_samples']}")
    print(f"Test Accuracy:  {metrics['test_accuracy']:.4f} ({metrics['test_accuracy']*100:.2f}%)")
    print(f"CV Accuracy:    {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
    print(f"                ({metrics['cv_mean']*100:.2f}% ± {metrics['cv_std']*100:.2f}%)")
    print()
    print("="*70)
    print("\nComparison with synthetic data:")
    print("  Synthetic (Stage 3): 70.80%")
    print(f"  ClinVar (Real):      {metrics['cv_mean']*100:.2f}%")
    
    if metrics['cv_mean'] > 0.708:
        improvement = (metrics['cv_mean'] - 0.708) * 100
        print(f"  Improvement:         +{improvement:.2f}% ✓")
    
    print("="*70)


if __name__ == "__main__":
    main()
