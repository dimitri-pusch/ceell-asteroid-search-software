# ☄️ CEELL Asteroid Search Software

Este software foi desenvolvido para auxiliar membros da **CEELL** (e entusiastas de astronomia) na detecção de asteroides e objetos transientes a partir de sequências de imagens astronômicas no formato FITS.

O diferencial desta ferramenta é a automação do processo de alinhamento e a limpeza visual para destacar pontos que se movem contra o fundo estelar fixo.

## 🚀 Funcionalidades

- **Alinhamento Automático:** Utiliza o algoritmo `Astroalign` para sincronizar perfeitamente 4 frames, corrigindo pequenas variações de posição ou rotação da câmera.
- **Detecção Automática (Full Auto):** Localiza o ponto de maior brilho em cada frame e o rastreia visualmente.
- **Blink Comparator:** Anima a sequência de fotos para que o olho humano detecte facilmente o movimento de asteroides.
- **Subtração Diferencial:** Gera uma imagem de diferença para evidenciar o deslocamento temporal do objeto.
- **Fundo Preto (Noise Reduction):** Aplica filtros estatísticos (Thresholding) para remover o ruído do céu e focar apenas nos candidatos reais.

## 🛠️ Tecnologias Utilizadas

* [Python](https://www.python.org/)
* **Astropy:** Manipulação de arquivos FITS e metadados astronômicos.
* **Astroalign:** Alinhamento de imagens baseado em padrões estelares.
* **OpenCV (Headless):** Processamento de visão computacional e detecção de pontos de brilho.
* **Streamlit:** Interface web para processamento em tempo real.

## 📦 Como Instalar e Rodar
1. Clone o repositório:
   ```bash
   git clone [https://github.com/seu-usuario/ceell-asteroid-search-software.git](https://github.com/seu-usuario/ceell-asteroid-search-software.git)
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute o software:
   ```bash
   streamlit run main.py
   ```

## ☄️ Metodologia de Busca
Para uma detecção eficiente, recomenda-se o upload de 4 imagens do mesmo campo estelar tiradas em intervalos de tempo regulares.
1. Após o Alinhamento, observe o círculo verde: se ele "saltar" em linha reta enquanto as estrelas ao redor permanecem estáticas, você encontrou um candidato a asteroide.
2. Utilize a Subtração para confirmar que o ponto não é um artefato fixo (ruído do sensor).

---
**Desenvolvido para fins científicos e educacionais pela equipe CEELL.**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/784d16dc-480d-4d76-abf6-d7f714ad9061" />
