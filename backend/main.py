!pip install ollama fastapi uvicorn python-multipart
from dotenv import load_dotenv
load_dotenv()
import os
import shutil
import asyncio
import ollama  # The engine for Gemma 4
from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 1. Add this at the top of main.py to read environment variables
NODE_ID = os.getenv("GFS4_NODE_ID", "GFS4_GENERIC_NODE")


app = FastAPI(title="GFS4 Global Node")

# Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Physical Storage Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_ROOT = os.path.join(BASE_DIR, "gfs4_data")
STAGING = os.path.join(STORAGE_ROOT, "staging")
VAULT = os.path.join(STORAGE_ROOT, "vault")

for path in [STAGING, VAULT]:
    os.makedirs(path, exist_ok=True)

async def g4_sieve_agent(filename: str):
    """
    GFS4 AGENT: Calls Gemma 4 to analyze the file intent.
    """
    source_path = os.path.join(STAGING, filename)
    
    # System Instruction for the Sieve Agent
    prompt = f"""
    Analyze the filename: '{filename}'
    You are the GFS4 Sentinel. Determine if this file contains sensitive, 
    private, or high-priority data (e.g., financial, keys, legal, identity).
    
    Return ONLY one word: 'VAULT' or 'STAGING'.
    """

    try:
        # Calling the local Gemma 4 E2B model
        response = ollama.generate(model='gemma4:e2b', prompt=prompt)
        decision = response['response'].strip().upper()

        if "VAULT" in decision:
            dest_path = os.path.join(VAULT, filename)
            shutil.move(source_path, dest_path)
            print(f"[G4-SENTINEL] Reasoning complete: {filename} -> VAULT")
        else:
            print(f"[G4-SIEVE] Reasoning complete: {filename} -> STAGING")
            
    except Exception as e:
        print(f"[ERROR] Gemma 4 Inference Failed: {e}")

@app.post("/ingest")
async def ingest_file(file: UploadFile, background_tasks: BackgroundTasks):
    try:
        file_location = os.path.join(STAGING, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        # Hand off to the G4 Sieve Agent asynchronously
        background_tasks.add_task(g4_sieve_agent, file.filename)
        
        return {"status": "success", "message": f"G4-Sentinel is analyzing {file.filename}..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 1. Add this at the top of main.py to read environment variables
NODE_ID = os.getenv("GFS4_NODE_ID", "GFS4_GENERIC_NODE")

@app.get("/status")
async def get_node_status():
    """
    Returns the real-time status of the specific GFS4 Node.
    """
    return {
        "node": NODE_ID,  # Now dynamic!
        "vault_count": len(os.listdir(VAULT)),
        "staging_count": len(os.listdir(STAGING)),
        "system_status": "OPERATIONAL"
    }
