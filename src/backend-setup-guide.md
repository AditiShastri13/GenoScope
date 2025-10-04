# Python Backend Setup Guide for GenoScope

This guide explains how to set up a Python backend to work with the GenoScope frontend.

## Recommended Stack

### Option 1: Django + Django REST Framework
```bash
# Install Django
pip install django djangorestframework django-cors-headers
pip install pandas scikit-learn tensorflow  # For ML processing
pip install celery redis  # For background tasks
pip install reportlab  # For PDF generation
pip install pillow  # For image processing
```

### Option 2: Flask + Flask-RESTful
```bash
# Install Flask
pip install flask flask-restful flask-cors
pip install pandas scikit-learn tensorflow
pip install celery redis
pip install reportlab
pip install flask-jwt-extended  # For authentication
```

## Project Structure

```
genescope-backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── mutation.py
│   │   └── prediction.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── mutations.py
│   │   ├── predictions.py
│   │   └── reports.py
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── preprocessing.py
│   │   └── prediction_engine.py
│   └── utils/
│       ├── __init__.py
│       ├── csv_parser.py
│       └── pdf_generator.py
├── requirements.txt
├── config.py
└── run.py
```

## Key API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user

### File Upload & Processing
- `POST /api/mutations/upload/` - Upload CSV file
- `GET /api/mutations/files/` - List uploaded files
- `DELETE /api/mutations/files/{id}/` - Delete file

### ML Predictions
- `POST /api/predictions/analyze/` - Run ML analysis
- `GET /api/predictions/history/` - Get prediction history
- `GET /api/predictions/{id}/` - Get specific prediction

### Reports
- `GET /api/reports/pdf/{prediction_id}/` - Generate PDF report
- `POST /api/reports/share/` - Share report via email

## Sample Django Model

```python
# models/prediction.py
from django.db import models
from django.contrib.auth.models import User

class MutationFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True)
    mutations_count = models.IntegerField()

class Prediction(models.Model):
    mutation_file = models.ForeignKey(MutationFile, on_delete=models.CASCADE)
    predicted_disease = models.CharField(max_length=255)
    confidence_score = models.FloatField()
    key_mutation = models.CharField(max_length=255)
    analysis_date = models.DateTimeField(auto_now_add=True)
    results_json = models.JSONField()  # Store detailed results

class Mutation(models.Model):
    mutation_file = models.ForeignKey(MutationFile, on_delete=models.CASCADE)
    gene = models.CharField(max_length=50)
    mutation = models.CharField(max_length=255)
    consequence = models.CharField(max_length=100)
    pathogenicity = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
```

## Sample ML Processing

```python
# ml/prediction_engine.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

class GeneticPredictionEngine:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load pre-trained ML model"""
        try:
            self.model = joblib.load('models/genetic_classifier.pkl')
        except:
            # Train a new model if none exists
            self.train_model()
    
    def preprocess_mutations(self, mutations_df):
        """Convert genetic mutations to ML features"""
        # Feature engineering for genetic data
        features = []
        for _, row in mutations_df.iterrows():
            # Extract features from mutation data
            gene_encoding = self.encode_gene(row['gene'])
            mutation_encoding = self.encode_mutation(row['mutation'])
            pathogenicity_score = self.encode_pathogenicity(row['pathogenicity'])
            
            features.append([gene_encoding, mutation_encoding, pathogenicity_score])
        
        return np.array(features)
    
    def predict_disease_risk(self, mutations_df):
        """Predict disease risk from mutations"""
        features = self.preprocess_mutations(mutations_df)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(features)
        
        # Calculate overall risk scores
        disease_risks = {
            'Breast Cancer': float(np.max(probabilities[:, 0])),
            'Ovarian Cancer': float(np.max(probabilities[:, 1])),
            'Colorectal Cancer': float(np.max(probabilities[:, 2])),
            # Add more diseases...
        }
        
        # Find highest risk disease
        predicted_disease = max(disease_risks.keys(), key=lambda k: disease_risks[k])
        confidence = disease_risks[predicted_disease] * 100
        
        return {
            'predicted_disease': predicted_disease,
            'confidence_score': confidence,
            'disease_probabilities': disease_risks,
            'key_mutations': self.identify_key_mutations(mutations_df, features)
        }
```

## Frontend Integration

The frontend is already set up to work with these endpoints. Key integration points:

1. **Authentication**: Uses JWT tokens stored in localStorage
2. **File Upload**: Sends CSV files to `/api/mutations/upload/`
3. **Real-time Updates**: Can be enhanced with WebSockets for live progress
4. **Error Handling**: Toast notifications for API errors

## Environment Variables

Create a `.env` file:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/genescope
REDIS_URL=redis://localhost:6379
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Deployment Considerations

1. **Database**: PostgreSQL for production, SQLite for development
2. **File Storage**: AWS S3 or similar for uploaded CSV files
3. **ML Models**: Store trained models in cloud storage
4. **Background Tasks**: Use Celery with Redis for ML processing
5. **API Rate Limiting**: Implement to prevent abuse
6. **Security**: HTTPS, proper CORS, input validation

## Getting Started

1. Clone/create the backend repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up database: `python manage.py migrate` (Django)
4. Create superuser: `python manage.py createsuperuser` (Django)
5. Run development server: `python manage.py runserver` (Django)
6. Start Celery worker: `celery -A app worker -l info`

The frontend will automatically connect to `http://localhost:8000/api` by default.