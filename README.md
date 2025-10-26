# Genoscope - Genomic Sequence Analysis Tool

Genoscope is an advanced genomic sequence analysis application that helps detect genetic markers for various medical conditions. This tool combines machine learning with genetic sequence analysis to provide insights from FASTA or direct sequence inputs.

## Features

- **Genetic Sequence Analysis**: Process FASTA files or direct DNA sequences
- **Multiple Analysis Models**: Specialized models for different genetic conditions:
  - Sickle Cell Anemia detection
  - Breast Cancer marker detection
  - More models can be added through the extensible architecture
- **Model Versioning**: Track and manage different versions of prediction models
- **Interactive UI**: User-friendly interface for uploading and analyzing sequences
- **RESTful API**: Backend API for integration with other systems

## Application Structure

```
genoscope/
├── backend/               # FastAPI backend
│   ├── app/               # Core application code
│   │   ├── data/          # Data handling modules
│   │   ├── models/        # ML model definitions
│   │   └── utils/         # Helper utilities
│   ├── trained_models/    # Saved ML models
│   └── run_app.py         # Backend entry point
├── frontend/              # Web interface
│   ├── app.js             # Frontend logic
│   ├── enhanced-app.js    # Enhanced frontend with additional features
│   ├── index.html         # HTML interface
│   └── styles.css         # CSS styling
├── run_genoscope.bat      # Windows batch file to run backend
├── run_frontend.bat       # Windows batch file to run frontend
└── deployment.md          # Deployment instructions
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Modern web browser
- Internet connection (for CDN resources)

### Running the Backend

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/genoscope.git
   cd genoscope
   ```

2. On Windows, use the batch file:
   ```
   run_genoscope.bat
   ```

   Alternatively, run the commands manually:
   ```
   cd backend
   pip install -r requirements.txt
   pip install -e .
   python run_app.py
   ```

   The API will be available at http://localhost:8000

### Running the Frontend

1. On Windows, use the batch file:
   ```
   run_frontend.bat
   ```

   Alternatively, run:
   ```
   cd frontend
   python -m http.server 8080
   ```

   The UI will be available at http://localhost:8080

## Using the Application

1. **Upload a FASTA file**:
   - Go to the "File Upload" tab
   - Select a FASTA file containing genetic sequences
   - Choose the target disease model
   - Click "Analyze Sequence"

2. **Enter a direct sequence**:
   - Go to the "Direct Sequence" tab
   - Paste the DNA sequence (A, T, G, C nucleotides)
   - Choose the target disease model
   - Click "Analyze Sequence"

3. **View Model Information**:
   - Go to the "Model Info" tab to view available model versions
   - Train new demo models with the "Train Demo Models" button

## API Endpoints

### Prediction Endpoints

- `POST /predict/?analysis_type={disease_type}` - Analyze genetic sequence file
- `POST /analyze-sequence/` - Analyze direct sequence input

### Model Management

- `GET /models/info/` - Get information about available models
- `POST /train-demo/` - Train new demo models

Detailed API documentation is available at http://localhost:8000/docs when the backend is running.

## Development

### Backend Development

The backend is built with FastAPI and uses scikit-learn for machine learning models. Key modules:

- `app/main.py` - API routes and server configuration
- `app/models.py` - Machine learning model definitions
- `app/feature_extraction.py` - DNA sequence feature extraction
- `app/model_versioning.py` - Model version management

### Frontend Development

The frontend uses vanilla JavaScript with a modern CSS design:

- `app.js` - Base frontend functionality
- `enhanced-app.js` - Enhanced version with improved error handling and UI features
- `styles.css` - Base styling
- `enhanced-styles.css` - Enhanced styling with animations and responsive design

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- FastAPI for the backend framework
- Scikit-learn for machine learning models
- Font Awesome for icons