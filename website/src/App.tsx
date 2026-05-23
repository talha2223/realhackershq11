import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';
import ADexPage from './pages/ADexPage';
import HDexPage from './pages/HDexPage';
import PhishingPage from './pages/PhishingPage';
import OSINTPage from './pages/OSINTPage';
import DangerPage from './pages/DangerPage';
import CreditsPage from './pages/CreditsPage';
import ContactPage from './pages/ContactPage';
import AboutPage from './pages/AboutPage';
import DocsPage from './pages/DocsPage';
import AdminPage from './pages/AdminPage';
import NotFoundPage from './pages/NotFoundPage';
import { AuthProvider } from './components/AuthContext';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
            <Route path="a-dex" element={<ADexPage />} />
            <Route path="h-dex" element={<HDexPage />} />
            <Route path="phishing" element={<PhishingPage />} />
            <Route path="osint" element={<OSINTPage />} />
            <Route path="danger" element={<DangerPage />} />
            <Route path="credits" element={<CreditsPage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="contact" element={<ContactPage />} />
            <Route path="docs" element={<DocsPage />} />
            <Route path="admin" element={<AdminPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
