import { useState } from 'react';
import styles from './Footer.module.css';

const Footer = ({ onSend }) => {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (message.trim() && !loading) {
      setLoading(true);
      onSend(message);
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
      <button onClick={handleSend} className={styles.button} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>
    </footer>
  );
};

export default Footer;
