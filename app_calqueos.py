import streamlit as st
import json
import zipfile

# Configuración de la página
st.set_page_config(page_title="Buscador - Gobierno de Dios", page_icon="🛡️", layout="wide")

# --- ESTILOS CSS MODO OSCURO INSTITUCIONAL ---
st.markdown("""
<style>
    /* Fondo oscuro elegante y descansado para la vista */
    .stApp {
        background-color: #051024;
    }
    /* Color del texto general */
    .stMarkdown, p {
        color: #E2E8F0;
    }
    /* Títulos en Dorado */
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Times New Roman', Times, serif;
        text-align: center;
    }
    /* Subtítulos */
    .subtitulo {
        color: #E2C275;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }
    /* Caja de búsqueda */
    .stTextInput>div>div>input {
        background-color: #0A1931;
        color: #FFFFFF;
        border: 2px solid #D4AF37;
        border-radius: 8px;
        padding: 12px;
        font-size: 1.1rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #E2C275;
        box-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
    }
    /* Tarjetas de resultados limpias (HTML puro para evitar las cajas blancas) */
    .resultado-card {
        background-color: #0A1931;
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 5px solid #D4AF37;
        margin-bottom: 15px;
        border-right: 1px solid #1A2B4C;
        border-top: 1px solid #1A2B4C;
        border-bottom: 1px solid #1A2B4C;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .resultado-card a {
        color: #4DA8DA;
        text-decoration: none;
        font-weight: bold;
    }
    .resultado-card a:hover {
        text-decoration: underline;
        color: #63B3ED;
    }
</style>
""", unsafe_allow_html=True)

# --- ENCABEZADO INSTITUCIONAL ---
# Ajustamos las proporciones para que el escudo quede de un tamaño perfecto y sin cajas
col1, col2, col3 = st.columns([1.5, 1, 1.5])
with col2:
    try:
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

with st.spinner('Cargando los archivos del Reino...'):
    base_de_datos = cargar_base_datos()

if not base_de_datos:
    st.stop()

# Etiqueta de base de datos activa
st.markdown(f"<div style='text-align: center; color: #829AB1; margin-bottom: 20px;'>🛡️ <b>Base de datos activa:</b> {len(base_de_datos)} calqueos indexados.</div>", unsafe_allow_html=True)

frase_busqueda = st.text_input("", placeholder="🔍 Ingresa la palabra o frase a buscar (Ejemplo: Bendecidos entienden)")

if frase_busqueda:
    frase_limpia = frase_busqueda.strip().lower()
    resultados_encontrados = []
    
    with st.spinner('Buscando coincidencias...'):
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
        st.markdown(f"<h3 style='text-align: left; margin-top: 20px;'>🔍 Se encontraron {len(resultados_encontrados)} menciones:</h3>", unsafe_allow_html=True)
        
        for res in resultados_encontrados:
            # Ahora usamos tarjetas personalizadas que no interfieren con la estructura de Streamlit
            st.markdown(f"""
            <div class="resultado-card">
                <div style="color: #D4AF37; font-size: 1.1rem; font-weight: bold; margin-bottom: 5px;">🎥 {res['titulo']}</div>
                <div style="color: #A0AEC0; font-size: 0.9rem; margin-bottom: 8px;">⏱️ Minuto {res['tiempo']}</div>
                <div style="color: #F0F2F6; font-size: 1.05rem; font-style: italic; margin-bottom: 10px;">"...{res['texto']}..."</div>
                <a href="{res['enlace']}" target="_blank">▶️ Ver en YouTube en este minuto exacto</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No se encontraron coincidencias para esa frase. Intenta buscar una palabra más corta o sin tildes.")
