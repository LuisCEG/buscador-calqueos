import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse as urlparse

# Configuración de la página
st.set_page_config(page_title="Buscador de Calqueos", page_icon="📖", layout="centered")

st.title("📖 Buscador Interactivo de Calqueos")
st.markdown("Encuentra frases exactas en tus predicaciones y salta al minuto correcto con un clic.")

# Función para limpiar y extraer el ID del video
def extraer_video_id(url):
    if "youtube.com" in url or "youtu.be" in url:
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        else:
            parsed = urlparse.urlparse(url)
            return urlparse.parse_qs(parsed.query).get("v", [url])[0]
    return url # Asume que ya es un ID si no hay URL

# Entrada de datos
video_input = st.text_input("🔗 Pega el enlace de YouTube o el ID del video:", placeholder="Ej: https://youtu.be/Jz6oTk7XEn0")

if video_input:
    video_id = extraer_video_id(video_input)
    
    try:
        # Extraer la transcripción
        with st.spinner("Extrayendo texto del video..."):
            transcripcion = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
            
        st.success("✅ Texto extraído correctamente.")
        
        # Buscador de palabras
        busqueda = st.text_input("🔍 Escribe la palabra o frase que deseas buscar en este video:")
        
        st.markdown("---")
        st.markdown("### 📝 Transcripción Interactiva")
        
        resultados_encontrados = 0
        
        # Iterar sobre cada línea de la transcripción
        for fragmento in transcripcion:
            texto = fragmento['text']
            
            # Filtro de búsqueda (si está vacío, muestra todo)
            if busqueda.lower() in texto.lower():
                resultados_encontrados += 1
                
                # Formatear el tiempo a [MM:SS]
                inicio_segundos = int(fragmento['start'])
                minutos = inicio_segundos // 60
                segundos = inicio_segundos % 60
                tiempo_formateado = f"[{minutos:02d}:{segundos:02d}]"
                
                # Construir enlace directo al segundo exacto
                enlace_youtube = f"https://youtu.be/{video_id}?t={inicio_segundos}"
                
                # Mostrar en pantalla
                st.markdown(f"**{tiempo_formateado}** - [{texto}]({enlace_youtube})")
                
        if resultados_encontrados == 0:
            st.warning("No se encontraron resultados para esa búsqueda. Intenta con otra palabra.")

    except Exception as e:
        st.error(f"❌ Error al cargar el video. Verifica el enlace o asegúrate de que tenga transcripción habilitada. Detalle: {e}")
