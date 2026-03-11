import streamlit as st
import base64
import os
import io
import fitz  # Esta es la librería PyMuPDF que convierte PDF a imagen
from pypdf import PdfWriter

# Configuración inicial de la página
st.set_page_config(page_title="Repertorio Iglesia", layout="centered")

# 1. Base de datos
canciones = {
    "El me sostendrá": {"etiquetas": ["#adoracion", "#himno"], "archivo_base": "el_me_sostendra"},
    "Suenan dulces himnos": {"etiquetas": ["#redencion", "#cruz"], "archivo_base": "suenan_dulces_himnos"},
    "Recibimos": {"etiquetas": ["#cena", "#redencion"], "archivo_base": "recibimos"}
    "Somos siempre tuyos": {"etiquetas": ["#redencion", "#cruz"], "archivo_base": "somos_siempre_tuyos"}
}

# --- FUNCION PDF --> IMAGEN ---
def mostrar_pdf(ruta_archivo):
    if os.path.exists(ruta_archivo):
        # Abrimos el PDF
        doc = fitz.open(ruta_archivo)
        # Convertimos cada página en una imagen de alta calidad
        for page in doc:
            pix = page.get_pixmap(dpi=150) 
            # Mostramos la imagen en pantalla, ajustada al ancho del celular/computador
            st.image(pix.tobytes(), use_container_width=True)
    else:
        st.warning(f"Falta subir el archivo PDF en: {ruta_archivo}")

st.title("📖 Repertorio de la Iglesia")

# --- SECCIÓN: CREADOR DE SETLISTS ---
st.header("🎵 Crear Lista de Reproducción (Setlist)")
st.write("Selecciona las canciones para el servicio y descarga un solo PDF con todas.")

playlist_seleccionada = st.multiselect("Agregar canciones a la lista:", options=list(canciones.keys()))

if playlist_seleccionada:
    formato_playlist = st.radio("Formato del Setlist:", ["Modo Cantante (Solo Letra)", "Modo Músico (Con Acordes)"], horizontal=True)
    
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
        pdf_final = io.BytesIO()
        merger.write(pdf_final)
        
        st.download_button(
            label="⬇️ Descargar Setlist en PDF",
            data=pdf_final.getvalue(),
            file_name="Setlist_Iglesia.pdf",
            mime="application/pdf"
        )
st.divider()

# --- SECCIÓN: REPOSITORIO Y FILTROS ---
st.header("📚 Repositorio Completo")

todas_las_etiquetas = list(set(tag for info in canciones.values() for tag in info["etiquetas"]))

st.sidebar.header("Filtros")
st.sidebar.write("Deja el filtro vacío para ver todas las canciones.")

etiquetas_seleccionadas = st.sidebar.multiselect(
    "Selecciona los temas:", 
    options=todas_las_etiquetas,
    default=[] 
)

if not etiquetas_seleccionadas:
    canciones_filtradas = list(canciones.keys())
else:
    canciones_filtradas = [
        titulo for titulo, info in canciones.items() 
        if any(tag in etiquetas_seleccionadas for tag in info["etiquetas"])
    ]

if canciones_filtradas:
    st.write(f"### Mostrando {len(canciones_filtradas)} canciones:")
    
    for cancion in canciones_filtradas:
        with st.expander(cancion):
            mostrar_acordes = st.toggle("🎸 Modo Músico (Mostrar Acordes)", key=f"toggle_{cancion}")
            
            base_name = canciones[cancion]["archivo_base"]
            sufijo = "_acordes.pdf" if mostrar_acordes else "_letra.pdf"
            ruta_pdf = f"pdfs/{base_name}{sufijo}"
            
            # Aquí se llama a la nueva función que renderiza imágenes
            mostrar_pdf(ruta_pdf)
else:
    st.info("No hay canciones que coincidan con los filtros seleccionados.")
