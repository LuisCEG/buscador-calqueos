import streamlit as st
import json
import zipfile

# Configuración de la página
st.set_page_config(page_title="Buscador - Gobierno de Dios", page_icon="🛡️", layout="wide")

# --- ESTILOS CSS INSTITUCIONALES ---
st.markdown("""
<style>
    /* Fondo sutil y elegante */
    .stApp {
        background-color: #f4f6f9;
    }
    /* Títulos en Azul Marino */
    h1, h2, h3 {
        color: #0B1C4A !important;
        font-family: 'Times New Roman', Times, serif;
        text-align: center;
    }
    /* Subtítulos Dorados */
    .subtitulo {
        color: #B8860B;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    /* Bordes dorados en la caja de búsqueda */
    .stTextInput>div>div>input {
        border: 2px solid #B8860B;
        border-radius: 8px;
        padding: 10px;
        font-size: 1.1rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #0B1C4A;
        box-shadow: 0 0 5px rgba(11, 28, 74, 0.5);
    }
    /* Diseño de los mensajes de alerta */
    .stAlert {
        border-left: 5px solid #B8860B;
    }
    /* Tarjetas de resultados */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-top: 3px solid #0B1C4A;
        border-bottom: 3px solid #B8860B;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- ENCABEZADO INSTITUCIONAL ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    try:
        # Aquí cargamos la imagen del escudo que vas a subir
        st.image("escudo.jpeg", use_container_width=True)
    except Exception:
        pass

st.markdown("<h1>Buscador Global de Calqueos</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>CRECIENDO EN GRACIA • GOBIERNO DE DIOS EN LA TIERRA</div>", unsafe_allow_html=True)

# --- MOTOR DE BÚSQUEDA ---
@st.cache_data(show_spinner=False)
def cargar_base_datos():
    try:
        with zipfile.ZipFile('bd_calqueos.zip', 'r') as z:
            with z.open('bd_calqueos.json') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return []

with st.spinner('Cargando la base de datos global...'):
    base_de_datos = cargar_base_datos()

if not base_de_datos:
    st.stop()

# Interfaz de búsqueda
st.info(f"🛡️ **Base de datos institucional activa:** {len(base_de_datos)} calqueos indexados en la red.")
frase_busqueda = st.text_input("", placeholder="🔍 Ingresa la palabra o frase a buscar (Ejemplo: Bendecidos entienden)")

if frase_busqueda:
    frase_limpia = frase_busqueda.strip().lower()
    resultados_encontrados = []
    
    with st.spinner('Buscando en los archivos del Reino...'):
        for video in base_de_datos:
            for bloque in video.get("transcripcion", []):
                texto_original = bloque.get("text", "")
                
                if frase_limpia in texto_original.lower():
                    segundos_totales = int(bloque.get("start", 0))
                    minutos = segundos_totales // 60
                    segundos = segundos_totales % 60
                    tiempo_formateado = f"{minutos}:{segundos:02d}"
                    
                    enlace_youtube = f"https://youtu.be/{video['video_id']}?t={segundos_totales}"
                    
                    resultados_encontrados.append({
                        "titulo": video["titulo"],
                        "texto": texto_original,
                        "tiempo": tiempo_formateado,
                        "enlace": enlace_youtube
                    })

    # Mostrar Resultados
    if resultados_encontrados:
        st.markdown(f"<h3 style='text-align: left; color: #0B1C4A;'>🔍 Se encontraron {len(resultados_encontrados)} menciones:</h3>", unsafe_allow_html=True)
        
        for res in resultados_encontrados:
            with st.container():
                st.markdown(f"**🎥 {res['titulo']}**")
                st.markdown(f"⏱️ **Minuto {res['tiempo']}** — *\"...{res['texto']}...\"*")
                st.markdown(f"[▶️ Ver el video en el minuto exacto]({res['enlace']})")
    else:
        st.warning("No se encontraron coincidencias para esa frase. Intenta buscar una palabra más corta o sin tildes.")
