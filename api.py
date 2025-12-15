
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from database import engine, Sorteo
import analisis
import scrape_quini6
import pandas as pd
from typing import List, Dict, Any

app = FastAPI(title="QuiniMind API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Session = sessionmaker(bind=engine)

@app.get("/")
def read_root():
    return {"status": "online", "system": "QuiniMind AI"}

@app.get("/update")
def trigger_update():
    """Manually triggers the scraper to check for new results."""
    try:
        scrape_quini6.main()
        return {"status": "success", "message": "Database updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/latest")
def get_latest_draw():
    """Returns the most recent draw (sorteo) with all modalities."""
    session = Session()
    try:
        # Assuming higher ID is newer. We need to group by ID.
        latest_id = session.query(Sorteo.sorteo_id).order_by(Sorteo.sorteo_id.desc()).first()
        
        if not latest_id:
            return {"error": "No data found"}
            
        sorteo_id = latest_id[0]
        
        # Get all entries for this ID (different modalities)
        draws = session.query(Sorteo).filter(Sorteo.sorteo_id == sorteo_id).all()
        
        result = {
            "id": sorteo_id,
            "date": draws[0].fecha if draws else "Unknown",
            "modes": {}
        }
        
        for draw in draws:
            # Normalize modality name to camelCase key
            key = "tradicional"
            if "SEGUNDA" in draw.modalidad.upper(): key = "laSegunda"
            elif "REVANCHA" in draw.modalidad.upper(): key = "revancha"
            elif "SIEMPRE" in draw.modalidad.upper(): key = "siempreSale"
            
            result["modes"][key] = [draw.n1, draw.n2, draw.n3, draw.n4, draw.n5, draw.n6]
            
        return result
    finally:
        session.close()

@app.get("/history")
def get_history(limit: int = 50):
    """Returns history of draws for statistics."""
    session = Session()
    try:
        # Get distinct draw IDs ordered descending
        unique_ids = session.query(Sorteo.sorteo_id, Sorteo.fecha).distinct().order_by(Sorteo.sorteo_id.desc()).limit(limit).all()
        
        history = []
        for sid, date in unique_ids:
            # For stats, we usually aggregate numbers from all modalities or just Tradicional
            # Let's aggregate all numbers for this draw ID into one flat list for simplicity in this visualizer
            draws = session.query(Sorteo).filter(Sorteo.sorteo_id == sid).all()
            all_numbers = []
            for d in draws:
                all_numbers.extend([d.n1, d.n2, d.n3, d.n4, d.n5, d.n6])
            
            # Remove duplicates if any (unlikely across modalities but possible)
            # Actually for frequency stats we keep them all.
            # But for "numbers" display we might want a representative set? 
            # The User's React code expects `numbers: [...]` (Array of 6).
            # It seems the mockup history was just random 6 numbers.
            # Let's return just the Tradicional numbers as the "representative" set for the history list view.
            trad = next((d for d in draws if "TRADICIONAL" in d.modalidad.upper()), None)
            if trad:
                nums = [trad.n1, trad.n2, trad.n3, trad.n4, trad.n5, trad.n6]
            else:
                nums = all_numbers[:6] # Fallback
                
            history.append({
                "id": sid,
                "date": date,
                "numbers": nums
            })
            
        return history
    finally:
        session.close()

@app.get("/stats/heatmap")
def get_heatmap(modalidad: str = "TRADICIONAL"):
    """Returns heatmap data."""
    df = analisis.get_heatmap_data(modalidad.upper())
    if df.empty:
        return []
    return df.to_dict(orient="records")

@app.get("/predict")
def get_prediction(modalidad: str = "TRADICIONAL"):
    """Generates a prediction."""
    return analisis.get_prediction(modalidad.upper())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
