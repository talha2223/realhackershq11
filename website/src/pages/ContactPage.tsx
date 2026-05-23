import React from 'react';
import { Mail, MessageSquare, Globe, Send } from 'lucide-react';

const ContactPage: React.FC = () => {
  return (
    <div className="container" style={{ maxWidth: '1000px', padding: '1rem' }}>
       
       <header style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <h1 style={{ fontSize: '3rem', fontWeight: '900', letterSpacing: '4px' }}>CONTACT_US</h1>
          <p style={{ opacity: 0.5 }}>NEED_SUPPORT? OUR_OPERATORS_ARE_STANDING_BY.</p>
       </header>

       <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3rem' }}>
          
          <div className="card" style={{ padding: '2rem' }}>
             <h2 style={{ marginBottom: '2rem' }}>DIRECT_CHANNELS</h2>
             
             <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                <a href="mailto:soolipitrair@Gmail.com" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', color: '#fff', textDecoration: 'none' }}>
                   <div style={{ background: 'rgba(231, 76, 60, 0.1)', padding: '1rem', borderRadius: '8px' }}>
                      <Mail color="var(--accent-color)" />
                   </div>
                   <div>
                      <div style={{ fontSize: '0.6rem', color: '#666', fontWeight: 'bold' }}>EMAIL_SECURE</div>
                      <div style={{ fontSize: '1rem' }}>soolipitrair@Gmail.com</div>
                   </div>
                </a>

                <a href="https://wa.me/923079347077" target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', color: '#fff', textDecoration: 'none' }}>
                   <div style={{ background: 'rgba(37, 211, 102, 0.1)', padding: '1rem', borderRadius: '8px' }}>
                      <MessageSquare color="#25D366" />
                   </div>
                   <div>
                      <div style={{ fontSize: '0.6rem', color: '#666', fontWeight: 'bold' }}>WHATSAPP_LINE</div>
                      <div style={{ fontSize: '1rem' }}>+92 307 9347077</div>
                   </div>
                </a>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                   <div style={{ background: 'rgba(52, 152, 219, 0.1)', padding: '1rem', borderRadius: '8px' }}>
                      <Globe color="#3498db" />
                   </div>
                   <div>
                      <div style={{ fontSize: '0.6rem', color: '#666', fontWeight: 'bold' }}>OPERATIONAL_REGION</div>
                      <div style={{ fontSize: '1rem' }}>GLOBAL / REMOTE</div>
                   </div>
                </div>
             </div>
          </div>

          <div className="card" style={{ padding: '2rem' }}>
             <h2 style={{ marginBottom: '2rem' }}>SEND_TICKET</h2>
             <form style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <input type="text" placeholder="SUBJECT" style={{ background: '#000', border: '1px solid #222', padding: '1rem', color: '#fff' }} />
                <textarea placeholder="MESSAGE_DETAILS" rows={6} style={{ background: '#000', border: '1px solid #222', padding: '1rem', color: '#fff', resize: 'none' }} />
                <button type="button" className="btn" style={{ width: '100%' }}>SUBMIT_ENCRYPTED_MESSAGE <Send size={14} /></button>
             </form>
          </div>

       </div>

    </div>
  );
};

export default ContactPage;
