import { Button } from "./ui/button";
import { Home, Upload, FileText, User, LogOut } from "lucide-react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDna } from '@fortawesome/free-solid-svg-icons';

interface NavigationProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export function Navigation({ currentPage, onNavigate }: NavigationProps) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-card/95 backdrop-blur-sm border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center gap-3 text-primary cursor-pointer font-bold text-xl" onClick={() => onNavigate('dashboard')}>
            <div className="relative">
              <FontAwesomeIcon icon={faDna} className="w-7 h-7" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-accent rounded-full animate-pulse"></div>
            </div>
            <span className="bg-clip-text text-transparent">
              GenoScope
            </span>
          </div>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Button
                  key={item.id}
                  variant={currentPage === item.id ? "default" : "ghost"}
                  onClick={() => onNavigate(item.id)}
                  className="flex items-center gap-2"
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Button>
              );
            })}
            
            <Button
              variant="ghost"
              onClick={() => onNavigate('login')}
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <Button variant="ghost" size="sm">
              <span className="sr-only">Open main menu</span>
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}