import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardView from './components/DashboardView';
import GmailView from './components/GmailView';
import DriveView from './components/DriveView';
import AgentChatView from './components/AgentChatView';
import ApiMonitorView from './components/ApiMonitorView';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [theme, setTheme] = useState('dark');

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    document.body.className = `${nextTheme}-theme`;
  };

  useEffect(() => {
    document.body.className = `${theme}-theme`;
  }, [theme]);

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView setActiveTab={setActiveTab} />;
      case 'gmail':
        return <GmailView />;
      case 'drive':
        return <DriveView />;
      case 'agent':
        return <AgentChatView />;
      case 'api-monitor':
        return <ApiMonitorView />;
      default:
        return <DashboardView setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        <Header activeTab={activeTab} theme={theme} toggleTheme={toggleTheme} />
        
        <div className="content-container">
          {renderActiveView()}
        </div>
      </main>
    </div>
  );
}
