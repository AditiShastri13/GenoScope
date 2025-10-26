"""
Model Versioning System for Genoscope

This module provides functionality for tracking and managing versions of trained models.
It includes features for model metadata, tracking training history, and model selection.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import shutil

class ModelVersion:
    """Class representing a single model version"""
    
    def __init__(self, 
                 model_id: str,
                 model_type: str,
                 version: str, 
                 path: str, 
                 training_date: datetime,
                 metrics: Dict[str, float],
                 parameters: Dict[str, Any],
                 description: str = ""):
        """
        Initialize a model version
        
        Args:
            model_id: Unique identifier for the model (e.g., 'sickle_cell_classifier')
            model_type: Type of the model (e.g., 'random_forest', 'svm', 'neural_network')
            version: Version string (e.g., '1.0.0')
            path: Path to the saved model file
            training_date: Date when the model was trained
            metrics: Dictionary of model evaluation metrics (e.g., {'accuracy': 0.95})
            parameters: Dictionary of model parameters
            description: Optional description of the model version
        """
        self.model_id = model_id
        self.model_type = model_type
        self.version = version
        self.path = path
        self.training_date = training_date
        self.metrics = metrics
        self.parameters = parameters
        self.description = description
        
    def to_dict(self) -> Dict:
        """Convert the model version to a dictionary for serialization"""
        return {
            'model_id': self.model_id,
            'model_type': self.model_type,
            'version': self.version,
            'path': self.path,
            'training_date': self.training_date.isoformat(),
            'metrics': self.metrics,
            'parameters': self.parameters,
            'description': self.description
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelVersion':
        """Create a ModelVersion instance from a dictionary"""
        return cls(
            model_id=data['model_id'],
            model_type=data['model_type'],
            version=data['version'],
            path=data['path'],
            training_date=datetime.fromisoformat(data['training_date']),
            metrics=data['metrics'],
            parameters=data['parameters'],
            description=data.get('description', '')
        )


class ModelRegistry:
    """Registry for tracking model versions"""
    
    def __init__(self, registry_path: str):
        """
        Initialize the model registry
        
        Args:
            registry_path: Path to the registry directory
        """
        self.registry_path = registry_path
        self.metadata_file = os.path.join(registry_path, 'model_registry.json')
        self.models: Dict[str, List[ModelVersion]] = {}
        self.load_registry()
        
    def load_registry(self):
        """Load registry from disk"""
        os.makedirs(self.registry_path, exist_ok=True)
        
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                
            self.models = {}
            for model_id, versions_data in data.items():
                self.models[model_id] = [ModelVersion.from_dict(v) for v in versions_data]
        else:
            self.models = {}
            self.save_registry()
            
    def save_registry(self):
        """Save registry to disk"""
        data = {}
        for model_id, versions in self.models.items():
            data[model_id] = [v.to_dict() for v in versions]
            
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def register_model(self, 
                      model_id: str,
                      model_type: str,
                      model_path: str,
                      metrics: Dict[str, float],
                      parameters: Dict[str, Any],
                      description: str = "") -> ModelVersion:
        """
        Register a new model version
        
        Args:
            model_id: Unique identifier for the model
            model_type: Type of model
            model_path: Path to the model file
            metrics: Model evaluation metrics
            parameters: Model parameters
            description: Model description
            
        Returns:
            The registered ModelVersion
        """
        if model_id not in self.models:
            self.models[model_id] = []
            new_version = "1.0.0"
        else:
            # Increment version
            latest = self.get_latest_version(model_id)
            major, minor, patch = map(int, latest.version.split('.'))
            new_version = f"{major}.{minor}.{patch+1}"
        
        # Create a timestamped directory for the model
        timestamp = int(time.time())
        version_dir = os.path.join(self.registry_path, f"{model_id}_{timestamp}")
        os.makedirs(version_dir, exist_ok=True)
        
        # Copy the model file to the versioned directory
        model_filename = os.path.basename(model_path)
        new_model_path = os.path.join(version_dir, model_filename)
        shutil.copy2(model_path, new_model_path)
        
        # Create model version
        model_version = ModelVersion(
            model_id=model_id,
            model_type=model_type,
            version=new_version,
            path=new_model_path,
            training_date=datetime.now(),
            metrics=metrics,
            parameters=parameters,
            description=description
        )
        
        self.models[model_id].append(model_version)
        self.save_registry()
        return model_version
    
    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get the latest version of a model"""
        if model_id not in self.models or not self.models[model_id]:
            return None
        
        # Sort by training date and return the newest
        return sorted(self.models[model_id], key=lambda x: x.training_date, reverse=True)[0]
    
    def get_best_version(self, model_id: str, metric: str = 'accuracy') -> Optional[ModelVersion]:
        """Get the best version of a model based on a specific metric"""
        if model_id not in self.models or not self.models[model_id]:
            return None
        
        # Filter versions that have the specified metric
        valid_versions = [v for v in self.models[model_id] if metric in v.metrics]
        if not valid_versions:
            return None
        
        # Return the version with the highest metric value
        return sorted(valid_versions, key=lambda x: x.metrics[metric], reverse=True)[0]
    
    def get_version(self, model_id: str, version: str) -> Optional[ModelVersion]:
        """Get a specific version of a model"""
        if model_id not in self.models:
            return None
        
        for v in self.models[model_id]:
            if v.version == version:
                return v
                
        return None
    
    def list_models(self) -> List[str]:
        """List all registered model IDs"""
        return list(self.models.keys())
    
    def list_versions(self, model_id: str) -> List[ModelVersion]:
        """List all versions of a specific model"""
        if model_id not in self.models:
            return []
            
        return sorted(self.models[model_id], key=lambda x: x.training_date, reverse=True)
    
    def delete_version(self, model_id: str, version: str) -> bool:
        """Delete a specific model version"""
        if model_id not in self.models:
            return False
            
        for i, v in enumerate(self.models[model_id]):
            if v.version == version:
                # Remove the model file
                if os.path.exists(v.path):
                    os.remove(v.path)
                    
                # Remove the version directory if empty
                version_dir = os.path.dirname(v.path)
                if os.path.exists(version_dir) and not os.listdir(version_dir):
                    os.rmdir(version_dir)
                    
                # Remove from registry
                self.models[model_id].pop(i)
                self.save_registry()
                return True
                
        return False
    
    def get_model_summary(self) -> Dict:
        """Get a summary of all registered models"""
        summary = {}
        for model_id, versions in self.models.items():
            latest = self.get_latest_version(model_id)
            best = self.get_best_version(model_id)
            
            summary[model_id] = {
                'versions': len(versions),
                'latest_version': latest.version if latest else None,
                'latest_date': latest.training_date.isoformat() if latest else None,
                'best_version': best.version if best else None,
                'best_metric': best.metrics.get('accuracy') if best else None
            }
            
        return summary