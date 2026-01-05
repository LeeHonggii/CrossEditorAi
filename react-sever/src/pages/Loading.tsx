import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Loading.css';

const Loading: React.FC = () => {
  const navigate = useNavigate();
  const [log, setLog] = useState<string>("영상을 확인하고 있습니다...");

  useEffect(() => {
    const analyzeVideo = async () => {
      try {
        const response = await fetch('http://localhost:5000/analyze', {
          method: 'POST',
        });
        const data = await response.json();
        console.log(data);
        navigate('/result'); // 비디오 분석 완료 후 결과 페이지로 이동
      } catch (error) {
        console.error('Error analyzing video:', error);
      }
    };

    const socket = new WebSocket('ws://localhost:5000');
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'stdout' || message.type === 'stderr') {
        setLog(message.data);
      }
    };

    socket.onopen = () => {
      console.log('WebSocket connection opened');
      analyzeVideo();
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      socket.close();
    };
  }, [navigate]);

  return (
    <div className="loading-page-container">
      <div className="loading-container">
        <div className="log-output">
          <p>{log}</p>
        </div>
        <div className="spinner"></div>
      </div>
    </div>
  );
};

export default Loading;
