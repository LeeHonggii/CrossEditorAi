import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import json

# Import refactored logic from main.py
from main import analyze_videos, render_video, get_video_files, VIDEO_EXTENSIONS
import numpy as np

def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {str(k): convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy(i) for i in obj)
    return obj

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
# Since we moved everything to server/, these should be relative to the current working directory when running server.py
# We assume server.py is run from the server/ directory or we adjust accordingly.
# Best practice: use absolute paths based on __file__
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = BASE_DIR

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RenderRequest(BaseModel):
    # For manual rendering, we might need to pass specific transition points
    # For now, we'll just trigger the default render logic based on previous analysis
    # In a full manual mode, this would accept a list of transition points
    pass

@app.post("/upload")
async def upload_videos(files: List[UploadFile] = File(...)):
    # Clear existing videos in data directory to ensure clean state for new session
    # Note: In a production multi-user env, we'd use session IDs or separate folders
    for f in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, f)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)
    
    return {"message": "Files uploaded successfully", "files": saved_files}

@app.post("/process/auto")
async def process_auto():
    video_files = get_video_files(UPLOAD_DIR, VIDEO_EXTENSIONS)
    if not video_files:
        raise HTTPException(status_code=400, detail="No video files found. Please upload videos first.")

    try:
        # Step 1: Analyze
        analysis_results = analyze_videos(video_files)
        if analysis_results[0] is None:
             raise HTTPException(status_code=500, detail="Analysis failed or no transition points found.")
        
        n_frame_similarities, n_frame_count, verified_matches, video_files, csv_files, video_file_mapping, best_vectors = analysis_results

        # Step 2: Render
        output_video = render_video(n_frame_similarities, n_frame_count, verified_matches, video_files, csv_files, video_file_mapping, best_vectors)
        
        return {"message": "Processing complete", "video_url": f"/result/{output_video}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/analyze")
async def process_analyze():
    video_files = get_video_files(UPLOAD_DIR, VIDEO_EXTENSIONS)
    if not video_files:
        raise HTTPException(status_code=400, detail="No video files found. Please upload videos first.")

    try:
        analysis_results = analyze_videos(video_files)
        if analysis_results[0] is None:
             raise HTTPException(status_code=500, detail="Analysis failed or no transition points found.")
        
        n_frame_similarities, n_frame_count, verified_matches, video_files, csv_files, video_file_mapping, best_vectors = analysis_results
        
        # Serialize data for frontend visualization
        # We need to convert keys (frame numbers) to strings for JSON compatibility if they aren't already
        # And ensure tuples are lists
        
        # Save intermediate data for the render step (in a real app, use a database or cache)
        # For this single-user demo, we can rely on re-running analyze or saving to a temp file
        # To keep it simple, we'll save to a pickle or just rely on the frontend passing data back? 
        # Actually, passing complex data back and forth is risky. 
        # Save state for rendering
        import pickle
        with open("analysis_state.pkl", "wb") as f:
            pickle.dump({
                "n_frame_similarities": n_frame_similarities,
                "n_frame_count": n_frame_count,
                "verified_matches": verified_matches,
                "video_files": video_files,
                "csv_files": csv_files,
                "video_file_mapping": video_file_mapping,
                "best_vectors": best_vectors
            }, f)

        # Convert frame_similarities to use video basenames instead of CSV filenames
        # video_file_mapping maps CSV path -> Video path
        frontend_frame_similarities = {}
        
        # Create a quick lookup for csv_basename -> video_basename
        csv_to_video_name = {}
        for csv_path, video_path in video_file_mapping.items():
            csv_to_video_name[os.path.basename(csv_path)] = os.path.basename(video_path)
            
        for frame, matches in n_frame_similarities.items():
            new_matches = []
            for pair in matches:
                # pair is [csv1, csv2] (could be full paths or basenames depending on main.py)
                # main.py usually returns full paths in similar_files
                
                f1 = os.path.basename(pair[0])
                f2 = os.path.basename(pair[1])
                
                v1 = csv_to_video_name.get(f1, f1)
                v2 = csv_to_video_name.get(f2, f2)
                
                new_matches.append([v1, v2])
            frontend_frame_similarities[frame] = new_matches

        response_data = {
            "message": "Analysis complete",
            "frame_similarities": frontend_frame_similarities, 
            "frame_count": n_frame_count,
            "video_files": [os.path.basename(f) for f in video_files]
        }
        
        return convert_numpy(response_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class RenderRequest(BaseModel):
    sequence: list = None # Optional list of {video: str, start: float}

@app.post("/process/render")
async def process_render(request: RenderRequest = None):
    try:
        import pickle
        if not os.path.exists("analysis_state.pkl"):
             raise HTTPException(status_code=400, detail="Analysis data not found. Please upload and analyze videos first.")
        
        with open("analysis_state.pkl", "rb") as f:
            state = pickle.load(f)
            
        custom_order = None
        if request and request.sequence:
            print(f"Received manual sequence: {request.sequence}")
            # Convert sequence to max_transformation_order format: (frame, start_csv, end_csv)
            # sequence is [{video: basename, start: seconds}, ...]
            
            # Create reverse mapping: basename -> csv_file
            # state['video_file_mapping'] maps csv_path -> video_path
            video_to_csv = {}
            for csv_path, video_path in state['video_file_mapping'].items():
                video_basename = os.path.basename(video_path)
                video_to_csv[video_basename] = csv_path
                
            custom_order = []
            FPS = 24 # Assuming 24 FPS as per main.py
            
            for i in range(1, len(request.sequence)):
                prev_seg = request.sequence[i-1]
                curr_seg = request.sequence[i]
                
                frame = int(float(curr_seg['start']) * FPS)
                start_video = prev_seg['video']
                end_video = curr_seg['video']
                
                if start_video in video_to_csv and end_video in video_to_csv:
                    start_csv = video_to_csv[start_video]
                    end_csv = video_to_csv[end_video]
                    custom_order.append((frame, start_csv, end_csv))
                else:
                    print(f"Warning: Could not map video files {start_video} or {end_video}")

        # Handle single video case (no transitions)
        if request and request.sequence and len(request.sequence) == 1:
             print("Single video sequence detected. Returning original video.")
             video_name = request.sequence[0]['video']
             return {"message": "Video rendered successfully", "video_url": f"/videos/{video_name}"}

        output_json, output_video = render_video(
            state['n_frame_similarities'],
            state['n_frame_count'],
            state['verified_matches'],
            state['video_files'],
            state['csv_files'],
            state['video_file_mapping'],
            state['best_vectors'],
            output_json=os.path.join(OUTPUT_DIR, "output_pose.json"),
            output_video=os.path.join(OUTPUT_DIR, "combined_video.mp4"),
            custom_order=custom_order
        )
        
        return {"message": "Video rendered successfully", "video_url": f"/result/{os.path.basename(output_video)}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/result/{filename}")
async def get_result(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/videos/{filename}")
async def get_source_video(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
