import { useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Navigation } from "./Navigation";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { fileApi, predictionApi, MutationData } from "./api/mockApi";
import { toast } from "sonner@2.0.3";
import { Upload, CloudUpload, Dna, FileText, TrendingUp, ArrowRight, Check } from "lucide-react";

interface UploadPageProps {
  onNavigate: (page: string) => void;
}

export function UploadPage({ onNavigate }: UploadPageProps) {
  const [isUploaded, setIsUploaded] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fileId, setFileId] = useState<string>("");
  const [fileName, setFileName] = useState<string>("");
  const [previewData, setPreviewData] = useState<MutationData[]>([]);
  const [mutationsCount, setMutationsCount] = useState<number>(0);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error("Please upload a CSV file");
      return;
    }

    try {
      const response = await fileApi.uploadMutationFile(file);
      setFileId(response.file_id);
      setFileName(file.name);
      setPreviewData(response.preview_data);
      setMutationsCount(response.mutations_count);
      setIsUploaded(true);
      toast.success("File uploaded successfully!");
    } catch (error) {
      toast.error("Failed to upload file. Please try again.");
    }
  };

  const handleRunPrediction = async () => {
    if (!fileId) return;

    setIsProcessing(true);
    try {
      const result = await predictionApi.runPrediction(fileId);
      toast.success("Analysis complete!");
      // Store result for report page (in a real app, this would be handled by state management)
      localStorage.setItem('latest_prediction', JSON.stringify(result));
      onNavigate('reports');
    } catch (error) {
      toast.error("Prediction failed. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const workflowSteps = [
    { step: "Upload", icon: Upload, description: "Upload your CSV file" },
    { step: "Process", icon: Dna, description: "Analyze mutations" },
    { step: "Predict", icon: TrendingUp, description: "Generate predictions" }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation currentPage="upload" onNavigate={onNavigate} />
      
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Page Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl text-primary">📤 Upload Your Mutation Data</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your genetic mutation data in CSV format to get instant disease risk predictions
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Upload Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Box */}
            <Card className="border-2 border-dashed border-muted-foreground/25 hover:border-accent transition-colors">
              <CardContent className="p-12">
                {!isUploaded ? (
                  <div className="text-center space-y-6">
                    <div className="flex items-center justify-center">
                      <div className="p-6 bg-accent/10 rounded-full">
                        <CloudUpload className="w-12 h-12 text-accent" />
                        <Dna className="w-8 h-8 text-primary -mt-4 ml-8" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl mb-2">Drop your CSV here or Browse Files</h3>
                      <p className="text-muted-foreground mb-4">Supported formats: .csv only</p>
                      <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileUpload}
                        className="hidden"
                        id="file-upload"
                      />
                      <Button 
                        onClick={() => document.getElementById('file-upload')?.click()}
                        className="bg-accent hover:bg-accent/90"
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Browse Files
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center space-y-4">
                    <div className="flex items-center justify-center">
                      <div className="p-4 bg-green-100 rounded-full">
                        <Check className="w-8 h-8 text-green-600" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl text-green-600">File Uploaded Successfully!</h3>
                      <p className="text-muted-foreground">{fileName} ({mutationsCount} mutations detected)</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Preview Table */}
            {isUploaded && (
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Data Preview
                  </CardTitle>
                  <CardDescription>
                    First 5 rows of your uploaded data
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Gene</TableHead>
                        <TableHead>Mutation</TableHead>
                        <TableHead>Consequence</TableHead>
                        <TableHead>Pathogenicity</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {previewData.map((row, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-mono">{row.gene}</TableCell>
                          <TableCell className="font-mono text-sm">{row.mutation}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{row.consequence}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge 
                              className={
                                row.pathogenicity === 'Pathogenic' 
                                  ? 'bg-red-100 text-red-800 border-red-200'
                                  : row.pathogenicity === 'Likely Pathogenic'
                                  ? 'bg-orange-100 text-orange-800 border-orange-200'
                                  : 'bg-gray-100 text-gray-800 border-gray-200'
                              }
                            >
                              {row.pathogenicity}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            )}

            {/* Run Prediction Button */}
            {isUploaded && (
              <div className="text-center">
                <Button 
                  size="lg" 
                  className="bg-accent hover:bg-accent/90 text-lg px-8 py-4"
                  onClick={handleRunPrediction}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      🔮 Run Prediction
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* How it Works */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>How It Works</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {workflowSteps.map((step, index) => {
                  const Icon = step.icon;
                  return (
                    <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                      <div className="p-2 bg-primary/10 rounded-full">
                        <Icon className="w-4 h-4 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-medium">{step.step}</h4>
                        <p className="text-sm text-muted-foreground">{step.description}</p>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* Illustration */}
            <Card className="border-0 shadow-lg overflow-hidden">
              <CardContent className="p-0">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1677756041243-08ac39882525?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2llbnRpc3QlMjBob2xvZ3JhcGhpYyUyMEROQSUyMHRlY2hub2xvZ3l8ZW58MXx8fHwxNzU4Njk0ODIyfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Genetic analysis workflow"
                  className="w-full h-48 object-cover"
                />
                <div className="p-4">
                  <h4>Advanced AI Analysis</h4>
                  <p className="text-sm text-muted-foreground">
                    Our machine learning algorithms analyze thousands of genetic markers to provide accurate predictions.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}