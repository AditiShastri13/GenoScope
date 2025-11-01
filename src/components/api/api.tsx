// API client for GenoScope FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface MutationData {
  gene: string;
  position: string;
  mutation_type: string;
  reference: string;
  alternate: string;
  impact: string;
}

export interface FileUploadResponse {
  file_id: string;
  file_name: string;
  mutations_count: number;
  preview_data: MutationData[];
  file: File; // Store the file for later prediction
}

export interface PredictionResult {
  prediction_id: string;
  file_id: string;
  has_mutation: boolean;
  disease: string;
  confidence: number;
  message: string;
  details: {
    sequence_length: number;
    gc_content: number;
    risk_level: string;
    sickle_cell?: {
      has_mutation: boolean;
      confidence: number;
      risk_level: string;
    };
    breast_cancer?: {
      has_mutation: boolean;
      confidence: number;
      risk_level: string;
    };
  };
  timestamp: string;
}

export interface UploadResponse {
  success: boolean;
  file_id: string;
  preview_data: MutationData[];
  mutations_count: number;
}

// Health check to verify backend is running
export const healthApi = {
  check: async (): Promise<{ status: string; models_loaded: boolean }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('Backend not responding');
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};

// File upload and analysis
export const fileApi = {
  uploadMutationFile: async (file: File): Promise<FileUploadResponse> => {
    try {
      // First, validate file type
      if (!file.name.endsWith('.fasta') && !file.name.endsWith('.fa') && !file.name.endsWith('.csv')) {
        throw new Error('Invalid file type. Please upload a .fasta, .fa, or .csv file');
      }

      // Read file to get preview data
      const text = await file.text();
      let sequence = '';
      
      // Parse FASTA or CSV
      if (file.name.endsWith('.fasta') || file.name.endsWith('.fa')) {
        const lines = text.split('\n');
        sequence = lines.filter(line => !line.startsWith('>')).join('').replace(/\s/g, '');
      } else {
        // For CSV, try to find sequence column
        const lines = text.split('\n');
        const headers = lines[0].toLowerCase().split(',');
        const seqIndex = headers.findIndex(h => 
          h.includes('sequence') || h.includes('dna') || h.includes('genetic')
        );
        if (seqIndex >= 0 && lines.length > 1) {
          sequence = lines[1].split(',')[seqIndex].replace(/\s/g, '');
        }
      }

      // Generate preview data from sequence
      const preview_data: MutationData[] = [];
      if (sequence.length > 100) {
        // Look for potential mutations (simplified example)
        const positions = [100, 250, 400];
        for (const pos of positions) {
          if (pos < sequence.length) {
            preview_data.push({
              gene: pos < 200 ? "HBB" : pos < 300 ? "BRCA1" : "BRCA2",
              position: `chr${pos < 200 ? '11' : '17'}:${5248000 + pos}`,
              mutation_type: "SNV",
              reference: sequence[pos] || "A",
              alternate: sequence[pos] === "A" ? "T" : sequence[pos] === "T" ? "A" : sequence[pos] === "G" ? "C" : "G",
              impact: pos < 200 ? "HIGH" : "MODERATE"
            });
          }
        }
      }

      return {
        file_id: `file_${Date.now()}`,
        file_name: file.name,
        mutations_count: Math.floor(sequence.length / 100),
        preview_data,
        file // Store file for actual prediction
      };
    } catch (error) {
      console.error('File upload error:', error);
      throw error;
    }
  }
};

// Prediction API - connects to FastAPI backend
export const predictionApi = {
  runPrediction: async (fileId: string, file: File): Promise<PredictionResult> => {
    try {
      console.log("🔧 API: Preparing FormData...");
      const formData = new FormData();
      formData.append('file', file);
      
      const url = `${API_BASE_URL}/predict/?analysis_type=comprehensive`;
      console.log("🌐 API: Sending POST to:", url);
      console.log("📄 API: File size:", file.size, "bytes");

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      console.log("📬 API: Response status:", response.status);
      
      if (!response.ok) {
        const error = await response.json();
        console.error("❌ API: Error response:", error);
        throw new Error(error.detail || 'Prediction failed');
      }

      const result = await response.json();
      console.log("📦 API: Raw backend response:", result);
      
      const predictionResult: PredictionResult = {
        prediction_id: `pred_${Date.now()}`,
        file_id: fileId,
        has_mutation: result.has_mutation,
        disease: result.disease,
        confidence: result.confidence,
        message: result.message,
        details: result.details,
        timestamp: new Date().toISOString()
      };
      
      console.log("✨ API: Formatted result:", predictionResult);
      return predictionResult;
    } catch (error) {
      console.error('❌ API: Prediction error:', error);
      throw error;
    }
  },

  analyzeDirectSequence: async (sequence: string): Promise<PredictionResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze-sequence/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sequence }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
      }

      const result = await response.json();
      
      return {
        prediction_id: `pred_${Date.now()}`,
        file_id: 'direct_sequence',
        has_mutation: result.has_mutation,
        disease: result.disease,
        confidence: result.confidence,
        message: result.message,
        details: result.details,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Direct sequence analysis error:', error);
      throw error;
    }
  },

  getPredictionHistory: async (): Promise<PredictionResult[]> => {
    // For now, get from localStorage
    const stored = localStorage.getItem('prediction_history');
    if (stored) {
      return JSON.parse(stored);
    }
    return [];
  }
};

// Model information
export const modelApi = {
  getInfo: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models/info/`);
      if (!response.ok) throw new Error('Failed to get model info');
      return await response.json();
    } catch (error) {
      console.error('Model info error:', error);
      throw error;
    }
  },

  trainDemo: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/train-demo/`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to train demo models');
      return await response.json();
    } catch (error) {
      console.error('Demo training error:', error);
      throw error;
    }
  }
};

// Auth API (simplified - no real backend auth yet)
export const authApi = {
  async login(email: string, _password: string): Promise<{ token: string; user: any }> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      token: 'demo_token',
      user: { id: '1', email, name: 'User' }
    };
  },

  async signup(name: string, email: string, _password: string): Promise<{ token: string; user: any }> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      token: 'demo_token',
      user: { id: '2', email, name }
    };
  },

  async logout(): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 500));
  }
};
