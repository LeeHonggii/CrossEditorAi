import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Result.css';

const Result: React.FC = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const globalData = (window as any)['__RESULT_DATA__'];
    if (location.state && location.state.videoUrl) {
      setVideoUrl(`http://localhost:8000${location.state.videoUrl}`);
    } else if (globalData && globalData.videoUrl) {
      setVideoUrl(`http://localhost:8000${globalData.videoUrl}`);
    }
  }, [location.state]);

  const handleDownloadAndRedirect = async () => {
    // 비디오 다운로드
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = 'final_video.mp4';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // 메인 페이지로 이동
    navigate('/');
  };

  return (
    <div className="result-page-container">
      <div className="result-page" style={{ backgroundColor: '#010101', minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: 'white' }}>
        <h1 style={{ color: 'var(--flowkitblue)', marginBottom: '30px' }}>생성된 영상</h1>
        {videoUrl ? (
          <div className="video-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
            <video
              controls
              src={videoUrl}
              width="800"
              style={{ borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', border: '2px solid #333' }}
            />
            <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
              <button
                className="download-button"
                onClick={handleDownloadAndRedirect}
                style={{
                  backgroundColor: 'var(--flowkitgreen)',
                  color: 'white',
                  padding: '15px 40px',
                  borderRadius: '30px',
                  border: 'none',
                  fontSize: '18px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}
              >
                저장하기
              </button>
              <button
                onClick={() => navigate('/')}
                style={{
                  backgroundColor: '#333',
                  color: 'white',
                  padding: '15px 40px',
                  borderRadius: '30px',
                  border: 'none',
                  fontSize: '18px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}
              >
                메인으로
              </button>
              <button
                onClick={() => navigate('/upload')}
                style={{
                  backgroundColor: 'var(--flowkitblue)',
                  color: 'white',
                  padding: '15px 40px',
                  borderRadius: '30px',
                  border: 'none',
                  fontSize: '18px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'transform 0.2s'
                }}
              >
                다시 만들기
              </button>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center' }}>
            <div className="loader" style={{ border: '5px solid #333', borderTop: '5px solid var(--flowkitblue)', borderRadius: '50%', width: '50px', height: '50px', animation: 'spin 1s linear infinite', margin: '0 auto 20px' }}></div>
            <p style={{ fontSize: '18px' }}>영상을 생성하고 있습니다... 잠시만 기다려주세요.</p>
            <p style={{ fontSize: '14px', color: '#888', marginTop: '10px' }}>(시간이 오래 걸릴 수 있습니다)</p>
            <style>{`
                  @keyframes spin {
                      0% { transform: rotate(0deg); }
                      100% { transform: rotate(360deg); }
                  }
              `}</style>
          </div>
        )}
      </div>
    </div>
  );
};

export default Result;
