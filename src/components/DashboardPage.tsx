import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { Navigation } from "./Navigation";
import { Dna, FileText, Activity, Upload, BarChart3, PieChart, FileBarChart } from "lucide-react";

interface DashboardPageProps {
  onNavigate: (page: string) => void;
}

export function DashboardPage({ onNavigate }: DashboardPageProps) {
  // Real GenoScope project statistics
  const stats = [
    {
      title: "Training Samples",
      value: "2,507",
      icon: Dna,
      color: "text-primary",
      bgColor: "bg-primary/10",
      description: "1,600 Sickle Cell + 907 Breast Cancer"
    },
    {
      title: "Diseases Predicted",
      value: "2",
      icon: PieChart,
      color: "text-accent",
      bgColor: "bg-accent/10",
      description: "Sickle Cell & Breast Cancer"
    },
    {
      title: "Sickle Cell Model",
      value: "85.0%",
      icon: BarChart3,
      color: "text-green-600",
      bgColor: "bg-green-100",
      description: "Test accuracy (Gradient Boosting)"
    },
    {
      title: "Breast Cancer Model",
      value: "82.7%",
      icon: FileBarChart,
      color: "text-orange-600",
      bgColor: "bg-orange-100",
      description: "CV accuracy (XGBoost)"
    }
  ];

  const recentActivity = [
    {
      fileName: "REAL_TRAINING_pathogenic_sickle_cell.fasta",
      uploadDate: "2025-11-01",
      mutations: "GAG→GTG",
      predictedDisease: "Sickle Cell Disease",
      confidence: 100.0
    },
    {
      fileName: "REAL_TRAINING_pathogenic_brca_1.fasta",
      uploadDate: "2025-11-01",
      mutations: "BRCA1 17:43045571",
      predictedDisease: "Breast Cancer",
      confidence: 85.4
    },
    {
      fileName: "ULTIMATE_sickle_cell_pathogenic.fasta",
      uploadDate: "2025-11-01",
      mutations: "229 GTG codons",
      predictedDisease: "Sickle Cell Disease",
      confidence: 29.9
    },
    {
      fileName: "BRCA2_pathogenic_6174delT.fasta",
      uploadDate: "2025-11-01",
      mutations: "6174delT",
      predictedDisease: "Breast Cancer",
      confidence: 8.3
    },
    {
      fileName: "TP53_pathogenic_R175H.fasta",
      uploadDate: "2025-11-01",
      mutations: "R175H",
      predictedDisease: "Multiple Cancers",
      confidence: 4.7
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation currentPage="dashboard" onNavigate={onNavigate} />
      
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-primary to-accent rounded-3xl p-8 text-white">
          <div className="max-w-3xl">
            <h1 className="text-4xl mb-4">👋 Welcome to GenoScope</h1>
            <p className="text-xl mb-6 text-white/90">
              AI-powered genomic variant analysis with 83.9% average accuracy. Upload FASTA sequences to predict Sickle Cell Disease and Breast Cancer risk.
            </p>
            <Button 
              size="lg" 
              className="bg-white text-primary hover:bg-white/90"
              onClick={() => onNavigate('upload')}
            >
              <Upload className="w-5 h-5 mr-2" />
              Upload Sequence
            </Button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">{stat.title}</p>
                      <p className="text-3xl font-bold">{stat.value}</p>
                      <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
                    </div>
                    <div className={`p-3 rounded-full ${stat.bgColor}`}>
                      <Icon className={`w-6 h-6 ${stat.color}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Recent Activity */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Recent Test Results
            </CardTitle>
            <CardDescription>
              Latest FASTA sequence uploads and prediction results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File Name</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Variant</TableHead>
                  <TableHead>Predicted Disease</TableHead>
                  <TableHead>Confidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentActivity.map((activity, index) => (
                  <TableRow key={index} className="cursor-pointer hover:bg-muted/50">
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-muted-foreground" />
                        {activity.fileName}
                      </div>
                    </TableCell>
                    <TableCell>{activity.uploadDate}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs">{activity.mutations}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
                        {activity.predictedDisease}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Progress value={activity.confidence} className="w-16 h-2" />
                        <span className="text-sm">{activity.confidence}%</span>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}