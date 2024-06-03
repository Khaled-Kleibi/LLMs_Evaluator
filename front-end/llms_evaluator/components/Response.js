import styles from './Response.module.css';

const Response = ({ title, content, scores }) => {
  const precision = scores[0] ? scores[0].toFixed(2) : 'N/A';
  const recall = scores[1] ? scores[1].toFixed(2) : 'N/A';
  const fmeasure = scores[2] ? scores[2].toFixed(2) : 'N/A';

  return (
    <div className={styles.responseContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>{title}</h1>
        {scores.length > 0 && (
          <div className={styles.scores}>
            <p>Precision: {precision}</p>
            <p>Recall: {recall}</p>
            <p>F-measure: {fmeasure}</p>
          </div>
        )}
      </div>
      <div className={styles.content}>{content}</div>
    </div>
  );
};

export default Response;
