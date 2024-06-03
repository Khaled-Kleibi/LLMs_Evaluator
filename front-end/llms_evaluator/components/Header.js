import Image from 'next/image';
import styles from './Header.module.css';

const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.logoContainer}>
        <Image src="/bot.png" alt="Logo" width={50} height={50} />
      </div>
        <p className={styles.title}>LLM's Evaluator</p>
    </header>
  );
};

export default Header;
