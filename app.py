
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import time
import numpy as np
import scrape_quini6
import analisis
from database import engine

# ------------------------------------------------------
# 1. CONFIGURACIÓN Y ESTILOS CSS MEJORADOS (V2)
# ------------------------------------------------------
st.set_page_config(page_title="QuiniMind Elite V2", page_icon="💎", layout="wide")

st.markdown("""
<style>
    /* --- FONDO ANIMADO --- */
    .stApp {
        background: linear-gradient(-45deg, #020024, #090979, #1f1c6b, #00d4ff);
        background-size: 400% 400%;
        animation: gradient 20s ease infinite;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* --- GLASSMORPHISM CARDS (ARREGLO DE TIPOGRAFÍA AQUÍ) --- */
    .glass-card {
        background: rgba(20, 20, 40, 0.6); /* Más oscuro para mejor contraste */
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        margin-bottom: 25px;
        color: #ffffff !important; /* FORZAMOS TEXTO BLANCO */
    }

    /* --- FUENTES Y TÍTULOS --- */
    h1, h2, h3, .metric-label {
        font-family: 'Montserrat', sans-serif;
        color: #ffffff !important;
        text-shadow: 0 0 15px rgba(0, 200, 255, 0.8);
    }

    /* ARREGLO CRÍTICO: Hacer legibles los Radio Buttons y Selectboxes de Streamlit */
    .stRadio > label, .stSelectbox > label {
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    /* Color del texto de las opciones del radio button */
    .stRadio div[role='radiogroup'] > label > div:first-of-type {
        color: #E0E0E0 !important;
    }

    /* --- BOTÓN "RADIOACTIVO" --- */
    /* Hack para estilizar el botón primario de Streamlit */
    div[data-testid="stButton"] > button {
        width: 100%;
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 18px;
        font-weight: bold;
        border-radius: 50px;
        box-shadow: 0 5px 15px rgba(242, 71, 61, 0.6);
        transition: all 0.3s ease 0s;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%);
        box-shadow: 0 10px 25px rgba(242, 71, 61, 0.9), 0 0 50px rgba(242, 71, 61, 0.4);
        transform: translateY(-3px);
    }

    /* --- BOLAS DE LOTERÍA 3D --- */
    .ball {
        display: inline-block;
        width: 65px;
        height: 65px;
        line-height: 65px;
        border-radius: 50%;
        /* Degradado dorado metálico */
        background: radial-gradient(ellipse at center, #ffdb4d 0%,#f7c52d 30%,#e0a613 60%,#b58205 100%);
        color: #2c2c2c;
        font-weight: 900;
        font-size: 26px;
        text-align: center;
        margin: 8px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4), inset 0 2px 5px rgba(255,255,255,0.7);
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
        animation: pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    @keyframes pop {
        0% { transform: scale(0) rotate(-180deg); opacity: 0;}
        100% { transform: scale(1) rotate(0deg); opacity: 1;}
    }

    /* Estilos para métricas personalizadas neón */
    .neon-metric-hot { color: #FF3333; font-weight: bold; text-shadow: 0 0 10px #FF3333; font-size: 1.2rem;}
    .neon-metric-cold { color: #33FFFF; font-weight: bold; text-shadow: 0 0 10px #33FFFF; font-size: 1.2rem;}
    
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# 2. FUNCIONES (MOCKUP MEJORADO -> INTEGRACIÓN REAL)
# ------------------------------------------------------

# --- Sidebar Control for DB Update ---
with st.sidebar:
    st.header("⚙️ Admin")
    if st.button("🔄 Sincronizar DB", use_container_width=True):
        with st.spinner("Conectando al servidor..."):
            try:
                scrape_quini6.main()
                st.success("¡Datos Actualizados!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ------------------------------------------------------
# 3. INTERFAZ PRINCIPAL V2
# ------------------------------------------------------

# Header con Glow
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<h1>💎 QUINIMIND <span style="color:#00d4ff">ELITE</span></h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#B0B0B0; font-size:1.1rem;">Inteligencia Artificial Predictiva v2.1 (Live Data)</p>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align: right; padding-top: 20px;"><span style="background-color: #00ff00; box-shadow: 0 0 10px #00ff00; border-radius: 50%; display: inline-block; width: 10px; height: 10px; margin-right: 8px;"></span><span style="color:white; font-weight:bold;">SISTEMA ONLINE</span></div>', unsafe_allow_html=True)

st.divider()

# --- SECCIÓN 1: EL TABLERO TÉRMICO NEÓN ---
st.markdown('<div class="glass-card"><h3>🔥 Mapa Térmico de Frecuencias (Histórico)</h3>', unsafe_allow_html=True)
st.markdown('<p style="color:#E0E0E0">Análisis visual del comportamiento histórico de las bolillas en base a datos reales.</p>', unsafe_allow_html=True)

# Selectbox para el Heatmap (usando el estilo corregido)
heatmap_modalidad = st.selectbox("Seleccionar Modalidad de Análisis:", ["TRADICIONAL", "LA SEGUNDA", "REVANCHA", "SIEMPRE SALE"])

# DATOS REALES
df_freq = analisis.get_heatmap_data(heatmap_modalidad)

if not df_freq.empty:
    z_values = np.full((5, 10), np.nan)
    text_values = np.full((5, 10), "", dtype=object)
    hover_text = np.full((5, 10), "", dtype=object)

    for index, row in df_freq.iterrows():
        num = int(row['Numero'])
        freq = int(row['Frecuencia'])
        delay = int(row['Retraso'])
        
        r = num // 10
        c = num % 10
        if r < 5:
            num_str = str(num).zfill(2)
            z_values[r][c] = freq
            text_values[r][c] = num_str
            status = "ARDIEENDO 🔥" if freq > 10 else ("CONGELADO ❄️" if delay > 20 else "Normal")
            hover_text[r][c] = f"Bolilla: {num_str}<br>Frecuencia: {freq}<br>Retraso: {delay}<br>Estado: {status}"

    # Crear gráfico Plotly con NUEVA ESCALA DE COLOR VIBRANTE
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=[f"C{i}" for i in range(10)],
        y=[f"F{i}" for i in range(5)],
        text=text_values,
        hovertext=hover_text,
        hoverinfo="text",
        texttemplate="%{text}",
        textfont={"size": 22, "color": "white", "family": "Arial Black"},
        hoverongaps=False,
        # Escala de color personalizada
        colorscale=[
            [0.0, 'rgb(0, 20, 100)'],    # Azul muy oscuro
            [0.2, 'rgb(0, 200, 255)'],   # Cian brillante
            [0.5, 'rgb(255, 255, 0)'],   # Amarillo
            [0.8, 'rgb(255, 100, 0)'],   # Naranja
            [1.0, 'rgb(255, 0, 50)']     # Rojo neón
        ],
        showscale=False,
        xgap=4,
        ygap=4
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=320,
        xaxis=dict(showticklabels=False, showgrid=False, fixedrange=True),
        yaxis=dict(showticklabels=False, showgrid=False, autorange="reversed", fixedrange=True)
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("No hay datos disponibles. Por favor actualiza la base de datos.")

st.markdown('</div>', unsafe_allow_html=True)


# --- SECCIÓN 2: PREDICCIÓN ESTRATÉGICA ---
col_pred, col_stats = st.columns([4, 3], gap="large")

with col_pred:
    st.markdown('<div class="glass-card" style="border: 2px solid rgba(255, 215, 0, 0.3);">', unsafe_allow_html=True)
    st.markdown('<h3>🔮 Oráculo IA: Generador Cuántico</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#B0B0B0; margin-bottom:20px;">Selecciona el objetivo y deja que la red neuronal trabaje.</p>', unsafe_allow_html=True)
    
    # Usamos radio horizontal
    pred_modalidad = st.radio("Modalidad Objetivo:", 
                         ["TRADICIONAL", "LA SEGUNDA", "REVANCHA", "SIEMPRE SALE"],
                         horizontal=True)
    
    st.write("") # Espacio
    
    # BOTÓN "RADIOACTIVO"
    if st.button("⚡ INVOCAR JUGADA MAESTRA ⚡", type="primary", use_container_width=True):
        with st.spinner("Iniciando secuencia de cálculo probabilístico..."):
            # Simulación de proceso
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.015)
                progress_bar.progress(i + 1)
            time.sleep(0.5)
            progress_bar.empty()
            
            # Generar números REALES
            try:
                nums = analisis.get_prediction(pred_modalidad)
                
                # Renderizar HTML de las bolas MEJORADAS
                html_balls = "".join([f'<div class="ball">{n:02d}</div>' for n in nums])
                
                st.markdown(f"""
                <div style="text-align:center; margin-top:30px; margin-bottom:20px;">
                    {html_balls}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                    <div style="background: rgba(0,255,0,0.1); border-left: 4px solid #00ff00; padding: 15px;">
                        <strong style="color:#00ff00;">✅ Análisis Finalizado:</strong> 
                        <span style="color:white;">La combinación maximiza la varianza entre decenas y respeta la Ley del Retraso actual.</span>
                    </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error("Error al generar predicción. Verifica los datos.")
            
    st.markdown('</div>', unsafe_allow_html=True)

with col_stats:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3>📊 Métricas de Tendencia (Live)</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#E0E0E0; margin-bottom:25px;">Datos en tiempo real del motor estadístico.</p>', unsafe_allow_html=True)
    
    # Obtener métricas reales
    hot_now = analisis.get_hot_numbers(heatmap_modalidad)
    cold_now = analisis.get_cold_numbers(heatmap_modalidad)
    
    val_hot = hot_now[0] if hot_now else "-"
    val_cold = cold_now[0] if cold_now else "-"

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="text-align:center;">Isótopo 🔥 (Más sale)</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 3.5rem; font-weight:900; text-align:center; color:#FF4B2B; text-shadow: 0 0 20px rgba(255, 75, 43, 0.8);">{val_hot}</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;" class="neon-metric-hot">↑ Alta Frecuencia</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="text-align:center;">Criogénico ❄️ (No sale)</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 3.5rem; font-weight:900; text-align:center; color:#00d4ff; text-shadow: 0 0 20px rgba(0, 212, 255, 0.8);">{val_cold}</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;" class="neon-metric-cold">↓ Retraso Alto</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("**Confianza del Algoritmo:**")
    # Barra de progreso personalizada (verde neón)
    st.markdown("""
        <div style="width:100%; background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 3px;">
            <div style="width: 88%; height: 12px; background: linear-gradient(90deg, #00ff00, #adff2f); border-radius: 8px; box-shadow: 0 0 10px #00ff00;"></div>
        </div>
        <div style="text-align:right; color:#00ff00; font-weight:bold; margin-top:5px;">88.4% Optimizada</div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
