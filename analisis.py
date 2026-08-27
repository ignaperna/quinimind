
import pandas as pd
import random
from constants import ALL_NUMBERS, NUMBERS_PER_DRAW
from database import engine
import draws

def get_data(modalidad):
    """Loads draw data for a specific modality into a DataFrame."""
    query = f"SELECT * FROM sorteos WHERE modalidad = '{modalidad}'"
    df = pd.read_sql(query, engine)
    return df

def get_hot_numbers(modalidad, last_n=50):
    """
    Returns the top 10 most frequent numbers in the last N draws.
    """
    df = get_data(modalidad)
    if df.empty:
        return []

    # Sort by date/id descending to get recent ones
    # Assuming higher ID = more recent
    df = df.sort_values(by='sorteo_id', ascending=False).head(last_n)

    # Count frequencies over the flattened number columns
    hot_counts = draws.melt_numbers(df).value_counts().head(10)
    return hot_counts.index.tolist()

def get_cold_numbers(modalidad):
    """
    Returns the top 10 numbers that haven't appeared for the longest time.
    """
    df = get_data(modalidad)
    if df.empty:
        return []

    last_seen_id, _ = draws.last_seen(df)

    # Check numbers never seen
    never_seen = [n for n in ALL_NUMBERS if n not in last_seen_id]
    
    # Check numbers seen but long ago
    seen_list = [(n, last_seen_id[n]) for n in last_seen_id]
    seen_list.sort(key=lambda x: x[1]) # Ascending sort by ID
    
    coldest = never_seen + [x[0] for x in seen_list]
    
    return coldest[:10]

def get_heatmap_data(modalidad):
    """
    Returns a DataFrame with stats for ALL numbers (0-45).
    Columns: Numero, Frecuencia, UltimoSorteoId, UltimaFecha
    """
    df = get_data(modalidad)
    if df.empty:
        return pd.DataFrame()

    # 1. Calculate Frequency (Total)
    freq_counts = draws.melt_numbers(df).value_counts()

    # 2. Calculate Last Seen
    last_seen_id, last_seen_date = draws.last_seen(df)

    # 3. Build Result DataFrame
    stats = []
    current_max_id = df['sorteo_id'].max()

    for n in ALL_NUMBERS:
        frec = freq_counts.get(n, 0)
        l_id = last_seen_id.get(n, -1)
        l_date = last_seen_date.get(n, "Nunca")
        
        # Calculate "Delay" (Retraso)
        delay = (current_max_id - l_id) if l_id != -1 else 999

        stats.append({
            'Numero': n,
            'Frecuencia': frec,
            'UltimoSorteo': l_id,
            'FechaUltima': l_date,
            'Retraso': delay
        })
    
    return pd.DataFrame(stats)

def get_prediction(modalidad):
    """
    Generates a prediction: 3 Hot, 2 Cold, 1 Random.
    Ensures unique numbers.
    """
    hot = get_hot_numbers(modalidad)
    cold = get_cold_numbers(modalidad)
    
    prediction = set()
    
    # 1. Pick 3 Hot
    hot_candidates = [n for n in hot if n not in prediction]
    prediction.update(hot_candidates[:3])
    
    # 2. Pick 2 Cold
    cold_candidates = [n for n in cold if n not in prediction]
    prediction.update(cold_candidates[:2])
    
    # 3. Fill the rest with Random (need total 6)
    while len(prediction) < NUMBERS_PER_DRAW:
        pick = random.choice(ALL_NUMBERS)
        prediction.add(pick)
        
    return sorted(list(prediction))

if __name__ == "__main__":
    # verification/test block
    MOD = "TRADICIONAL"
    print(f"--- Analysis for {MOD} ---")
    # print("Heatmap Sample:\n", get_heatmap_data(MOD).head())
