import { useState } from 'react';
import Response from './Response';
import Footer from './Footer';
import styles from './ResponsesGrid.module.css';

const ResponsesGrid = () => {
  const [responses, setResponses] = useState([]);
  const [scores, setScores] = useState({});

  const handleSend = (prompt) => {
    
    setResponses([]);
    setScores({});

    
    fetch('http://127.0.0.1:5000/evaluate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      // SSE
      const eventSource = new EventSource('http://127.0.0.1:5000/evaluate-stream');

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.response) {
          setResponses((prevResponses) => [...prevResponses, data]);
        } else if (data.rouge_scores) {
          setScores((prevScores) => ({ ...prevScores, [data.model]: data.rouge_scores }));
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
  };

  return (
    <div className={styles.gridContainer}>
      <div className={styles.responses}>
        {responses.map((response, index) => (
          <div key={index} className={styles.responseContainer}>
            {console.log("here is the res")}
            {console.log(response)}
            <Response title={response.model} content={response.response} scores={response.scores} />
          </div>
        ))}
      </div>
      <Footer onSend={handleSend} />
    </div>
  );
};

export default ResponsesGrid;
