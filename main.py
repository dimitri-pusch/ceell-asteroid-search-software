import streamlit as st
import numpy as np
from astropy.io import fits
import astroalign as aa
import time
import cv2

st.set_page_config(page_title="CEELL Asteroid Search Software v3.1", layout="wide")

def apply_mask_and_circles(img, coord_list, frame_idx):
    """Limpa o ruído de fundo e desenha o círculo no candidato."""
    # 1. Normalização e Limpeza de ruído (Threshold)
    # Mantemos apenas o que está acima da média + 3 desvios padrões (ajustável)
    std_val = np.std(img)
    mean_val = np.mean(img)
    thresh = mean_val + (std_val * 3)
    
    clean_img = np.where(img > thresh, img, 0)
    
    # Normalizar para visualização (0-255)
    img_rescaled = cv2.normalize(clean_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    img_rgb = cv2.cvtColor(img_rescaled, cv2.COLOR_GRAY2RGB)
    
    # 2. Desenhar Círculo Verde no candidato (se houver coordenadas)
    if coord_list and frame_idx < len(coord_list):
        point = coord_list[frame_idx]
        cv2.circle(img_rgb, point, 20, (0, 255, 0), 2)
        
    return img_rgb

st.title("☄️ CEELL Asteroid Search Software")

with st.sidebar:
    st.header("Configurações")
    files = st.file_uploader("Arquivos FITS", type=["fits", "fit"], accept_multiple_files=True)
    
    st.subheader("Rastreio do Candidato")
    st.info("Insira as coordenadas X,Y do ponto no Quadrante 3 para cada frame.")
    # Exemplo de entrada: 150,400; 155,405...
    coords_input = st.text_input("Coordenadas (x1,y1; x2,y2...)", "100,100; 110,110; 120,120; 130,130")
    
    st.divider()
    btn_processar = st.button("🚀 INICIAR BUSCA", use_container_width=True)

if files and len(files) == 4:
    # Converter input de coordenadas em lista de tuplas
    try:
        coord_list = [tuple(map(int, p.split(','))) for p in coords_input.split(';')]
    except:
        coord_list = []

    if btn_processar:
        with st.spinner("Processando e alinhando..."):
            # Lógica de carregamento e alinhamento
            images = []
            for f in files:
                with fits.open(f) as h:
                    images.append(h[0].data.astype(np.float32))
            
            # Alinhamento
            target = images[0]
            aligned = [target]
            for i in range(1, 4):
                reg, _ = aa.register(images[i], target)
                aligned.append(reg)
            
            st.session_state.processed_frames = aligned
            st.session_state.sub_result = aligned[0] - aligned[3]

    if "processed_frames" in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Blink & Tracking")
            placeholder_blink = st.empty()
            
        with col2:
            st.subheader("Subtração Animada")
            placeholder_sub = st.empty()

        # Loop de animação único para ambos
        while True:
            for i in range(4):
                # Frame Original com Máscara e Círculo
                frame_visual = apply_mask_and_circles(st.session_state.processed_frames[i], coord_list, i)
                placeholder_blink.image(frame_visual, caption=f"Frame {i+1}", use_container_width=True)
                
                # Frame de Subtração (Blink entre Original e Subtraído)
                sub_visual = apply_mask_and_circles(st.session_state.sub_result, coord_list, i)
                placeholder_sub.image(sub_visual, caption="Diferença Temporal", use_container_width=True)
                
                time.sleep(0.4)
