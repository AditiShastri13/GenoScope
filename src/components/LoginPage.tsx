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

interface LoginPageProps {
  onNavigate: (page: string) => void;
}

export function LoginPage({ onNavigate }: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login, loading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    const success = await login(email, password);
    if (success) {
      toast.success("Login successful!");
      onNavigate('dashboard');
    } else {
      toast.error("Invalid credentials. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/5 flex items-center justify-center p-4">
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
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                
                <Button 
                  type="submit"
                  className="w-full bg-primary hover:bg-primary/90"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Logging in...
                    </>
                  ) : (
                    'Login'
                  )}
                </Button>
              </form>
              
              <div className="text-center space-y-2">
                <button className="text-sm text-muted-foreground hover:text-primary">
                  Forgot Password?
                </button>
                <div>
                  <span className="text-sm text-muted-foreground">Don't have an account? </span>
                  <button 
                    onClick={() => onNavigate('signup')}
                    className="text-sm text-accent hover:text-accent/80"
                  >
                    Sign Up
                  </button>
                </div>
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