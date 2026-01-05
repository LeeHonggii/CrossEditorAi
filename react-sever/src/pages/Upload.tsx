import React, { useState } from "react";
// import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Upload.css";
import "./UploadComponent.css";
import "./UploadLoader.css";

const Upload: React.FC = () => {
  // const navigate = useNavigate();
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFiles(event.target.files);
    }
  };

  const uploadFiles = async () => {
    if (!selectedFiles) return false;

    const formData = new FormData();
    for (let i = 0; i < selectedFiles.length; i++) {
      formData.append("files", selectedFiles[i]);
    }

    try {
      await axios.post("http://localhost:8000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return true;
    } catch (error) {
      console.error("Upload failed:", error);
      alert("파일 업로드에 실패했습니다.");
      return false;
    }
  };

  const handleAutoEdit = async () => {
    if (!selectedFiles) {
      alert("영상을 선택해주세요.");
      return;
    }

    setUploading(true);
    const uploadSuccess = await uploadFiles();
    if (!uploadSuccess) {
      setUploading(false);
      return;
    }

    // navigate("/loading"); // Show loading screen
    window.location.hash = '#/loading';

    try {
      const response = await axios.post("http://localhost:8000/process/auto");
      // Assuming response contains video_url or filename
      // Navigate to result with data
      // navigate("/result", { state: { videoUrl: response.data.video_url } });
      // For manual router, we might need a global state or just pass data via localStorage/global var for now
      // Simpler: just go to result, Result component fetches data or we use a simple global
      (window as any)['__RESULT_DATA__'] = { videoUrl: response.data.video_url };
      window.location.hash = '#/result';
    } catch (error) {
      console.error("Auto processing failed:", error);
      alert("자동 편집 중 오류가 발생했습니다.");
      // navigate("/upload"); // Go back on error
      window.location.hash = '#/upload';
    } finally {
      setUploading(false);
    }
  };

  const handleManualEdit = async () => {
    if (!selectedFiles) {
      alert("영상을 선택해주세요.");
      return;
    }

    setUploading(true);
    const uploadSuccess = await uploadFiles();
    if (!uploadSuccess) {
      setUploading(false);
      return;
    }

    try {
      // Call analyze endpoint
      const response = await axios.post("http://localhost:8000/process/analyze");
      // Navigate to Manual page with analysis data
      // navigate("/manual", { state: { analysisData: response.data } });
      (window as any)['__MANUAL_DATA__'] = { analysisData: response.data };
      window.location.hash = '#/manual';
    } catch (error) {
      console.error("Analysis failed:", error);
      alert("영상 분석 중 오류가 발생했습니다.");
    } finally {
      setUploading(false);
    }
  };



  return (
    <div className="upload-page-container">
      <div className="page" style={{
        backgroundColor: '#010101',
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        position: 'relative', // Ensure z-index works
        zIndex: 10000, // Force on top
        pointerEvents: 'auto' // Force clickable
      }}>
        <div className="div-2" style={{ maxWidth: '800px', width: '100%', padding: '40px', textAlign: 'center' }}>
          <div className="text-wrapper-2" style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px', color: 'var(--flowkitblue)' }}>이용 가이드</div>
          <p className="p" style={{ marginBottom: '40px', lineHeight: '1.6' }}>
            교차편집을 원하는 영상을 첨부하고 편집 모드를 선택해주세요.
          </p>
          <div className="text-wrapper-2" style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px', color: 'var(--flowkitblue)' }}>영상 첨부</div>
          <p className="p" style={{ marginBottom: '20px' }}>영상 파일을 선택해주세요 (여러 개 선택 가능)</p>

          <div className="components-container" style={{ display: 'flex', justifyContent: 'center', padding: '20px', marginBottom: '40px' }}>
            <label htmlFor="file-upload" style={{
              cursor: 'pointer',
              padding: '40px',
              border: '2px dashed var(--flowkitblue)',
              borderRadius: '20px',
              width: '100%',
              backgroundColor: 'rgba(0, 153, 255, 0.1)',
              transition: 'all 0.3s ease'
            }}>
              <div style={{ fontSize: '18px', marginBottom: '10px' }}>
                {selectedFiles ? `${selectedFiles.length}개의 파일이 선택됨` : "클릭하여 파일 선택"}
              </div>
              <div style={{ fontSize: '14px', color: '#888' }}>
                {selectedFiles ? "다시 선택하려면 클릭하세요" : "또는 파일을 여기로 드래그하세요"}
              </div>
            </label>
            <input
              id="file-upload"
              type="file"
              multiple
              accept="video/*"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
            <button
              className="edit-button-instance"
              onClick={handleAutoEdit}
              disabled={uploading}
              style={{
                backgroundColor: 'var(--flowkitblue)',
                color: 'white',
                padding: '15px 40px',
                borderRadius: '30px',
                border: 'none',
                fontSize: '18px',
                fontWeight: 'bold',
                cursor: uploading ? 'not-allowed' : 'pointer',
                opacity: uploading ? 0.7 : 1,
                transition: 'transform 0.2s'
              }}
            >
              {uploading ? "처리 중..." : "자동 편집 시작"}
            </button>
            <button
              className="edit-button-instance"
              onClick={handleManualEdit}
              disabled={uploading}
              style={{
                backgroundColor: 'var(--flowkitred)',
                color: 'white',
                padding: '15px 40px',
                borderRadius: '30px',
                border: 'none',
                fontSize: '18px',
                fontWeight: 'bold',
                cursor: uploading ? 'not-allowed' : 'pointer',
                opacity: uploading ? 0.7 : 1,
                transition: 'transform 0.2s'
              }}
            >
              {uploading ? "처리 중..." : "수동 편집 (타임라인)"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
