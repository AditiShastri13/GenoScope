from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles
import os
from typing import List

from .models import classifier
from .schemas import HealthCheck, PredictionResult, AnalysisRequest
from .utils import parse_fasta, parse_csv, validate_genetic_sequence

app = FastAPI(
    title="Genoscope API",
    description="Genetic Mutation Detection Tool",
    version="1.0.0"
)

# Add CORS middleware with more secure settings
# In development, we can use wide settings, but in production these should be restricted
import os

# Get environment (default to development if not set)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Set CORS settings based on environment
if ENVIRONMENT == "production":
    # More restricted settings for production
    origins = [
        "https://genoscope.example.com",  # Replace with your actual domain
        "https://app.genoscope.example.com",  # Additional trusted domains
        "http://localhost:8080"  # For local frontend server
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],  # Restrict to needed methods
        allow_headers=["Content-Type", "Authorization"],
    )
else:
    # Development settings - more permissive
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    try:
        classifier._load_models()
        print("✅ Production models loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load production models: {e}")
        print("⚠️  Training demo models as fallback...")
        classifier.train_demo_models()

@app.get("/", response_model=HealthCheck)
async def root():
    return {"status": "Genoscope API is running"}

@app.get("/health")
async def health_check():
    """
    Check if the API is running and models are loaded.
    Used by frontend to verify backend availability.
    """
    return {
        "status": "healthy",
        "models_loaded": classifier.is_trained,
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "server_time": str(import_datetime().now())
    }

def import_datetime():
    """Import datetime dynamically to avoid circular imports"""
    from datetime import datetime
    return datetime

