import streamlit as st
import base64
import os
import io
from pypdf import PdfWriter

# Configuración inicial de la página
st.set_page_config(page_title="Repertorio Iglesia", layout="centered")

# 1. Base de datos
canciones = {
    "El me sostendrá": {"etiquetas": ["#adoracion", "#himno"], "archivo_base": "el_me_sostendra"},
    "Suenan dulces himnos": {"etiquetas": ["#redencion", "#cruz"], "archivo_base": "suenan_dulces_himnos"}
}

# Función para renderizar el PDF
def mostrar_pdf(ruta_archivo):
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="650" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.warning(f"Falta subir el archivo PDF en: {ruta_archivo}")

st.title("📖 Repertorio Alabanzas IBBG")

# --- NUEVA SECCIÓN: CREADOR DE SETLISTS ---
st.header("🎵 Crear Lista de Reproducción (Setlist)")
st.write("Selecciona las canciones para el servicio y descarga un solo PDF con todas.")

# Seleccionar canciones para la lista
playlist_seleccionada = st.multiselect("Agregar canciones a la lista:", options=list(canciones.keys()))

if playlist_seleccionada:
    # Elegir si el PDF unificado será para músicos o cantantes
    formato_playlist = st.radio("Formato del Setlist:", ["Modo Cantante (Solo Letra)", "Modo Músico (Con Acordes)"], horizontal=True)
    
    # Lógica para unir los PDFs
    merger = PdfWriter()
    archivos_faltantes = []
    
    for cancion in playlist_seleccionada:
        base_name = canciones[cancion]["archivo_base"]
        sufijo = "_acordes.pdf" if "Músico" in formato_playlist else "_letra.pdf"
        ruta = f"pdfs/{base_name}{sufijo}"
        
        if os.path.exists(ruta):
            merger.append(ruta)
        else:
            archivos_faltantes.append(ruta)
            
    if archivos_faltantes:
        st.error(f"No se puede generar el PDF. Faltan estos archivos: {', '.join(archivos_faltantes)}")
    else:
        # Guardar el PDF unificado en la memoria temporal para descargarlo
        pdf_final = io.BytesIO()
        merger.write(pdf_final)
        
        st.download_button(
            label="⬇️ Descargar Setlist en PDF",
            data=pdf_final.getvalue(),
            file_name="Setlist_Iglesia.pdf",
            mime="application/pdf"
        )
st.divider()

# --- SECCIÓN ORIGINAL: REPOSITORIO Y FILTROS ---
st.header("📚 Repositorio Completo")

todas_las_etiquetas = list(set(tag for info in canciones.values() for tag in info["etiquetas"]))

st.sidebar.header("Filtros")
st.sidebar.write("Deja el filtro vacío para ver todas las canciones.")
# El filtro ahora empieza vacío (limpio visualmente)
etiquetas_seleccionadas = st.sidebar.multiselect(
    "Selecciona los temas:", 
    options=todas_las_etiquetas,
    default=[] 
)

# Lógica de filtrado dinámico: Si está vacío, muestra todas. Si no, filtra.
if not etiquetas_seleccionadas:
    canciones_filtradas = list(canciones.keys())
else:
    canciones_filtradas = [
        titulo for titulo, info in canciones.items() 
        if any(tag in etiquetas_seleccionadas for tag in info["etiquetas"])
    ]

# Mostrar la lista de canciones con sus desplegables
if canciones_filtradas:
    st.write(f"### Mostrando {len(canciones_filtradas)} canciones:")
    
    for cancion in canciones_filtradas:
        with st.expander(cancion):
            mostrar_acordes = st.toggle("🎸 Modo Músico (Mostrar Acordes)", key=f"toggle_{cancion}")
            
            base_name = canciones[cancion]["archivo_base"]
            sufijo = "_acordes.pdf" if mostrar_acordes else "_letra.pdf"
            ruta_pdf = f"pdfs/{base_name}{sufijo}"
            
            mostrar_pdf(ruta_pdf)
else:
    st.info("No hay canciones que coincidan con los filtros seleccionados.")