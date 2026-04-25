import streamlit as st
import numpy as np
from astropy.io import fits  # Biblioteca padrão para arquivos astronômicos
import astroalign as aa      # Alinha imagens baseando-se em triângulos de estrelas
import time
import cv2                  # Processamento de visão computacional

st.set_page_config(page_title="CEELL Asteroid Search Software - v3.2", layout="wide")

def clean_and_format(img):
    """
    Limpa o ruído de fundo usando estatística e converte para 8-bit (RGB).
    O objetivo é deixar o fundo preto e as estrelas/asteroides nítidos.
    """
    # Calcula a média e o desvio padrão dos pixels
    mean, std = np.mean(img), np.std(img)
    # Define um limite (Threshold): Tudo abaixo de 3.5 sigmas da média vira 0 (preto)
    limit = mean + (std * 3.5)
    img_cleaned = np.where(img > limit, img, 0)
    
    # Normaliza a imagem para a escala de 0 a 255 (exigida para exibição de imagem)
    img_rescaled = cv2.normalize(img_cleaned, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    # Converte de tons de cinza para RGB para podermos desenhar o círculo colorido
    return cv2.cvtColor(img_rescaled, cv2.COLOR_GRAY2RGB)

def get_brightest_point(img):
    """
    Encontra automaticamente a coordenada (X, Y) do ponto mais brilhante na imagem.
    Ideal para seguir o candidato a asteroide em campos limpos.
    """
    # minMaxLoc retorna o valor mín e máx e suas respectivas posições (x, y)
    _, _, _, max_loc = cv2.minMaxLoc(img)
    return max_loc

st.title("☄️ CEELL Asteroid Search Software - v3.2")
st.subheader("Modo de Detecção Automática de Transientes")

# Inicialização de variáveis de estado (para o Streamlit não perder os dados ao atualizar a tela)
if "aligned_images" not in st.session_state:
    st.session_state.aligned_images = None
if "sub_image" not in st.session_state:
    st.session_state.sub_image = None

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    uploaded_files = st.file_uploader("Upload de 4 fotos FITS", type=["fits", "fit"], accept_multiple_files=True)
    blink_speed = st.slider("Velocidade do Blink (s)", 0.1, 1.0, 0.4)
    
    btn_process = st.button("🚀 ALINHAR E DETECTAR", use_container_width=True)
    btn_sub = st.button("➖ SUBTRAÇÃO FINAL", use_container_width=True)

# Lógica principal ao clicar em Processar
if uploaded_files and len(uploaded_files) == 4:
    if btn_process:
        with st.spinner("Lendo arquivos e alinhando estrelas..."):
            raw_images = []
            for f in uploaded_files:
                with fits.open(f) as hdul:
                    # hdul[0].data extrai a matriz numérica de brilho da imagem
                    raw_images.append(hdul[0].data.astype(np.float32))
            
            # Alinhamento automático via Astroalign
            # Ele detecta padrões de estrelas e rotaciona/move as fotos para ficarem idênticas
            target = raw_images[0]
            aligned = [target]
            for i in range(1, 4):
                # 'register' transforma a imagem i para o referencial da imagem target
                registered, _ = aa.register(raw_images[i], target)
                aligned.append(registered)
            
            st.session_state.aligned_images = aligned
            st.session_state.sub_image = None # Reseta a subtração ao carregar novas

    # Lógica de Subtração
    if btn_sub and st.session_state.aligned_images:
        imgs = st.session_state.aligned_images
        # Subtraímos o primeiro frame do último para ver o deslocamento total
        st.session_state.sub_image = imgs[0] - imgs[3]

    # --- ÁREA DE VISUALIZAÇÃO ---
    col1, col2 = st.columns(2)

    # Lado Esquerdo: Blink das Imagens Originais
    if st.session_state.aligned_images:
        with col1:
            st.write("**Sequência Sincronizada (Blink)**")
            placeholder_blink = st.empty()
        
        # Lado Direito: Subtração ou Status
        with col2:
            if st.session_state.sub_image is not None:
                st.write("**Resultado da Subtração**")
                placeholder_sub = st.empty()
            else:
                st.info("Clique em 'Subtração Final' para processar a diferença.")

        # Loop infinito de animação (enquanto o app estiver aberto)
        while True:
            for idx, img in enumerate(st.session_state.aligned_images):
                # Processa visualmente o frame atual
                frame_rgb = clean_and_format(img)
                
                # Detecta o ponto mais brilhante neste frame específico
                point = get_brightest_point(img)
                # Desenha o círculo verde (coord, raio, cor, espessura)
                cv2.circle(frame_rgb, point, 20, (0, 255, 0), 2)
                
                placeholder_blink.image(frame_rgb, caption=f"Frame {idx+1} - Candidato em {point}", use_container_width=True)
                
                # Se a subtração existir, anima ela também
                if st.session_state.sub_image is not None:
                    sub_rgb = clean_and_format(st.session_state.sub_image)
                    placeholder_sub.image(sub_rgb, caption="Mapa de Deslocamento", use_container_width=True)
                
                time.sleep(blink_speed)

else:
    st.warning("Por favor, faça o upload de exatamente 4 arquivos FITS.")
