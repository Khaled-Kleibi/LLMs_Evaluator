'use client';

import { useState } from 'react';
import styles from './Footer.module.css';

const Footer = ({ onSend }) => {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (message.trim() && !loading) {
      setLoading(true);
      console.log('Sending message:', message);
      try {
        const response = await fetch('http://127.0.0.1:5000/evaluate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt: message }),
        });

        console.log('Response status:', response.status);
        if (!response.ok) {
          throw new Error(`Network response was not ok: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('Server response:', result);
        onSend(result);
      } catch (error) {
        console.error('Error sending message:', error);
      }

      setLoading(false);
      setMessage('');
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <footer className={styles.footer}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message here..."
        className={styles.input}
        disabled={loading}
      />
      <button onClick={handleSend} className={`${styles.button} ${styles.rouge}`} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>
    </footer>
  );
};

export default Footer;
