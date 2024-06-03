import { useState } from 'react';
import Response from './Response';
import Footer from './Footer';
import styles from './ResponsesGrid.module.css';

const ResponsesGrid = () => {
  const [combinedResponses, setCombinedResponses] = useState([]);

  const handleSend = (apiResponses) => {
    const { results, rouge_scores } = apiResponses;

    const combinedData = Object.keys(results).map((key) => ({
      title: key,
      content: results[key],
      scores: rouge_scores[key] ? rouge_scores[key].rouge2 : [],
    }));

    setCombinedResponses(combinedData);
  };

  return (
    <div className={styles.gridContainer}>
      <div className={styles.responses}>
        {combinedResponses.map((response, index) => (
          <div key={index} className={styles.responseContainer}>
            <Response title={response.title} content={response.content} scores={response.scores} />
          </div>
        ))}
      </div>
      <Footer onSend={handleSend} />
    </div>
  );
};

export default ResponsesGrid;
