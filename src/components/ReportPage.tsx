import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Navigation } from "./Navigation";
import { FileText, Download, Share2, AlertTriangle, CheckCircle, Dna, Activity, Info } from "lucide-react";
import { PredictionResult } from "./api/api";

interface ReportPageProps {
  onNavigate: (page: string) => void;
}

export function ReportPage({ onNavigate }: ReportPageProps) {
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);

  useEffect(() => {
    // Load the latest prediction from localStorage
    console.log("📖 ReportPage: Loading prediction from localStorage...");
    const stored = localStorage.getItem('latest_prediction');
    console.log("💾 ReportPage: Raw stored data:", stored);
    
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        console.log("✅ ReportPage: Parsed prediction:", parsed);
        console.log("   - Disease:", parsed.disease);
        console.log("   - Confidence:", parsed.confidence);
        console.log("   - Has Mutation:", parsed.has_mutation);
        console.log("   - Details:", parsed.details);
        setPrediction(parsed);
      } catch (error) {
        console.error("❌ ReportPage: Failed to parse prediction:", error);
      }
    } else {
      console.warn("⚠️ ReportPage: No prediction found in localStorage");
    }
  }, []);

  if (!prediction) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation currentPage="reports" onNavigate={onNavigate} />
        <div className="max-w-7xl mx-auto p-6">
          <Card className="border-0 shadow-lg">
            <CardContent className="p-12 text-center space-y-4">
              <AlertTriangle className="w-16 h-16 mx-auto text-orange-500" />
              <h2 className="text-2xl font-semibold">No Prediction Results</h2>
              <p className="text-muted-foreground">
                Please upload a file and run prediction first.
              </p>
              <Button 
                onClick={() => onNavigate('upload')}
                className="bg-accent hover:bg-accent/90"
              >
                Go to Upload Page
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Get risk level color
  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'moderate': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Backend now returns confidence as percentage (0-100), not probability (0-1)
  const confidencePercent = prediction.confidence.toFixed(1);

  return (
    <div className="min-h-screen bg-background">
      <Navigation currentPage="reports" onNavigate={onNavigate} />
      
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl text-primary flex items-center gap-3">
              📄 Prediction Report
            </h1>
            <p className="text-muted-foreground mt-2">AI-Powered Genetic Analysis Results</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              Share Report
            </Button>
            <Button className="bg-accent hover:bg-accent/90 flex items-center gap-2">
              <Download className="w-4 h-4" />
              Download PDF
            </Button>
          </div>
        </div>

        {/* Main Result Card */}
        <Card className="border-0 shadow-2xl">
          <CardHeader className="bg-gradient-to-r from-primary/10 to-accent/10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                {prediction.has_mutation ? (
                  <div className="p-4 bg-red-100 rounded-full flex-shrink-0">
                    <AlertTriangle className="w-8 h-8 text-red-600" />
                  </div>
                ) : (
                  <div className="p-4 bg-green-100 rounded-full flex-shrink-0">
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                )}
                <div>
                  <CardTitle className="text-2xl md:text-3xl">
                    {prediction.has_mutation ? "🔬 Positive Detection" : "✅ Negative Detection"}
                  </CardTitle>
                  <p className="text-base md:text-lg mt-2 text-muted-foreground">
                    <strong>Analysis:</strong> {prediction.disease}
                  </p>
                  <p className="text-sm md:text-base mt-1 text-muted-foreground">
                    {prediction.message}
                  </p>
                </div>
              </div>
              <div className="text-center md:text-right flex-shrink-0">
                <p className="text-sm text-muted-foreground">Primary Confidence</p>
                <p className="text-4xl md:text-5xl font-bold text-primary">{confidencePercent}%</p>
                <Badge className={getRiskColor(prediction.details.risk_level) + " mt-2"}>
                  {prediction.details.risk_level.toUpperCase()} RISK
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-6 space-y-6">

            {/* Sequence Details */}
            <Card className="border-accent/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Dna className="w-5 h-5" />
                  Sequence Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Sequence Length</p>
                  <p className="text-2xl font-semibold">{prediction.details.sequence_length.toLocaleString()} bp</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">GC Content</p>
                  <p className="text-2xl font-semibold">{(prediction.details.gc_content * 100).toFixed(1)}%</p>
                  <Progress value={prediction.details.gc_content * 100} className="mt-2" />
                </div>
              </CardContent>
            </Card>

            {/* Disease-Specific Results */}
            {prediction.details.sickle_cell && prediction.details.breast_cancer && (
              <Card className="border-primary/30 bg-gradient-to-br from-primary/5 to-accent/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-xl">
                    <Activity className="w-6 h-6" />
                    Disease Prediction Confidence Scores
                  </CardTitle>
                  <CardDescription className="text-base">
                    Individual confidence analysis for each disease type
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Sickle Cell Analysis */}
                  <div className="p-6 border-2 rounded-lg bg-white shadow-sm">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-full ${prediction.details.sickle_cell.has_mutation ? 'bg-red-100' : 'bg-green-100'}`}>
                          <Dna className={`w-7 h-7 ${prediction.details.sickle_cell.has_mutation ? 'text-red-600' : 'text-green-600'}`} />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold">Sickle Cell Anemia</h3>
                          <p className="text-muted-foreground">HBB Gene Analysis (Chr 11)</p>
                          <p className="text-sm mt-1">
                            {prediction.details.sickle_cell.has_mutation 
                              ? "✓ Mutation markers detected" 
                              : "✓ No mutations detected"}
                          </p>
                        </div>
                      </div>
                      <div className="text-center md:text-right">
                        <p className="text-4xl font-bold text-primary">
                          {prediction.details.sickle_cell.confidence.toFixed(1)}%
                        </p>
                        <Badge className={getRiskColor(prediction.details.sickle_cell.risk_level) + " mt-2 text-sm"}>
                          {prediction.details.sickle_cell.risk_level.toUpperCase()} RISK
                        </Badge>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Confidence Level</span>
                        <span className="font-semibold">{prediction.details.sickle_cell.confidence.toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={prediction.details.sickle_cell.confidence} 
                        className="h-3"
                      />
                    </div>
                  </div>

                  {/* Breast Cancer Analysis */}
                  <div className="p-6 border-2 rounded-lg bg-white shadow-sm">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-full ${prediction.details.breast_cancer.has_mutation ? 'bg-red-100' : 'bg-green-100'}`}>
                          <Dna className={`w-7 h-7 ${prediction.details.breast_cancer.has_mutation ? 'text-red-600' : 'text-green-600'}`} />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold">Breast Cancer</h3>
                          <p className="text-muted-foreground">BRCA1/BRCA2 Gene Analysis (Chr 17)</p>
                          <p className="text-sm mt-1">
                            {prediction.details.breast_cancer.has_mutation 
                              ? "✓ Mutation markers detected" 
                              : "✓ No mutations detected"}
                          </p>
                        </div>
                      </div>
                      <div className="text-center md:text-right">
                        <p className="text-4xl font-bold text-primary">
                          {prediction.details.breast_cancer.confidence.toFixed(1)}%
                        </p>
                        <Badge className={getRiskColor(prediction.details.breast_cancer.risk_level) + " mt-2 text-sm"}>
                          {prediction.details.breast_cancer.risk_level.toUpperCase()} RISK
                        </Badge>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Confidence Level</span>
                        <span className="font-semibold">{prediction.details.breast_cancer.confidence.toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={prediction.details.breast_cancer.confidence} 
                        className="h-3"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Model Information */}
            <Card className="bg-muted/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Info className="w-4 h-4" />
                  Analysis Information
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Model Version:</span>
                  <span className="font-medium">GenoScope v1.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Analysis Type:</span>
                  <span className="font-medium">Comprehensive Genetic Screening</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Prediction ID:</span>
                  <span className="font-mono text-xs">{prediction.prediction_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">File ID:</span>
                  <span className="font-mono text-xs">{prediction.file_id}</span>
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-center pt-4">
              <Button 
                variant="outline" 
                onClick={() => onNavigate('upload')}
                className="flex items-center gap-2"
              >
                <FileText className="w-4 h-4" />
                Analyze Another File
              </Button>
              <Button 
                onClick={() => onNavigate('dashboard')}
                className="bg-primary hover:bg-primary/90 flex items-center gap-2"
              >
                Return to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Clinical Recommendations */}
        {prediction.has_mutation && (
          <Card className="border-orange-200 bg-orange-50/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-800">
                <AlertTriangle className="w-5 h-5" />
                Clinical Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p className="text-orange-900">
                ⚠️ <strong>Important:</strong> This analysis is for research and educational purposes only.
              </p>
              <ul className="list-disc list-inside space-y-2 text-orange-800">
                <li>Consult with a qualified geneticist or healthcare provider</li>
                <li>Consider confirmatory testing through clinical genetic testing</li>
                <li>Discuss family history and genetic counseling options</li>
                <li>Do not make medical decisions based solely on this analysis</li>
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}