import streamlit as st
import json
import zipfile
import re
import html
import unicodedata
from bisect import bisect_right

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
def normalizar(txt):
    """Minúsculas, sin tildes ni signos: 'Bendecídos,' -> 'bendecidos'."""
    txt = unicodedata.normalize("NFD", txt.lower())
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]+", "", txt)


@st.cache_data(show_spinner=False)
def cargar_base_datos():
    try:
        with zipfile.ZipFile("bd_calqueos.zip", "r") as z:
            with z.open("bd_calqueos.json") as f:
                crudo = json.load(f)
    except Exception as e:
        st.error(f"Error al cargar la base de datos: {e}")
        return []

    videos = []
    for v in crudo:
        palabras = v["texto"].split()
        tiempos, t = [], 0.0
        for dt in v["dt"]:
            t += dt
            tiempos.append(t)
        # texto normalizado palabra por palabra (alineado con 'palabras')
        norm = [normalizar(p) for p in palabras]
        offsets, pos = [], 0
        for n in norm:
            offsets.append(pos)
            pos += len(n) + 1
        videos.append({
            "id": v["video_id"],
            "titulo": v["titulo"].strip(),
            "palabras": palabras,
            "tiempos": tiempos,
            "norm": norm,
            "ntexto": " ".join(norm),
            "offsets": offsets,
        })
    return videos


def buscar(videos, frase, modo, ventana=15, separacion=12):
    """Devuelve lista de coincidencias [(video, idx_palabra_inicial, idx_palabra_final)]."""
    q = [normalizar(p) for p in frase.split()]
    q = [p for p in q if p]
    if not q:
        return []
    resultados = []
    for v in videos:
        nt, offs = v["ntexto"], v["offsets"]
        hallazgos = []
        if modo == "frase":
            patron = re.compile(r"(?<![a-z0-9ñ])" + " ".join(map(re.escape, q)) + r"(?![a-z0-9ñ])")
            for m in patron.finditer(nt):
                i = bisect_right(offs, m.start()) - 1
                hallazgos.append((i, i + len(q) - 1))
        else:  # todas las palabras, en cualquier orden, dentro de una ventana
            patron = re.compile(r"(?<![a-z0-9ñ])" + re.escape(q[0]) + r"(?![a-z0-9ñ])")
            for m in patron.finditer(nt):
                i = bisect_right(offs, m.start()) - 1
                a, b = max(0, i - ventana), min(len(v["norm"]), i + ventana + 1)
                trozo = set(v["norm"][a:b])
                if all(p in trozo for p in q[1:]):
                    hallazgos.append((i, i))
        # unir coincidencias muy cercanas para no repetir la misma escena
        ultimo = -10**9
        for ini, fin in hallazgos:
            if ini - ultimo >= separacion:
                resultados.append((v, ini, fin))
                ultimo = ini
    return resultados


def fmt_tiempo(seg):
    seg = int(seg)
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fragmento(v, ini, fin, contexto=18):
    a, b = max(0, ini - contexto), min(len(v["palabras"]), fin + contexto + 1)
    antes = html.escape(" ".join(v["palabras"][a:ini]))
    medio = html.escape(" ".join(v["palabras"][ini:fin + 1]))
    despues = html.escape(" ".join(v["palabras"][fin + 1:b]))
    return f"{antes} <mark style='background:#D4AF37;color:#051024;padding:0 3px;border-radius:3px'>{medio}</mark> {despues}"


with st.spinner("Cargando los archivos del Reino..."):
    base_de_datos = cargar_base_datos()

if not base_de_datos:
    st.stop()

total_palabras = sum(len(v["palabras"]) for v in base_de_datos)
st.markdown(
    f"<div style='text-align: center; color: #829AB1; margin-bottom: 20px;'>🛡️ <b>Base de datos activa:</b> "
    f"{len(base_de_datos)} calqueos indexados · {total_palabras:,} palabras.</div>".replace(",", "."),
    unsafe_allow_html=True,
)

frase_busqueda = st.text_input(
    "Búsqueda", label_visibility="collapsed",
    placeholder="🔍 Ingresa la palabra o frase a buscar (Ejemplo: Bendecidos entienden)",
)

c1, c2, c3 = st.columns([1.3, 1.3, 1])
with c1:
    modo_txt = st.radio(
        "Modo", ["Frase exacta", "Todas las palabras cerca"],
        horizontal=True, label_visibility="collapsed",
        help="«Todas las palabras cerca» encuentra las palabras en cualquier orden dentro de ~15 palabras.",
    )
with c2:
    orden = st.radio("Orden", ["Por calqueo", "Más menciones primero"], horizontal=True, label_visibility="collapsed")
with c3:
    st.caption("Ignora tildes y mayúsculas.")
modo = "frase" if modo_txt == "Frase exacta" else "cerca"

if frase_busqueda and frase_busqueda.strip():
    with st.spinner("Buscando coincidencias..."):
        hallazgos = buscar(base_de_datos, frase_busqueda, modo)

    if not hallazgos:
        st.warning("No se encontraron coincidencias. Prueba con una palabra más corta o el modo «Todas las palabras cerca».")
        st.stop()

    por_video = {}
    for v, ini, fin in hallazgos:
        por_video.setdefault(v["id"], {"video": v, "items": []})["items"].append((ini, fin))
    grupos = list(por_video.values())
    if orden == "Más menciones primero":
        grupos.sort(key=lambda g: -len(g["items"]))

    st.markdown(
        f"<h3 style='text-align: left; margin-top: 20px;'>🔍 {len(hallazgos)} menciones en {len(grupos)} calqueos</h3>",
        unsafe_allow_html=True,
    )

    LIMITE = 150
    mostrados = 0
    for g in grupos:
        v = g["video"]
        st.markdown(
            f"<div style='color:#D4AF37;font-weight:bold;font-size:1.15rem;margin:22px 0 8px'>🎥 {html.escape(v['titulo'])} "
            f"<span style='color:#829AB1;font-size:.9rem'>— {len(g['items'])} mención(es)</span></div>",
            unsafe_allow_html=True,
        )
        for ini, fin in g["items"]:
            if mostrados >= LIMITE:
                break
            seg = int(v["tiempos"][ini])
            enlace = f"https://youtu.be/{v['id']}?t={max(0, seg - 3)}"
            st.markdown(
                f"""<div class="resultado-card">
                <div style="color:#A0AEC0;font-size:.9rem;margin-bottom:8px">⏱️ Minuto {fmt_tiempo(seg)}</div>
                <div style="color:#F0F2F6;font-size:1.05rem;margin-bottom:10px">…{fragmento(v, ini, fin)}…</div>
                <a href="{enlace}" target="_blank">▶️ Ver en YouTube en este minuto</a>
                </div>""",
                unsafe_allow_html=True,
            )
            mostrados += 1
        if mostrados >= LIMITE:
            break
    if len(hallazgos) > LIMITE:
        st.info(f"Se muestran las primeras {LIMITE} de {len(hallazgos)} menciones. Afina la búsqueda con una frase más específica.")
