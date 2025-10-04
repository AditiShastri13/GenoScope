import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Navigation } from "./Navigation";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { FileText, Download, Share2, Calendar, FileCheck, Target, Dna, AlertTriangle, CheckCircle } from "lucide-react";

interface ReportPageProps {
  onNavigate: (page: string) => void;
}

export function ReportPage({ onNavigate }: ReportPageProps) {
  // Mock data for charts
  const confidenceData = [
    { disease: 'Breast Cancer', confidence: 94.7 },
    { disease: 'Ovarian Cancer', confidence: 78.2 },
    { disease: 'Colorectal Cancer', confidence: 43.1 },
    { disease: 'Prostate Cancer', confidence: 22.8 },
    { disease: 'Lung Cancer', confidence: 18.5 }
  ];

  const mutationTypeData = [
    { name: 'SNP', value: 65, color: '#2B4C7E' },
    { name: 'Indel', value: 25, color: '#6C63FF' },
    { name: 'Deletion', value: 10, color: '#10B981' }
  ];

  const mutationDetails = [
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
  ];

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
            <p className="text-muted-foreground mt-2">Comprehensive genetic analysis results</p>
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

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Patient/Upload Info */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileCheck className="w-5 h-5" />
                  Analysis Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3">
                  <FileText className="w-8 h-8 text-primary bg-primary/10 p-2 rounded-lg" />
                  <div>
                    <p className="text-sm text-muted-foreground">File Name</p>
                    <p>patient_mutations.csv</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Calendar className="w-8 h-8 text-accent bg-accent/10 p-2 rounded-lg" />
                  <div>
                    <p className="text-sm text-muted-foreground">Upload Date</p>
                    <p>January 15, 2025</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Dna className="w-8 h-8 text-green-600 bg-green-100 p-2 rounded-lg" />
                  <div>
                    <p className="text-sm text-muted-foreground">Mutations Analyzed</p>
                    <p>342 variants</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Prediction Summary */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Prediction Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-2xl text-primary mb-2">Predicted Disease</h3>
                      <Badge className="bg-red-100 text-red-800 border-red-200 text-lg px-4 py-2">
                        Breast Cancer
                      </Badge>
                    </div>
                    <div>
                      <h4 className="mb-2">Key Mutation</h4>
                      <p className="font-mono bg-muted p-2 rounded">BRCA1 c.68_69delAG</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-center">
                    <div className="relative w-32 h-32">
                      <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                        <path
                          className="text-gray-200"
                          strokeWidth="3"
                          fill="none"
                          stroke="currentColor"
                          d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <path
                          className="text-accent"
                          strokeWidth="3"
                          strokeDasharray="94.7, 100"
                          fill="none"
                          stroke="currentColor"
                          d="M18 2.0845
                            a 15.9155 15.9155 0 0 1 0 31.831
                            a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                          <div className="text-2xl text-accent">94.7%</div>
                          <div className="text-xs text-muted-foreground">Confidence</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Charts */}
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle>Disease Risk Confidence</CardTitle>
                  <CardDescription>Prediction confidence across disease categories</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={confidenceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="disease" 
                        tick={{ fontSize: 10 }}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="confidence" fill="#6C63FF" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg">
                <CardHeader>
                  <CardTitle>Mutation Distribution</CardTitle>
                  <CardDescription>Types of genetic variants detected</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={mutationTypeData}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}%`}
                      >
                        {mutationTypeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Mutation Details Table */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Dna className="w-5 h-5" />
                  Detailed Mutation Analysis
                </CardTitle>
                <CardDescription>
                  Key genetic variants contributing to the prediction
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
                      <TableHead>Clinical Notes</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mutationDetails.map((mutation, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-mono">{mutation.gene}</TableCell>
                        <TableCell className="font-mono text-sm">{mutation.mutation}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{mutation.consequence}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {mutation.pathogenicity === 'Pathogenic' && <AlertTriangle className="w-4 h-4 text-red-500" />}
                            {mutation.pathogenicity === 'Likely Pathogenic' && <AlertTriangle className="w-4 h-4 text-orange-500" />}
                            {mutation.pathogenicity === 'VUS' && <CheckCircle className="w-4 h-4 text-gray-500" />}
                            <Badge 
                              className={
                                mutation.pathogenicity === 'Pathogenic' 
                                  ? 'bg-red-100 text-red-800 border-red-200'
                                  : mutation.pathogenicity === 'Likely Pathogenic'
                                  ? 'bg-orange-100 text-orange-800 border-orange-200'
                                  : 'bg-gray-100 text-gray-800 border-gray-200'
                              }
                            >
                              {mutation.pathogenicity}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground max-w-xs">
                          {mutation.notes}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>

          {/* Right Panel */}
          <div className="space-y-6">
            {/* Scientist Illustration */}
            <Card className="border-0 shadow-lg overflow-hidden">
              <CardContent className="p-0">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1677756041243-08ac39882525?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzY2llbnRpc3QlMjBob2xvZ3JhcGhpYyUyMEROQSUyMHRlY2hub2xvZ3l8ZW58MXx8fHwxNzU4Njk0ODIyfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Scientist with holographic DNA strand"
                  className="w-full h-48 object-cover"
                />
                <div className="p-4">
                  <h4>AI-Powered Analysis</h4>
                  <p className="text-sm text-muted-foreground">
                    Advanced machine learning algorithms analyze your genetic data to provide precise risk assessments.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start" onClick={() => onNavigate('upload')}>
                  <FileText className="w-4 h-4 mr-2" />
                  Upload New Data
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={() => onNavigate('dashboard')}>
                  <Target className="w-4 h-4 mr-2" />
                  View Dashboard
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Share2 className="w-4 h-4 mr-2" />
                  Share with Doctor
                </Button>
              </CardContent>
            </Card>

            {/* Disclaimer */}
            <Card className="border-0 shadow-lg bg-orange-50 border-orange-200">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5" />
                  <div>
                    <h4 className="text-orange-800 mb-1">Important Notice</h4>
                    <p className="text-sm text-orange-700">
                      This analysis is for research and educational purposes only. 
                      Please consult with a healthcare professional for medical decisions.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}