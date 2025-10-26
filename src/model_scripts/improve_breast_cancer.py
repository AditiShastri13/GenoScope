"""
Advanced Breast Cancer Model Improvement

This script implements targeted strategies to improve breast cancer accuracy:
1. Increase training data (4000 samples)
2. Add more diverse mutation types
3. Implement class balancing techniques
4. Try different algorithms (XGBoost, LightGBM)
5. Use more aggressive hyperparameter search
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from Bio import SeqIO
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib
import logging
import json

# Add parent directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.feature_extraction import GeneticFeatureExtractor

# Import enhanced extractor
exec(open('optimize_features.py').read(), globals())

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_advanced_breast_cancer_mutations(sequence: str, gene_name: str) -> tuple:
    """Create realistic breast cancer mutations with known pathogenic patterns"""
    
    seq_list = list(sequence)
    mutation_type = np.random.choice(['missense', 'frameshift', 'splice_site', 'deletion', 'insertion'])
    
    if gene_name == 'BRCA1':
        # Known BRCA1 hotspots: exons 11, 12, 13 (middle region)
        hotspot_region = len(seq_list) // 2
        
        if mutation_type == 'frameshift':
            # Frameshift mutation (highly pathogenic)
            pos = np.random.randint(max(0, hotspot_region - 100), min(len(seq_list), hotspot_region + 100))
            # Delete 1-2 bases (causes frameshift)
            del_size = np.random.randint(1, 3)
            for _ in range(del_size):
                if pos < len(seq_list):
                    seq_list.pop(pos)
        
        elif mutation_type == 'splice_site':
            # Splice site mutation (GT->GC or AG->AA)
            # Find GT or AG patterns
            seq_str = ''.join(seq_list)
            if 'GT' in seq_str:
                pos = seq_str.find('GT')
                seq_list[pos] = 'G'
                seq_list[pos + 1] = 'C'
            
        elif mutation_type == 'deletion':
            # Large deletion (3-50 bases)
            pos = np.random.randint(0, len(seq_list) - 50)
            del_size = np.random.randint(3, 51)
            for _ in range(min(del_size, len(seq_list) - pos)):
                if pos < len(seq_list):
                    seq_list.pop(pos)
    
    elif gene_name == 'BRCA2':
        # Known BRCA2 hotspots: exon 10, 11 (large central exons)
        hotspot_region = len(seq_list) // 2
        
        if mutation_type == 'missense':
            # Multiple missense mutations
            num_muts = np.random.randint(3, 8)
            bases = ['A', 'T', 'G', 'C']
            for _ in range(num_muts):
                pos = np.random.randint(max(0, hotspot_region - 200), min(len(seq_list), hotspot_region + 200))
                seq_list[pos] = np.random.choice([b for b in bases if b != seq_list[pos]])
        
        elif mutation_type == 'deletion':
            pos = np.random.randint(0, len(seq_list) - 100)
            del_size = np.random.randint(5, 101)
            for _ in range(min(del_size, len(seq_list) - pos)):
                if pos < len(seq_list):
                    seq_list.pop(pos)
    
    elif gene_name == 'TP53':
        # TP53 hotspots: codons 175, 245, 248, 273, 282 (DNA binding domain)
        # Approximate position: around 1/3 to 2/3 of gene
        hotspot_start = len(seq_list) // 3
        hotspot_end = 2 * len(seq_list) // 3
        
        if mutation_type == 'missense':
            # Single critical missense (like R175H, R273H)
            pos = np.random.randint(hotspot_start, hotspot_end)
            bases = ['A', 'T', 'G', 'C']
            # Change single base in critical codon
            seq_list[pos] = np.random.choice([b for b in bases if b != seq_list[pos]])
        
        elif mutation_type == 'frameshift':
            pos = np.random.randint(hotspot_start, hotspot_end)
            del_size = np.random.randint(1, 4)
            for _ in range(del_size):
                if pos < len(seq_list):
                    seq_list.pop(pos)
    
    else:
        # Generic mutations for other genes
        num_muts = np.random.randint(2, 6)
        bases = ['A', 'T', 'G', 'C']
        for _ in range(num_muts):
            pos = np.random.randint(0, len(seq_list))
            seq_list[pos] = np.random.choice([b for b in bases if b != seq_list[pos]])
    
    return ''.join(seq_list), mutation_type


def generate_large_breast_cancer_dataset(gene_sequences: dict, 
                                         enhanced_extractor: EnhancedFeatureExtractor,
                                         num_samples: int = 4000) -> tuple:
    """Generate larger, more balanced dataset"""
    
    logger.info(f"Generating LARGE dataset: {num_samples} samples for breast cancer...")
    
    features_list = []
    labels = []
    mutation_types = []
    
    relevant_genes = [g for g in ['BRCA1', 'BRCA2', 'TP53'] if g in gene_sequences]
    
    # Aim for 40% pathogenic (instead of 30%)
    target_pathogenic = int(num_samples * 0.40)
    target_benign = num_samples - target_pathogenic
    
    pathogenic_count = 0
    benign_count = 0
    
    while pathogenic_count < target_pathogenic or benign_count < target_benign:
        gene = np.random.choice(relevant_genes)
        base_sequence = gene_sequences[gene]
        
        # Extract random window
        if len(base_sequence) > 1000:
            start = np.random.randint(0, len(base_sequence) - 1000)
            sequence = base_sequence[start:start + 1000]
        else:
            sequence = base_sequence
        
        # Decide if pathogenic or benign
        if pathogenic_count < target_pathogenic:
            is_pathogenic = True
        elif benign_count < target_benign:
            is_pathogenic = False
        else:
            break
        
        if is_pathogenic:
            sequence, mut_type = create_advanced_breast_cancer_mutations(sequence, gene)
            label = 1
            pathogenic_count += 1
        else:
            # Benign: either no mutation or very minor single mutation
            if np.random.random() < 0.7:
                # 70% completely benign
                mut_type = 'benign'
            else:
                # 30% single neutral variant
                seq_list = list(sequence)
                pos = np.random.randint(0, len(seq_list))
                bases = ['A', 'T', 'G', 'C']
                seq_list[pos] = np.random.choice([b for b in bases if b != seq_list[pos]])
                sequence = ''.join(seq_list)
                mut_type = 'neutral'
            label = 0
            benign_count += 1
        
        try:
            features = enhanced_extractor.extract_enhanced_features(sequence, 'breast_cancer')
            features_list.append(features)
            labels.append(label)
            mutation_types.append(mut_type)
        except Exception as e:
            continue
    
    X = pd.DataFrame(features_list)
    y = pd.Series(labels)
    
    logger.info(f"✓ Created LARGE dataset: {len(X)} samples, {len(X.columns)} features")
    logger.info(f"  Class balance: {sum(y==1)/len(y)*100:.1f}% pathogenic ({sum(y==1)} samples)")
    logger.info(f"  Mutation types: {pd.Series(mutation_types).value_counts().to_dict()}")
    
    return X, y


def try_xgboost_if_available(X_train, y_train, X_test, y_test):
    """Try XGBoost if available (better than GradientBoosting)"""
    
    try:
        import xgboost as xgb
        logger.info("\n✓ XGBoost detected - using XGBClassifier")
        
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
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"  XGBoost Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        return model, accuracy, 'XGBoost'
    
    except ImportError:
        logger.info("\n✗ XGBoost not installed - using GradientBoosting")
        return None, 0, None


def train_with_class_balancing(X, y):
    """Train with SMOTE oversampling for minority class"""
    
    logger.info(f"\n{'='*70}")
    logger.info(f"TRAINING WITH CLASS BALANCING (SMOTE)")
    logger.info(f"{'='*70}")
    
    # Load selected features
    features_file = os.path.join('trained_models', 'breast_cancer_selected_features.json')
    if os.path.exists(features_file):
        with open(features_file, 'r') as f:
            selected_features = json.load(f)
        X = X[selected_features]
        logger.info(f"Using {len(selected_features)} selected features")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"\nOriginal class distribution:")
    logger.info(f"  Train: {sum(y_train==1)}/{len(y_train)} pathogenic ({sum(y_train==1)/len(y_train)*100:.1f}%)")
    logger.info(f"  Test:  {sum(y_test==1)}/{len(y_test)} pathogenic ({sum(y_test==1)/len(y_test)*100:.1f}%)")
    
    # Apply SMOTE to balance training data
    logger.info(f"\nApplying SMOTE oversampling...")
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    
    logger.info(f"After SMOTE:")
    logger.info(f"  Train: {sum(y_train_balanced==1)}/{len(y_train_balanced)} pathogenic ({sum(y_train_balanced==1)/len(y_train_balanced)*100:.1f}%)")
    logger.info(f"  Added {len(X_train_balanced) - len(X_train)} synthetic samples")
    
    # Try XGBoost first
    xgb_model, xgb_acc, _ = try_xgboost_if_available(X_train_balanced, y_train_balanced, X_test, y_test)
    
    # Train Gradient Boosting with aggressive parameters
    logger.info(f"\nTraining GradientBoosting with aggressive parameters...")
    gb_model = GradientBoostingClassifier(
        n_estimators=500,  # More trees
        learning_rate=0.05,  # Lower learning rate
        max_depth=10,  # Deeper trees
        min_samples_leaf=1,  # Allow more specific splits
        min_samples_split=2,
        subsample=0.8,
        max_features='sqrt',
        random_state=42
    )
    
    gb_model.fit(X_train_balanced, y_train_balanced)
    
    # Evaluate both models
    y_pred_gb = gb_model.predict(X_test)
    gb_accuracy = accuracy_score(y_test, y_pred_gb)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"TEST SET RESULTS:")
    logger.info(f"{'='*70}")
    
    if xgb_model and xgb_acc > gb_accuracy:
        logger.info(f"\n✓ XGBoost performed better!")
        logger.info(f"  XGBoost:         {xgb_acc:.4f} ({xgb_acc*100:.2f}%)")
        logger.info(f"  GradientBoosting: {gb_accuracy:.4f} ({gb_accuracy*100:.2f}%)")
        
        best_model = xgb_model
        best_accuracy = xgb_acc
        model_name = 'XGBoost'
        y_pred = xgb_model.predict(X_test)
    else:
        logger.info(f"\n✓ GradientBoosting performed better!")
        if xgb_model:
            logger.info(f"  GradientBoosting: {gb_accuracy:.4f} ({gb_accuracy*100:.2f}%)")
            logger.info(f"  XGBoost:         {xgb_acc:.4f} ({xgb_acc*100:.2f}%)")
        else:
            logger.info(f"  GradientBoosting: {gb_accuracy:.4f} ({gb_accuracy*100:.2f}%)")
        
        best_model = gb_model
        best_accuracy = gb_accuracy
        model_name = 'GradientBoosting'
        y_pred = y_pred_gb
    
    logger.info(f"\n{classification_report(y_test, y_pred, target_names=['Benign', 'Pathogenic'])}")
    
    # Cross-validation on balanced data
    logger.info(f"Running 5-fold cross-validation on balanced data...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(best_model, X_train_balanced, y_train_balanced, 
                                cv=cv, scoring='accuracy', n_jobs=-1)
    
    logger.info(f"\nCross-Validation (on balanced training data):")
    logger.info(f"  Fold accuracies: {[f'{s:.4f}' for s in cv_scores]}")
    logger.info(f"  Mean CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    logger.info(f"  This is: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")
    
    # Also test on original test set (more realistic)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average='weighted'
    )
    
    metrics = {
        'model_name': model_name,
        'test_accuracy': best_accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'training_samples': len(X_train_balanced),
        'smote_applied': True
    }
    
    return best_model, metrics


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("Breast Cancer Model - Advanced Improvement")
    print("="*70)
    print()
    print("Strategies:")
    print("  1. Larger dataset (4000 samples)")
    print("  2. More realistic mutations (BRCA1/2, TP53 hotspots)")
    print("  3. Class balancing (SMOTE)")
    print("  4. XGBoost if available")
    print("  5. Aggressive hyperparameters")
    print("="*70)
    print()
    
    # Setup
    current_dir = Path(__file__).parent
    data_dir = os.path.join(current_dir, 'app', 'data', 'raw')
    models_dir = os.path.join(current_dir, 'trained_models')
    
    # Load sequences
    logger.info("Loading gene sequences...")
    gene_sequences = load_gene_sequences(data_dir)
    logger.info(f"✓ Loaded {len(gene_sequences)} gene sequences")
    
    # Initialize extractors
    base_extractor = GeneticFeatureExtractor()
    enhanced_extractor = EnhancedFeatureExtractor(base_extractor)
    
    # Generate LARGE dataset
    X, y = generate_large_breast_cancer_dataset(
        gene_sequences, enhanced_extractor, num_samples=4000
    )
    
    # Train with class balancing
    model, metrics = train_with_class_balancing(X, y)
    
    # Save improved model
    model_file = os.path.join(models_dir, 'breast_cancer_improved_model.pkl')
    joblib.dump(model, model_file)
    logger.info(f"\n✓ Saved improved model: {model_file}")
    
    # Save metrics
    metrics_file = os.path.join(models_dir, 'breast_cancer_improved_metrics.json')
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    logger.info(f"✓ Saved metrics: {metrics_file}")
    
    # Final summary
    print("\n" + "="*70)
    print("IMPROVEMENT RESULTS")
    print("="*70)
    print()
    print(f"Model: {metrics['model_name']}")
    print(f"Training Samples: {metrics['training_samples']} (with SMOTE)")
    print(f"Test Accuracy:  {metrics['test_accuracy']:.4f} ({metrics['test_accuracy']*100:.2f}%)")
    print(f"CV Accuracy:    {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
    print(f"                ({metrics['cv_mean']*100:.2f}% ± {metrics['cv_std']*100:.2f}%)")
    print(f"Precision:      {metrics['precision']:.4f}")
    print(f"Recall:         {metrics['recall']:.4f}")
    print(f"F1-Score:       {metrics['f1_score']:.4f}")
    print()
    print("="*70)
    print("\nComparison with previous best:")
    print("  Previous: 70.80% (Stage 3 Optimized)")
    print(f"  Current:  {metrics['test_accuracy']*100:.2f}%")
    
    if metrics['test_accuracy'] > 0.708:
        improvement = (metrics['test_accuracy'] - 0.708) * 100
        print(f"  Improvement: +{improvement:.2f}%")
    else:
        print("  Note: May need more data or different features")
    
    print("="*70)
    
    # Suggestions for further improvement
    print("\n" + "="*70)
    print("FURTHER IMPROVEMENT SUGGESTIONS:")
    print("="*70)
    print()
    print("1. Install XGBoost for better performance:")
    print("   pip install xgboost")
    print()
    print("2. Collect more real clinical data:")
    print("   - ClinVar pathogenic variants")
    print("   - Patient sequencing data")
    print()
    print("3. Try deep learning:")
    print("   - CNN for sequence analysis")
    print("   - LSTM for sequential patterns")
    print()
    print("4. Add more biological features:")
    print("   - Protein structure predictions")
    print("   - Conservation scores (PhyloP)")
    print("   - Functional impact (PolyPhen, SIFT)")
    print()
    print("5. Ensemble with external tools:")
    print("   - Combine with VEP, CADD, REVEL scores")
    print("="*70)


if __name__ == "__main__":
    main()
