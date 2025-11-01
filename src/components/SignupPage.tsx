import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { useAuth } from "./hooks/useAuth";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDna } from '@fortawesome/free-solid-svg-icons';

interface SignupPageProps {
  onNavigate: (page: string) => void;
}

export function SignupPage({ onNavigate }: SignupPageProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const { signup, loading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name || !email || !password || !confirmPassword) {
      toast.error("Please fill in all fields");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    const success = await signup(name, email, password);
    if (success) {
      toast.success("Account created successfully!");
      onNavigate('dashboard');
    } else {
      toast.error("Failed to create account. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-accent/5 via-background to-primary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-md relative z-10">
        <Card className="w-full shadow-2xl border-0 bg-card/80 backdrop-blur-sm">
          <CardHeader className="text-center space-y-4 pb-8">
            <div className="flex justify-center">
              <div className="relative">
                <FontAwesomeIcon icon={faDna} className="w-16 h-16 text-primary" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full animate-pulse"></div>
              </div>
            </div>
            <CardTitle className="text-3xl font-bold bg-clip-text text-transparent">
              GenoScope
            </CardTitle>
            <CardDescription className="text-base">
              AI-Powered Genomic Variant Analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="pb-8">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input 
                    id="name" 
                    type="text" 
                    placeholder="Enter your full name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input 
                    id="password" 
                    type="password" 
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input 
                    id="confirmPassword" 
                    type="password" 
                    placeholder="Confirm your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </div>
                
                <Button 
                  type="submit"
                  className="w-full bg-accent hover:bg-accent/90"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating Account...
                    </>
                  ) : (
                    'Create Account'
                  )}
                </Button>
              </form>
              
              <div className="text-center">
                <span className="text-sm text-muted-foreground">Already have an account? </span>
                <button 
                  onClick={() => onNavigate('login')}
                  className="text-sm text-primary hover:text-primary/80"
                >
                  Login
                </button>
              </div>
            </CardContent>
          </Card>
        
        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-muted-foreground">
            For research and educational purposes only
          </p>
        </div>
      </div>
    </div>
  );
}