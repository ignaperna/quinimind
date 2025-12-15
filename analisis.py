
import pandas as pd
import random
from sqlalchemy.orm import sessionmaker
from database import engine, Sorteo

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

    # Melt the number columns into a single Series
    numbers = pd.melt(df, value_vars=['n1', 'n2', 'n3', 'n4', 'n5', 'n6'])['value']
    
    # Count frequencies
    hot_counts = numbers.value_counts().head(10)
    return hot_counts.index.tolist()

def get_cold_numbers(modalidad):
    """
    Returns the top 10 numbers that haven't appeared for the longest time.
    """
    df = get_data(modalidad)
    if df.empty:
        return []

    # Sort by ID ascending (oldest to newest) to iterate properly
    df = df.sort_values(by='sorteo_id', ascending=True)

    last_seen = {}
    
    # Iterate through all draws to update the last seen ID for each number
    for _, row in df.iterrows():
        current_id = row['sorteo_id']
        nums = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
        for n in nums:
            last_seen[n] = current_id

    all_numbers = list(range(46)) 
    
    # Check numbers never seen
    never_seen = [n for n in all_numbers if n not in last_seen]
    
    # Check numbers seen but long ago
    seen_list = [(n, last_seen[n]) for n in last_seen]
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
    melted = pd.melt(df, value_vars=['n1', 'n2', 'n3', 'n4', 'n5', 'n6'])
    freq_counts = melted['value'].value_counts()

    # 2. Calculate Last Seen
    df_sorted = df.sort_values(by='sorteo_id', ascending=True)
    last_seen_id = {}
    last_seen_date = {}

    for _, row in df_sorted.iterrows():
        draw_id = row['sorteo_id']
        date_val = row['fecha']
        nums = [row['n1'], row['n2'], row['n3'], row['n4'], row['n5'], row['n6']]
        for n in nums:
            last_seen_id[n] = draw_id
            last_seen_date[n] = date_val

    # 3. Build Result DataFrame
    stats = []
    current_max_id = df['sorteo_id'].max()

    for n in range(46):
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
    
    # All possible numbers for random selection
    all_numbers = list(range(46))
    
    prediction = set()
    
    # 1. Pick 3 Hot
    hot_candidates = [n for n in hot if n not in prediction]
    prediction.update(hot_candidates[:3])
    
    # 2. Pick 2 Cold
    cold_candidates = [n for n in cold if n not in prediction]
    prediction.update(cold_candidates[:2])
    
    # 3. Fill the rest with Random (need total 6)
    while len(prediction) < 6:
        pick = random.choice(all_numbers)
        prediction.add(pick)
        
    return sorted(list(prediction))

if __name__ == "__main__":
    # verification/test block
    MOD = "TRADICIONAL"
    print(f"--- Analysis for {MOD} ---")
    # print("Heatmap Sample:\n", get_heatmap_data(MOD).head())
