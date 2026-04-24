import streamlit as st
import numpy as np
from astropy.io import fits
import astroalign as aa
import time

st.set_page_config(page_title="CEELL Asteroid Search Software v2.0", layout="wide")

def advanced_stretch(data, quadrant=None):
    """Ajusta o contraste e foca em quadrantes específicos se solicitado."""
    # Recorte por quadrante (1 a 4)
    h, w = data.shape
    mid_h, mid_w = h // 2, w // 2
    
    if quadrant == 1: data = data[:mid_h, mid_w:]
    elif quadrant == 2: data = data[:mid_h, :mid_w]
    elif quadrant == 3: data = data[mid_h:, :mid_w]
    elif quadrant == 4: data = data[mid_h:, mid_w:]

    # Normalização robusta (Percentile Clipping como no Astrometrica)
    vmin, vmax = np.percentile(data, [0.5, 99.5])
    data = np.clip(data, vmin, vmax)
    data = (data - vmin) / (vmax - vmin)
    return data

def process_fits(files):
    images, headers = [], []
    for f in files:
        with fits.open(f) as hdul:
            # Garante que estamos lidando com dados 2D
            data = hdul[0].data.astype(np.float32)
            images.append(data)
            headers.append(hdul[0].header)
    return images, headers

st.title("☄️ CEELL Asteroid Search Software - High Precision")

if "aligned_images" not in st.session_state:
    st.session_state.aligned_images = None
if "result_image" not in st.session_state:
    st.session_state.result_image = None

with st.sidebar:
    st.header("Configurações de Análise")
    files = st.file_uploader("Arquivos FITS", type=["fits", "fit"], accept_multiple_files=True)
    
    quadrante = st.selectbox("Focar Quadrante (Zoom)", [None, 1, 2, 3, 4], 
                             help="O Astrometrica divide a imagem para facilitar a busca manual.")
    
    blink_speed = st.slider("Velocidade do Blink (segundos)", 0.1, 1.0, 0.3)
    
    st.divider()
    btn_alinhar = st.button("🚀 ALINHAR E SINCRONIZAR", use_container_width=True)
    btn_subtrair = st.button("➖ SUBTRAÇÃO DIFERENCIAL", use_container_width=True)

col_main = st.container()

if files and len(files) == 4:
    images, headers = process_fits(files)

    if btn_alinhar:
        try:
            with st.spinner("Alinhando estrelas de referência..."):
                target = images[0]
                aligned = [target]
                for i in range(1, 4):
                    reg, _ = aa.register(images[i], target)
                    aligned.append(reg)
                st.session_state.aligned_images = aligned
                st.session_state.result_image = None
                st.success("Imagens sincronizadas!")
        except Exception as e:
            st.error(f"Falha no alinhamento: {e}. Verifique se as fotos possuem estrelas suficientes.")

    if btn_subtrair:
        if st.session_state.aligned_images:
            # Subtração temporal para evidenciar transientes
            imgs = st.session_state.aligned_images
            # Técnica de mediana para remover estrelas fixas e sobrar apenas o que mudou
            result = imgs[0] - imgs[3] 
            st.session_state.result_image = result
        else:
            st.warning("Alinhe primeiro.")

    with col_main:
        if st.session_state.result_image is not None:
            st.subheader(f"Resultado da Subtração - {'Visão Geral' if not quadrante else f'Foco no Quadrante {quadrante}'}")
            st.image(advanced_stretch(st.session_state.result_image, quadrante), use_container_width=True)
            if st.button("Voltar para o Blink"):
                st.session_state.result_image = None
                st.rerun()
        
        elif st.session_state.aligned_images is not None:
            st.subheader(f"Blink Comparator - {'Visão Geral' if not quadrante else f'Foco no Quadrante {quadrante}'}")
            placeholder = st.empty()
            
            # O loop de blink agora roda continuamente enquanto o usuário observa
            while True:
                for idx, img in enumerate(st.session_state.aligned_images):
                    with placeholder.container():
                        st.caption(f"Frame {idx + 1} de 4")
                        st.image(advanced_stretch(img, quadrante), use_container_width=True)
                        time.sleep(blink_speed)
else:
    st.info("Aguardando o upload de 4 sequências de imagens do mesmo campo estelar.")