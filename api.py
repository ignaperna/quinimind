
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from constants import DEFAULT_MODALIDAD, NUMBERS_PER_DRAW
from database import Sorteo, session_scope
import analisis
import draws
import scrape_quini6

app = FastAPI(title="QuiniMind API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "system": "QuiniMind AI"}

@app.get("/update")
def trigger_update():
    """Manually triggers the scraper to check for new results."""
    try:
        scrape_quini6.run_scraper()
        return {"status": "success", "message": "Database updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/latest")
def get_latest_draw():
    """Returns the most recent draw (sorteo) with all modalities."""
    with session_scope() as session:
        # Assuming higher ID is newer. We need to group by ID.
        latest_id = session.query(Sorteo.sorteo_id).order_by(Sorteo.sorteo_id.desc()).first()
        
        if not latest_id:
            return {"error": "No data found"}
            
        sorteo_id = latest_id[0]
        
        # Get all entries for this ID (different modalities)
        sorteos = session.query(Sorteo).filter(Sorteo.sorteo_id == sorteo_id).all()
        
        result = {
            "id": sorteo_id,
            "date": sorteos[0].fecha if sorteos else "Unknown",
            "modes": {}
        }
        
        for sorteo in sorteos:
            result["modes"][draws.mode_key(sorteo.modalidad)] = draws.numbers_of_sorteo(sorteo)
            
        return result

@app.get("/history")
def get_history(limit: int = 50):
    """Returns history of draws for statistics."""
    with session_scope() as session:
        # Get distinct draw IDs ordered descending
        unique_ids = session.query(Sorteo.sorteo_id, Sorteo.fecha).distinct().order_by(Sorteo.sorteo_id.desc()).limit(limit).all()
        
        history = []
        for sid, date in unique_ids:
            # For stats, we usually aggregate numbers from all modalities or just Tradicional
            # Let's aggregate all numbers for this draw ID into one flat list for simplicity in this visualizer
            sorteos = session.query(Sorteo).filter(Sorteo.sorteo_id == sid).all()
            all_numbers = []
            for sorteo in sorteos:
                all_numbers.extend(draws.numbers_of_sorteo(sorteo))
            
            # Remove duplicates if any (unlikely across modalities but possible)
            # Actually for frequency stats we keep them all.
            # But for "numbers" display we might want a representative set? 
            # The User's React code expects `numbers: [...]` (Array of 6).
            # It seems the mockup history was just random 6 numbers.
            # Let's return just the Tradicional numbers as the "representative" set for the history list view.
            trad = next((s for s in sorteos if "TRADICIONAL" in s.modalidad.upper()), None)
            if trad:
                nums = draws.numbers_of_sorteo(trad)
            else:
                nums = all_numbers[:NUMBERS_PER_DRAW] # Fallback
                
            history.append({
                "id": sid,
                "date": date,
                "numbers": nums
            })
            
        return history

@app.get("/stats/heatmap")
def get_heatmap(modalidad: str = DEFAULT_MODALIDAD):
    """Returns heatmap data."""
    df = analisis.get_heatmap_data(modalidad.upper())
    if df.empty:
        return []
    return df.to_dict(orient="records")

@app.get("/predict")
def get_prediction(modalidad: str = DEFAULT_MODALIDAD):
    """Generates a prediction."""
    return analisis.get_prediction(modalidad.upper())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
