/* eslint-disable */
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Upload.css';

const FPS = 24;

const Manual: React.FC = () => {
    // Use any to bypass strict type checks that might confuse the old parser
    const manualData = (window as any)['__MANUAL_DATA__'];
    const analysisData = manualData ? manualData.analysisData : null;

    // State with simple types
    const [currentVideo, setCurrentVideo] = useState<any>("");
    const [videoList, setVideoList] = useState<any[]>([]);
    const [rendering, setRendering] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [sequence, setSequence] = useState<any[]>([]);
    const [duration, setDuration] = useState(0);

    // Preview State
    const [preview, setPreview] = useState<any>(null);

    const videoRef = useRef<any>(null);
    const previewCurrentRef = useRef<any>(null);
    const previewTargetRef = useRef<any>(null);

    useEffect(() => {
        if (analysisData && analysisData.video_files && analysisData.video_files.length > 0) {
            setVideoList(analysisData.video_files);
            setCurrentVideo(analysisData.video_files[0]);
            setSequence([{ video: analysisData.video_files[0], start: 0 }]);
        }
    }, [analysisData]);

    // Handle preview synchronization
    useEffect(() => {
        if (preview && preview.show && previewCurrentRef.current && previewTargetRef.current) {
            const startTime = preview.currentFrame / FPS;
            // Play from 2 seconds before the cut
            const previewStart = Math.max(0, startTime - 2);

            previewCurrentRef.current.currentTime = previewStart;
            previewTargetRef.current.currentTime = previewStart;

            previewCurrentRef.current.play();
            previewTargetRef.current.play();
        }
    }, [preview]);

    if (!analysisData) {
        return (
            <div className="upload-page-container">
                <div style={{ color: 'white', textAlign: 'center', marginTop: '50px' }}>
                    No analysis data found. Please go back and upload videos.
                </div>
            </div>
        );
    }

    const { frame_similarities } = analysisData;

    // Ref for preserving time during auto-switch
    const pendingSeekRef = useRef<number | null>(null);

    const handleTimeUpdate = () => {
        if (!videoRef.current) return;

        // Ignore updates while we are waiting to seek after a switch
        if (pendingSeekRef.current !== null) return;

        const time = videoRef.current.currentTime;
        setCurrentTime(time);

        if (videoRef.current.duration && videoRef.current.duration !== duration) {
            setDuration(videoRef.current.duration);
        }

        // Preview Logic: Check if we need to switch videos based on sequence
        // Find the latest start time <= current time
        let activeSegment = sequence[0];
        for (let i = 1; i < sequence.length; i++) {
            if (sequence[i].start <= time + 0.1) { // Add small buffer
                activeSegment = sequence[i];
            } else {
                break;
            }
        }

        if (activeSegment && activeSegment.video !== currentVideo) {
            console.log(`Auto-switching to ${activeSegment.video} at ${time}`);
            pendingSeekRef.current = time;
            setCurrentVideo(activeSegment.video);
            // The video src will change, triggering reload. 
            // onLoadedMetadata will handle the seek.
        }
    };

    const handleVideoSwitch = (targetVideo: string, frame: number) => {
        const time = frame / FPS;

        setSequence(prev => {
            // 1. Remove any existing transition at the exact same time (replace it)
            // 2. Filter out transitions that are redundant (same video as previous segment)
            // But wait, if we replace a segment, the "previous" might change.
            // Simplest approach: Add new one, sort, then clean up.

            const newSeq = [...prev.filter(item => Math.abs(item.start - time) > 0.01), { video: targetVideo, start: time }];
            newSeq.sort((a, b) => a.start - b.start);

            // Clean up redundant segments (e.g. A -> A)
            // We only keep a segment if it changes the video from the previous segment
            const cleanedSeq = [newSeq[0]];
            for (let i = 1; i < newSeq.length; i++) {
                if (newSeq[i].video !== newSeq[i - 1].video) {
                    cleanedSeq.push(newSeq[i]);
                }
            }
            return cleanedSeq;
        });

        setCurrentVideo(targetVideo);
        // Do NOT reset duration here, we want to preserve the global timeline feel.
        // But if videos have different lengths, it might be tricky. 
        // Assuming synced videos, duration should be same. 
        // If not, onLoadedMetadata will update it.

        // NO Auto-play, just jump to time
        setTimeout(() => {
            if (videoRef.current) {
                videoRef.current.currentTime = time;
                // videoRef.current.play(); // REMOVED Auto-play
            }
        }, 100);

        setPreview(null); // Close preview
    };

    const handleRender = async () => {
        setRendering(true);
        try {
            console.log("Sending sequence:", sequence);
            const response = await axios.post("http://localhost:8000/process/render", { sequence });
            (window as any)['__RESULT_DATA__'] = { videoUrl: response.data.video_url };
            window.location.hash = '#/result';
        } catch (error) {
            console.error("Rendering failed:", error);
            alert("영상 생성 중 오류가 발생했습니다.");
        } finally {
            setRendering(false);
        }
    };

    // Helper to find transition points for a specific video track
    const getTransitionPoints = (targetVideoName: string) => {
        const points: any[] = [];

        // Iterate over ALL frames in frame_similarities
        const entries = Object.entries(frame_similarities);
        for (let i = 0; i < entries.length; i++) {
            const [frameStr, matches] = entries[i];
            const frame = parseInt(frameStr, 10);
            const time = frame / FPS;

            // Filter out points in the past (with a small buffer)
            // User might want to see all points now? 
            // "지금은 내가 보고 있는 위취에 초록불이 들어와" -> "Filter past" was requested.
            // But for "Preview" concept, maybe we should show all?
            // User said: "내가 만약에 10초에서... 그이후에 시간대에서..." -> implies future only.
            // Let's keep the future filter for now.
            if (time < currentTime + 0.5) continue;

            // Cast matches to any to iterate
            const matchPairs = matches as any[];

            for (let j = 0; j < matchPairs.length; j++) {
                const pair = matchPairs[j];
                const file1 = pair[0].split('/').pop();
                const file2 = pair[1].split('/').pop();

                // If one of the pair is the current video, the other is a target
                if (file1 === currentVideo && file2 === targetVideoName) {
                    points.push({ frame: frame, currentVideo: file1 });
                } else if (file2 === currentVideo && file1 === targetVideoName) {
                    points.push({ frame: frame, currentVideo: file2 });
                }
            }
        }

        return points;
    };

    return (
        <div className="upload-page-container">
            <div className="page" style={{ backgroundColor: '#010101', minHeight: '100vh', color: 'white', padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

                {/* Main Container */}
                <div style={{
                    width: '95%',
                    maxWidth: '1400px',
                    backgroundColor: 'rgba(255, 192, 203, 0.1)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: '30px',
                    padding: '30px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                        <h2 style={{ color: 'var(--flowkitblue)', margin: 0 }}>Interactive Manual Editor</h2>
                        <button
                            onClick={handleRender}
                            disabled={rendering}
                            style={{
                                backgroundColor: 'var(--flowkitred)',
                                color: 'white',
                                padding: '10px 30px',
                                borderRadius: '20px',
                                border: 'none',
                                fontSize: '16px',
                                fontWeight: 'bold',
                                cursor: rendering ? 'not-allowed' : 'pointer',
                                opacity: rendering ? 0.7 : 1
                            }}
                        >
                            {rendering ? "생성 중..." : "편집 완료"}
                        </button>
                    </div>

                    {/* Main Player */}
                    <div style={{ width: '100%', height: '500px', backgroundColor: '#000', borderRadius: '20px', overflow: 'hidden', marginBottom: '30px', position: 'relative', border: '2px solid #333' }}>
                        {currentVideo && (
                            <video
                                ref={videoRef}
                                src={`http://localhost:8000/videos/${currentVideo}`}
                                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                controls
                                onTimeUpdate={handleTimeUpdate}
                                onLoadedMetadata={() => {
                                    if (videoRef.current) {
                                        setDuration(videoRef.current.duration);
                                        // Handle auto-switch seek
                                        if (pendingSeekRef.current !== null) {
                                            videoRef.current.currentTime = pendingSeekRef.current;
                                            videoRef.current.play(); // Resume playback
                                            pendingSeekRef.current = null;
                                        }
                                    }
                                }}
                            />
                        )}
                    </div>

                    {/* Timeline Section */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                        {videoList.map((videoName: any, index: number) => {
                            const isCurrent = videoName === currentVideo;
                            const transitionPoints = !isCurrent ? getTransitionPoints(videoName) : [];

                            return (
                                <div key={videoName} style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                                    {/* Label */}
                                    <div style={{ width: '150px', textAlign: 'right', fontWeight: 'bold', color: isCurrent ? 'var(--flowkitblue)' : '#888' }}>
                                        {videoName}
                                    </div>

                                    {/* Track Bar */}
                                    <div style={{ flex: 1, height: '40px', backgroundColor: '#222', borderRadius: '10px', position: 'relative', overflow: 'hidden' }}>
                                        {/* Progress Bar (only for current video) */}
                                        {isCurrent && (
                                            <div style={{
                                                position: 'absolute',
                                                left: 0,
                                                top: 0,
                                                bottom: 0,
                                                width: `${(currentTime / duration) * 100}%`,
                                                backgroundColor: 'rgba(52, 152, 219, 0.3)',
                                                borderRight: '2px solid var(--flowkitblue)'
                                            }}></div>
                                        )}

                                        {/* Green Blocks (Transition Points) */}
                                        {duration > 0 && transitionPoints.map((point: any, idx: number) => (
                                            <div
                                                key={idx}
                                                onMouseEnter={(e) => {
                                                    const rect = e.currentTarget.getBoundingClientRect();
                                                    setPreview({
                                                        show: true,
                                                        x: rect.left,
                                                        y: rect.top - 220, // Position above the block
                                                        targetVideo: videoName,
                                                        targetFrame: point.frame,
                                                        currentFrame: point.frame
                                                    });
                                                }}
                                                onMouseLeave={() => setPreview(null)}
                                                onClick={() => handleVideoSwitch(videoName, point.frame)}
                                                style={{
                                                    position: 'absolute',
                                                    left: `${((point.frame / FPS) / duration) * 100}%`, // Position at specific frame time
                                                    top: '5px',
                                                    bottom: '5px',
                                                    width: '20px', // Fixed width for visibility
                                                    backgroundColor: 'var(--flowkitgreen)',
                                                    borderRadius: '5px',
                                                    cursor: 'pointer',
                                                    boxShadow: '0 0 10px var(--flowkitgreen)',
                                                    zIndex: 10
                                                }}
                                            ></div>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Edit History Section */}
                    <div style={{ marginTop: '30px', width: '100%', color: '#ccc' }}>
                        <h3 style={{ borderBottom: '1px solid #444', paddingBottom: '10px' }}>Edit History</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', maxHeight: '150px', overflowY: 'auto' }}>
                            {sequence.map((item, idx) => {
                                if (idx === 0) return null; // Skip initial start
                                const prevItem = sequence[idx - 1];
                                return (
                                    <div key={idx} style={{ padding: '5px 10px', backgroundColor: '#222', borderRadius: '5px' }}>
                                        <span style={{ color: 'var(--flowkitblue)', fontWeight: 'bold' }}>
                                            {new Date(item.start * 1000).toISOString().substr(14, 5)}
                                        </span>
                                        <span style={{ margin: '0 10px' }}>:</span>
                                        <span>{prevItem.video}</span>
                                        <span style={{ margin: '0 10px', color: '#888' }}>→</span>
                                        <span style={{ color: 'white' }}>{item.video}</span>
                                    </div>
                                );
                            })}
                            {sequence.length <= 1 && (
                                <div style={{ color: '#666', fontStyle: 'italic' }}>No edits yet. Click green blocks to add transitions.</div>
                            )}
                        </div>
                    </div>

                </div>

                {/* Hover Preview Popup */}
                {preview && preview.show && (
                    <div style={{
                        position: 'fixed',
                        left: preview.x - 150, // Center horizontally relative to mouse
                        top: preview.y,
                        width: '320px',
                        height: '200px',
                        backgroundColor: 'rgba(0,0,0,0.9)',
                        borderRadius: '15px',
                        border: '2px solid var(--flowkitgreen)',
                        zIndex: 1000,
                        display: 'flex',
                        padding: '10px',
                        gap: '10px',
                        pointerEvents: 'none' // Let clicks pass through if needed, though usually popup blocks
                    }}>
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <span style={{ fontSize: '12px', color: '#888', marginBottom: '5px' }}>Current</span>
                            <video
                                ref={previewCurrentRef}
                                src={`http://localhost:8000/videos/${currentVideo}`}
                                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '5px' }}
                                muted
                                loop
                            />
                        </div>
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <span style={{ fontSize: '12px', color: 'var(--flowkitgreen)', marginBottom: '5px' }}>Next</span>
                            <video
                                ref={previewTargetRef}
                                src={`http://localhost:8000/videos/${preview.targetVideo}`}
                                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '5px' }}
                                muted
                                loop
                            />
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default Manual;
