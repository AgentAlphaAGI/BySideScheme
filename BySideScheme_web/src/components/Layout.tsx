import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, BrainCircuit, Database, User, MessageSquareDashed } from 'lucide-react';
import { cn } from '../utils/cn';

const Layout: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: '仪表板' },
    { path: '/advisor', icon: BrainCircuit, label: '策略顾问' },
    { path: '/simulator', icon: MessageSquareDashed, label: '模拟器' },
    { path: '/memory', icon: Database, label: '记忆库' },
    { path: '/profile', icon: User, label: '个人中心' },
  ];

  return (
    <div className="min-h-screen bg-background text-white flex flex-col md:flex-row">
      {/* Sidebar / Mobile Bottom Nav */}
      <nav className="glass fixed bottom-0 w-full md:static md:w-64 md:h-screen flex md:flex-col justify-around md:justify-start md:pt-10 z-50">
        <div className="hidden md:flex items-center justify-center mb-10">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent neon-text-blue">
            在旁术
          </h1>
        </div>
        
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex flex-col md:flex-row items-center p-4 md:px-8 md:py-4 transition-all duration-300",
                isActive 
                  ? "text-primary neon-text-blue bg-white/5 border-t-2 md:border-t-0 md:border-r-2 border-primary" 
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              )}
            >
              <item.icon className={cn("w-6 h-6 md:mr-3", isActive && "animate-pulse")} />
              <span className="text-xs md:text-base mt-1 md:mt-0">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-8 mb-16 md:mb-0 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