@app.post("/predict/", response_model=PredictionResult)
async def predict_mutation(file: UploadFile = File(...), analysis_type: str = "comprehensive"):
    """
    Analyze genetic data file for mutations
    """
    try:
        # Set maximum file size (5MB)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        
        # Check if file is empty
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Empty file detected. Please upload a valid file."
            )
            
        # Validate file type
        if not (file.filename.endswith('.fasta') or 
                file.filename.endswith('.fa') or 
                file.filename.endswith('.csv')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload a file with .fasta, .fa, or .csv extension."
            )

        # Read file content with size limit
        contents = await file.read(MAX_FILE_SIZE + 1)
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds the limit of 5MB."
            )
            
        # Try to decode file content
        try:
            file_content = contents.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File encoding error. Please ensure the file contains valid text."
            )

        # Parse file based on type with error handling
        try:
            if file.filename.endswith(('.fasta', '.fa')):
                sequence = parse_fasta(file_content)
                if not sequence:
                    raise HTTPException(
                        status_code=400,
                        detail="No valid sequence found in the FASTA file. Check the format."
                    )
            else:  # CSV
                sequence = parse_csv(file_content)
                if not sequence:
                    raise HTTPException(
                        status_code=400,
                        detail="No valid sequence found in the CSV file. Ensure it has a 'sequence', 'dna_sequence', or 'genetic_sequence' column."
                    )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error parsing file: {str(e)}"
            )

        # Validate sequence
        if not sequence or not isinstance(sequence, str):
            raise HTTPException(
                status_code=400,
                detail="Invalid sequence format. Expected a string of nucleotides."
            )
            
        if not validate_genetic_sequence(sequence):
            raise HTTPException(
                status_code=400,
                detail="Invalid genetic sequence. Sequence should contain only A, T, C, G characters."
            )

        if len(sequence) < 50:
            raise HTTPException(
                status_code=400,
                detail="Sequence too short. Minimum length is 50 characters."
            )
            
        # Practical maximum sequence length check
        if len(sequence) > 1000000:  # 1 million bases
            raise HTTPException(
                status_code=400,
                detail="Sequence too long. Maximum supported length is 1,000,000 characters."
            )

        # Analyze for both diseases
        sickle_cell_pred, sickle_cell_prob = classifier.predict(sequence, "sickle_cell")
        breast_cancer_pred, breast_cancer_prob = classifier.predict(sequence, "breast_cancer")

        # Calculate GC content
        gc_content = round((sequence.count('G') + sequence.count('C')) / len(sequence), 3)
        
        # Prepare sickle cell results (convert to percentage)
        sickle_cell_risk = "high" if sickle_cell_prob > 0.8 else "moderate" if sickle_cell_prob > 0.5 else "low"
        sickle_cell_results = {
            "has_mutation": bool(sickle_cell_pred == 1),
            "confidence": round(sickle_cell_prob * 100, 1),  # Convert to percentage
            "risk_level": sickle_cell_risk
        }
        
        # Prepare breast cancer results (convert to percentage)
        breast_cancer_risk = "high" if breast_cancer_prob > 0.8 else "moderate" if breast_cancer_prob > 0.5 else "low"
        breast_cancer_results = {
            "has_mutation": bool(breast_cancer_pred == 1),
            "confidence": round(breast_cancer_prob * 100, 1),  # Convert to percentage
            "risk_level": breast_cancer_risk
        }

        # Determine primary result (whichever has higher confidence)
        if sickle_cell_pred == 1 and sickle_cell_prob > breast_cancer_prob:
            primary_disease = "Sickle Cell Anemia"
            primary_confidence = round(sickle_cell_prob * 100, 1)  # Percentage
            primary_has_mutation = True
            message = f"Mutation detected associated with Sickle Cell Anemia (Confidence: {sickle_cell_prob*100:.1f}%). HBB gene variant likely present."
            risk_level = sickle_cell_risk
        elif breast_cancer_pred == 1 and breast_cancer_prob > sickle_cell_prob:
            primary_disease = "Breast Cancer"
            primary_confidence = round(breast_cancer_prob * 100, 1)  # Percentage
            primary_has_mutation = True
            message = f"Mutation detected associated with Breast Cancer (Confidence: {breast_cancer_prob*100:.1f}%). BRCA1/BRCA2 or related gene variant likely present."
            risk_level = breast_cancer_risk
        elif sickle_cell_pred == 1:
            primary_disease = "Sickle Cell Anemia"
            primary_confidence = round(sickle_cell_prob * 100, 1)  # Percentage
            primary_has_mutation = True
            message = f"Mutation detected associated with Sickle Cell Anemia (Confidence: {sickle_cell_prob*100:.1f}%). HBB gene variant likely present."
            risk_level = sickle_cell_risk
        elif breast_cancer_pred == 1:
            primary_disease = "Breast Cancer"
            primary_confidence = round(breast_cancer_prob * 100, 1)  # Percentage
            primary_has_mutation = True
            message = f"Mutation detected associated with Breast Cancer (Confidence: {breast_cancer_prob*100:.1f}%). BRCA1/BRCA2 or related gene variant likely present."
            risk_level = breast_cancer_risk
        else:
            primary_disease = "None"
            primary_confidence = round(max(sickle_cell_prob, breast_cancer_prob) * 100, 1)  # Percentage
            primary_has_mutation = False
            message = f"No known mutations detected for the analyzed diseases. Sickle Cell: {sickle_cell_prob*100:.1f}%, Breast Cancer: {breast_cancer_prob*100:.1f}%"
            risk_level = "low"

        return PredictionResult(
            has_mutation=primary_has_mutation,
            disease=primary_disease,
            confidence=primary_confidence,
            message=message,
            details={
                "sequence_length": len(sequence),
                "gc_content": gc_content,
                "risk_level": risk_level,
                "sickle_cell": sickle_cell_results,
                "breast_cancer": breast_cancer_results
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/train-demo/")
async def train_demo_models():
    """
    Train demo models with synthetic data
    """
    try:
        classifier.train_demo_models()
        model_info = classifier.get_model_info()
        return {
            "message": "Demo models trained successfully", 
            "status": "success",
            "models": model_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")
        
@app.get("/models/info/")
async def get_model_info():
    """
    Get information about the currently loaded models
    """
    try:
        model_info = classifier.get_model_info()
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model information: {str(e)}")
        
@app.post("/predict/{disease_type}/{version}/")
async def predict_with_version(
    file: UploadFile = File(...),
    disease_type: str = None,
    version: str = None
):
    """
    Analyze genetic data using a specific model version
    """
    try:
        if disease_type not in ["sickle_cell", "breast_cancer"]:
            raise HTTPException(status_code=400, detail="Invalid disease type. Must be 'sickle_cell' or 'breast_cancer'")
            
        # Validate file type
        if not (file.filename.endswith('.fasta') or 
                file.filename.endswith('.fa') or 
                file.filename.endswith('.csv')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload FASTA or CSV."
            )

        # Set maximum file size (5MB)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        
        # Read file content with size limit
        contents = await file.read(MAX_FILE_SIZE + 1)
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds the limit of 5MB."
            )
            
        # Decode file content
        try:
            file_content = contents.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File encoding error. Please ensure the file contains valid text."
            )

        # Parse file based on type
        try:
            if file.filename.endswith(('.fasta', '.fa')):
                sequence = parse_fasta(file_content)
            else:  # CSV
                sequence = parse_csv(file_content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

        # Validate sequence
        if not validate_genetic_sequence(sequence):
            raise HTTPException(
                status_code=400,
                detail="Invalid genetic sequence. Sequence should contain only valid nucleotides."
            )

        # Analyze with specific model version
        result = classifier.predict_with_version(sequence, disease_type, version)
        
        return {
            "sequence_length": len(sequence),
            "gc_content": round((sequence.count('G') + sequence.count('C')) / len(sequence), 3),
            "prediction": result["prediction"],
            "probability": result["probability"],
            "model_version": result["model_version"],
            "model_date": result["model_date"],
            "model_type": result["model_type"],
            "disease_type": disease_type,
            "has_mutation": bool(result["prediction"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/analyze-sequence/")
async def analyze_direct_sequence(request: AnalysisRequest):
    """
    Analyze a genetic sequence directly (without file upload)
    """
    try:
        if not request.sequence:
            raise HTTPException(
                status_code=400, 
                detail="Missing sequence. Please provide a genetic sequence for analysis."
            )
        
        sequence = request.sequence.strip()
        
        # Validate sequence
        if not validate_genetic_sequence(sequence):
            raise HTTPException(
                status_code=400, 
                detail="Invalid genetic sequence. Sequence should contain only valid nucleotides (A, T, C, G)."
            )
        
        if len(sequence) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Sequence too short. Minimum length is 50 characters."
            )
            
        if len(sequence) > 1000000:  # 1 million bases
            raise HTTPException(
                status_code=400,
                detail="Sequence too long. Maximum supported length is 1,000,000 characters."
            )
        
        # Analyze sequence for both diseases
        sickle_cell_pred, sickle_cell_prob = classifier.predict(sequence, "sickle_cell")
        breast_cancer_pred, breast_cancer_prob = classifier.predict(sequence, "breast_cancer")
        
        # Calculate sequence metrics
        gc_content = round((sequence.count('G') + sequence.count('C')) / len(sequence), 3)
        
        # Return comprehensive results
        return PredictionResult(
            has_mutation=bool(sickle_cell_pred == 1 or breast_cancer_pred == 1),
            disease="Sickle Cell Anemia" if (sickle_cell_pred == 1 and sickle_cell_prob > breast_cancer_prob) else 
                   "Breast Cancer" if breast_cancer_pred == 1 else "None",
            confidence=round(max(sickle_cell_prob if sickle_cell_pred == 1 else 0, 
                                breast_cancer_prob if breast_cancer_pred == 1 else 0), 3),
            message="Analysis completed successfully.",
            details={
                "sequence_length": len(sequence),
                "gc_content": gc_content,
                "sickle_cell": {
                    "has_mutation": bool(sickle_cell_pred),
                    "confidence": round(sickle_cell_prob, 3),
                    "risk_level": "high" if sickle_cell_prob > 0.8 else 
                                 "moderate" if sickle_cell_prob > 0.5 else "low"
                },
                "breast_cancer": {
                    "has_mutation": bool(breast_cancer_pred),
                    "confidence": round(breast_cancer_prob, 3),
                    "risk_level": "high" if breast_cancer_prob > 0.8 else 
                                 "moderate" if breast_cancer_prob > 0.5 else "low"
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sequence: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
