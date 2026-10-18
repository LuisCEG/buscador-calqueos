import streamlit as st
import json
import zipfile

# Configuración de la página
st.set_page_config(page_title="Buscador de Calqueos", page_icon="📖", layout="wide")

st.title("📖 Buscador Global de Calqueos")
st.markdown("Encuentra frases exactas en los 740 videos de **CRECIENDO EN GRACIA** al instante.")

# Función para cargar la base de datos desde el ZIP de forma optimizada
@st.cache_data(show_spinner=False)
def cargar_base_datos():
    try:
        # Aquí es donde abrimos tu archivo comprimido
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
st.success(f"✅ Base de datos lista: {len(base_de_datos)} videos cargados.")
frase_busqueda = st.text_input("Ingresa la palabra o frase a buscar:", placeholder="Ejemplo: Bendecidos entien y no entienden")

if frase_busqueda:
    frase_limpia = frase_busqueda.strip().lower()
    resultados_encontrados = []
    
    with st.spinner('Buscando en todos los videos...'):
        # Recorremos los videos en memoria
        for video in base_de_datos:
            for bloque in video.get("transcripcion", []):
                texto_original = bloque.get("text", "")
                
                # Búsqueda ignorando mayúsculas y minúsculas
                if frase_limpia in texto_original.lower():
                    # Formatear el tiempo a minutos y segundos
                    segundos_totales = int(bloque.get("start", 0))
                    minutos = segundos_totales // 60
                    segundos = segundos_totales % 60
                    tiempo_formateado = f"{minutos}:{segundos:02d}"
                    
                    # Crear el enlace de YouTube al minuto exacto
                    enlace_youtube = f"https://youtu.be/{video['video_id']}?t={segundos_totales}"
                    
                    resultados_encontrados.append({
                        "titulo": video["titulo"],
                        "texto": texto_original,
                        "tiempo": tiempo_formateado,
                        "enlace": enlace_youtube
                    })

    # Mostrar Resultados
    if resultados_encontrados:
        st.subheader(f"🔍 Se encontraron {len(resultados_encontrados)} menciones:")
        
        for res in resultados_encontrados:
            with st.container():
                st.markdown(f"**🎥 {res['titulo']}**")
                st.markdown(f"⏱️ **Minuto {res['tiempo']}** — *\"...{res['texto']}...\"*")
                st.markdown(f"[▶️ Clic aquí para ver el video en este minuto exacto]({res['enlace']})")
                st.divider()
    else:
        st.warning("No se encontraron coincidencias para esa frase. Intenta buscar una palabra más corta.")
