// Mock API service that simulates calls to a Python backend
// In production, these would call your Django/Flask endpoints

const API_BASE_URL = 'http://localhost:8000/api';

// Mock response data structures that match what a Python backend would return
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface MutationData {
  gene: string;
  mutation: string;
  consequence: string;
  pathogenicity: string;
  notes?: string;
}

export interface PredictionResult {
  id: string;
  file_name: string;
  upload_date: string;
  predicted_disease: string;
  confidence_score: number;
  key_mutation: string;
  mutations_count: number;
  mutations: MutationData[];
  disease_probabilities: Array<{
    disease: string;
    confidence: number;
  }>;
  mutation_distribution: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
}

export interface UploadResponse {
  success: boolean;
  file_id: string;
  preview_data: MutationData[];
  mutations_count: number;
}

// Mock API functions that would call your Python backend
export const authApi = {
  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    // POST /api/auth/login/
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
    return {
      token: 'mock_jwt_token_here',
      user: {
        id: '1',
        email,
        name: 'Dr. Smith',
        created_at: '2024-01-01T00:00:00Z'
      }
    };
  },

  async signup(name: string, email: string, password: string): Promise<{ token: string; user: User }> {
    // POST /api/auth/register/
    await new Promise(resolve => setTimeout(resolve, 1200));
    return {
      token: 'mock_jwt_token_here',
      user: {
        id: '2',
        email,
        name,
        created_at: new Date().toISOString()
      }
    };
  },

  async logout(): Promise<void> {
    // POST /api/auth/logout/
    await new Promise(resolve => setTimeout(resolve, 500));
  }
};

export const fileApi = {
  async uploadMutationFile(file: File): Promise<UploadResponse> {
    // POST /api/mutations/upload/
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const mockPreviewData: MutationData[] = [
      { gene: "BRCA1", mutation: "c.68_69delAG", consequence: "Frameshift", pathogenicity: "Pathogenic" },
      { gene: "TP53", mutation: "c.524G>A", consequence: "Missense", pathogenicity: "Likely Pathogenic" },
      { gene: "PTEN", mutation: "c.697C>T", consequence: "Nonsense", pathogenicity: "Pathogenic" },
      { gene: "ATM", mutation: "c.5932C>T", consequence: "Missense", pathogenicity: "VUS" },
      { gene: "CHEK2", mutation: "c.1100delC", consequence: "Frameshift", pathogenicity: "Pathogenic" }
    ];

    return {
      success: true,
      file_id: 'file_' + Date.now(),
      preview_data: mockPreviewData,
      mutations_count: 342
    };
  }
};

export const predictionApi = {
  async runPrediction(fileId: string): Promise<PredictionResult> {
    // POST /api/predictions/analyze/
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    return {
      id: 'pred_' + Date.now(),
      file_name: 'patient_mutations.csv',
      upload_date: new Date().toISOString(),
      predicted_disease: 'Breast Cancer',
      confidence_score: 94.7,
      key_mutation: 'BRCA1 c.68_69delAG',
      mutations_count: 342,
      mutations: [
        {
          gene: "BRCA1",
          mutation: "c.68_69delAG",
          consequence: "Frameshift",
          pathogenicity: "Pathogenic",
          notes: "High penetrance breast/ovarian cancer risk"
        },
        {
          gene: "TP53",
          mutation: "c.524G>A",
          consequence: "Missense",
          pathogenicity: "Likely Pathogenic",
          notes: "Li-Fraumeni syndrome associated"
        },
        {
          gene: "PTEN",
          mutation: "c.697C>T",
          consequence: "Nonsense",
          pathogenicity: "Pathogenic",
          notes: "Cowden syndrome predisposition"
        },
        {
          gene: "ATM",
          mutation: "c.5932C>T",
          consequence: "Missense",
          pathogenicity: "VUS",
          notes: "Uncertain clinical significance"
        },
        {
          gene: "CHEK2",
          mutation: "c.1100delC",
          consequence: "Frameshift",
          pathogenicity: "Pathogenic",
          notes: "Moderate breast cancer risk"
        }
      ],
      disease_probabilities: [
        { disease: 'Breast Cancer', confidence: 94.7 },
        { disease: 'Ovarian Cancer', confidence: 78.2 },
        { disease: 'Colorectal Cancer', confidence: 43.1 },
        { disease: 'Prostate Cancer', confidence: 22.8 },
        { disease: 'Lung Cancer', confidence: 18.5 }
      ],
      mutation_distribution: [
        { type: 'SNP', count: 222, percentage: 65 },
        { type: 'Indel', count: 86, percentage: 25 },
        { type: 'Deletion', count: 34, percentage: 10 }
      ]
    };
  },

  async getPredictionHistory(): Promise<PredictionResult[]> {
    // GET /api/predictions/history/
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return [
      {
        id: 'pred_1',
        file_name: 'patient_001_mutations.csv',
        upload_date: '2025-01-15T10:30:00Z',
        predicted_disease: 'Breast Cancer',
        confidence_score: 94.7,
        key_mutation: 'BRCA1 c.68_69delAG',
        mutations_count: 342,
        mutations: [],
        disease_probabilities: [],
        mutation_distribution: []
      },
      {
        id: 'pred_2',
        file_name: 'sample_genetic_data.csv',
        upload_date: '2025-01-14T15:45:00Z',
        predicted_disease: "Alzheimer's Disease",
        confidence_score: 87.3,
        key_mutation: 'APOE ε4/ε4',
        mutations_count: 156,
        mutations: [],
        disease_probabilities: [],
        mutation_distribution: []
      }
    ];
  }
};

export const reportsApi = {
  async generatePDF(predictionId: string): Promise<Blob> {
    // GET /api/reports/pdf/{predictionId}/
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // In a real app, this would return the actual PDF blob from your Python backend
    return new Blob(['Mock PDF content'], { type: 'application/pdf' });
  },

  async shareReport(predictionId: string, email: string): Promise<{ success: boolean }> {
    // POST /api/reports/share/
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return { success: true };
  }
};

// Python Backend Structure Comments:
/*
Python Backend (Django/Flask) would have these endpoints:

1. Authentication (Django REST Framework or Flask-JWT):
   - POST /api/auth/register/
   - POST /api/auth/login/
   - POST /api/auth/logout/
   - GET /api/auth/user/

2. File Upload (with pandas for CSV processing):
   - POST /api/mutations/upload/
   - GET /api/mutations/files/
   - DELETE /api/mutations/files/{id}/

3. ML Predictions (scikit-learn, TensorFlow, PyTorch):
   - POST /api/predictions/analyze/
   - GET /api/predictions/history/
   - GET /api/predictions/{id}/

4. Reports (ReportLab for PDF generation):
   - GET /api/reports/pdf/{prediction_id}/
   - POST /api/reports/share/

5. Dashboard Statistics:
   - GET /api/dashboard/stats/

Key Python Libraries:
- Django/Flask for web framework
- pandas for CSV processing
- scikit-learn/TensorFlow for ML
- ReportLab for PDF generation
- celery for background tasks
- PostgreSQL/MongoDB for database
*/