import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { Navigation } from "./Navigation";
import { Dna, FileText, TrendingUp, Activity, Upload, BarChart3, PieChart, FileBarChart } from "lucide-react";

interface DashboardPageProps {
  onNavigate: (page: string) => void;
}

export function DashboardPage({ onNavigate }: DashboardPageProps) {
  // Mock data
  const stats = [
    {
      title: "Total Mutations Uploaded",
      value: "1,247",
      icon: Dna,
      color: "text-primary",
      bgColor: "bg-primary/10"
    },
    {
      title: "Predicted Diseases",
      value: "23",
      icon: PieChart,
      color: "text-accent",
      bgColor: "bg-accent/10"
    },
    {
      title: "Accuracy Score",
      value: "94.7%",
      icon: BarChart3,
      color: "text-green-600",
      bgColor: "bg-green-100"
    },
    {
      title: "Reports Generated",
      value: "156",
      icon: FileBarChart,
      color: "text-orange-600",
      bgColor: "bg-orange-100"
    }
  ];

  const recentActivity = [
    {
      fileName: "patient_001_mutations.csv",
      uploadDate: "2025-01-15",
      mutations: 342,
      predictedDisease: "Breast Cancer",
      confidence: 94.7
    },
    {
      fileName: "sample_genetic_data.csv",
      uploadDate: "2025-01-14",
      mutations: 156,
      predictedDisease: "Alzheimer's Disease",
      confidence: 87.3
    },
    {
      fileName: "genome_analysis_batch2.csv",
      uploadDate: "2025-01-13",
      mutations: 289,
      predictedDisease: "Colorectal Cancer",
      confidence: 91.2
    },
    {
      fileName: "hereditary_screening.csv",
      uploadDate: "2025-01-12",
      mutations: 78,
      predictedDisease: "Huntington's Disease",
      confidence: 96.1
    },
    {
      fileName: "family_history_analysis.csv",
      uploadDate: "2025-01-11",
      mutations: 203,
      predictedDisease: "Type 2 Diabetes",
      confidence: 82.5
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation currentPage="dashboard" onNavigate={onNavigate} />
      
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-primary to-accent rounded-3xl p-8 text-white">
          <div className="max-w-3xl">
            <h1 className="text-4xl mb-4">👋 Welcome, Dr. Smith</h1>
            <p className="text-xl mb-6 text-white/90">
              Analyze genetic mutations and predict disease risk instantly with our advanced AI algorithms.
            </p>
            <Button 
              size="lg" 
              className="bg-white text-primary hover:bg-white/90"
              onClick={() => onNavigate('upload')}
            >
              <Upload className="w-5 h-5 mr-2" />
              Get Started
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
                      <p className="text-3xl">{stat.value}</p>
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
              Recent Activity
            </CardTitle>
            <CardDescription>
              Your latest genetic analysis uploads and predictions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File Name</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Mutations</TableHead>
                  <TableHead>Predicted Disease</TableHead>
                  <TableHead>Confidence %</TableHead>
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
                    <TableCell>{activity.mutations}</TableCell>
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