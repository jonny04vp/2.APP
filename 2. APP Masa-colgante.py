import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile
import os
from matplotlib.animation import PillowWriter
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Modelo Dinámico de Discos", layout="wide")
st.title("Modelo de Dinámica: Sistema de Discos y Bloque")

st.markdown("""
Esta simulación representa dos cilindros una mas grande que el otro en una de ellos esta enrollado un cable que sostiene un bloque de una deteminada masa
""")

# Título
st.title("Ejemplo grafico de lo queremos calcular")

st.title("Visualización de un Cilindro")

st.image("https://i.postimg.cc/prK1pBzP/DOS.png", 
         caption="Ilustración", 
         use_container_width=True)

st.markdown("""
Mediante esta aplicación el usuario podra calcular el tiempo que se demora en caer la caja de una determina altura ademas de las velocidades de los discos y del bloque
""")
st.markdown("""
Ademas mediante los gráficos interactivos podrá observar como disminuye la energía potencial pero aumenta la energia cinética
""")


# Entradas del usuario
st.sidebar.header("Parámetros del sistema")
R = st.sidebar.number_input("Radio externo R (m)", 0.02, 0.2, 0.1, 0.005)
r = st.sidebar.number_input("Radio interno r (m)", 0.01, R - 0.01, 0.03, 0.001)
M1 = st.sidebar.number_input("Masa del disco interno M1 (kg)", 0.1, 5.0, 1.0, 0.1)
M2 = st.sidebar.number_input("Masa del disco externo M2 (kg)", 0.1, 5.0, 1.0, 0.1)
m = st.sidebar.number_input("Masa del bloque (kg)", 0.1, 5.0, 1.5, 0.1)
h = st.sidebar.number_input("Altura de caída (m)", 0.1, 5.0, 2.0, 0.1)
n_frames = st.sidebar.slider("Cuadros en la animación", 10, 200, 80)
generar_anim = st.sidebar.checkbox("Mostrar animaciones", True)

# Constantes y cálculos
I1 = 0.5 * M1 * r**2
I2 = 0.5 * M2 * R**2
I_total = I1 + I2

a = 9.81 / (1 + I_total / (m * r**2))
t_total = np.sqrt(2 * h / a)
t_vals = np.linspace(0, t_total, n_frames)

# Cinemática y energías
y_vals = h - 0.5 * a * t_vals**2
v_vals = a * t_vals
w_vals = v_vals / r
Ep_vals = m * 9.81 * y_vals
Ec_tras_vals = 0.5 * m * v_vals**2
Ec_rot_vals = 0.5 * I_total * w_vals**2
Ec_total_vals = Ec_tras_vals + Ec_rot_vals

# Mostrar resultados globales
st.subheader("Resultados Finales")
st.markdown(f"**Tiempo total:** {t_total:.2f} s")
st.markdown(f"**Velocidad final del bloque:** {v_vals[-1]:.2f} m/s")
st.markdown(f"**Velocidad angular final:** {w_vals[-1]:.2f} rad/s")
st.markdown(f"**Energía potencial final:** {Ep_vals[-1]:.2f} J")
st.markdown(f"**Energía cinética total final:** {Ec_total_vals[-1]:.2f} J")

# Tabla de variables vs tiempo
st.subheader("Evolución Temporal (muestras)")
df = pd.DataFrame({
    "Tiempo (s)": t_vals,
    "Altura (m)": y_vals,
    "Velocidad (m/s)": v_vals,
    "Velocidad Angular (rad/s)": w_vals,
    "E_Potencial (J)": Ep_vals,
    "E_Cinética (J)": Ec_total_vals
})
st.dataframe(df.round(2), height=300)

def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Informe del Modelo Dinámico de Discos y Bloque", 0, 1, 'C')

    pdf.set_font("Arial", size=12)
    pdf.ln(5)
    pdf.cell(0, 10, "Parámetros del sistema:", 0, 1)
    pdf.cell(0, 8, f"Radio externo R: {R:.3f} m", 0, 1)
    pdf.cell(0, 8, f"Radio interno r: {r:.3f} m", 0, 1)
    pdf.cell(0, 8, f"Masa del disco interno M1: {M1:.2f} kg", 0, 1)
    pdf.cell(0, 8, f"Masa del disco externo M2: {M2:.2f} kg", 0, 1)
    pdf.cell(0, 8, f"Masa del bloque m: {m:.2f} kg", 0, 1)
    pdf.cell(0, 8, f"Altura de caída h: {h:.2f} m", 0, 1)

    pdf.ln(5)
    pdf.cell(0, 10, "Resultados finales:", 0, 1)
    pdf.cell(0, 8, f"Tiempo total: {t_total:.3f} s", 0, 1)
    pdf.cell(0, 8, f"Velocidad final del bloque: {v_vals[-1]:.3f} m/s", 0, 1)
    pdf.cell(0, 8, f"Velocidad angular final: {w_vals[-1]:.3f} rad/s", 0, 1)
    pdf.cell(0, 8, f"Energía potencial final: {Ep_vals[-1]:.3f} J", 0, 1)
    pdf.cell(0, 8, f"Energía cinética total final: {Ec_total_vals[-1]:.3f} J", 0, 1)

    pdf.ln(5)
    pdf.cell(0, 10, "Evolución temporal (muestras):", 0, 1)
    pdf.set_font("Arial", size=10)

    df_small = pd.concat([df.head(5), df.tail(5)])
    for _, row in df_small.iterrows():
        texto = (f"t={row['Tiempo (s)']:.2f}s, h={row['Altura (m)']:.2f}m, "
                 f"v={row['Velocidad (m/s)']:.2f}m/s, w={row['Velocidad Angular (rad/s)']:.2f}rad/s, "
                 f"Ep={row['E_Potencial (J)']:.2f}J, Ec={row['E_Cinética (J)']:.2f}J")
        pdf.cell(0, 6, texto, 0, 1)

    # Compatibilidad: detectar si se necesita encode
    salida = pdf.output(dest='S')
    pdf_bytes = salida.encode('latin1') if isinstance(salida, str) else bytes(salida)
    return pdf_bytes

# Botón para generar y descargar PDF
if st.button("Generar informe PDF"):
    pdf_bytes = generar_pdf()
    st.download_button(
        label="Descargar informe PDF",
        data=pdf_bytes,
        file_name="informe_modelo_dinamico.pdf",
        mime="application/pdf"
    )

# Animaciones
if generar_anim:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Animación 1: Sistema físico
        fig1, ax1 = plt.subplots(figsize=(5, 5))
        ax1.set_xlim(-R - 0.2, R + 0.2)
        ax1.set_ylim(-0.5, h + 0.5)
        ax1.set_aspect('equal')
        ax1.grid(True)

        disco_ext = plt.Circle((0, h), R, fill=False, color='black', lw=2)
        disco_int = plt.Circle((0, h), r, fill=False, color='gray', lw=4)
        bloque = plt.Rectangle((-0.1, y_vals[0]), 0.2, 0.2, color='orange')
        linea, = ax1.plot([0, 0], [h, y_vals[0]], 'k-', lw=2)

        ax1.add_patch(disco_ext)
        ax1.add_patch(disco_int)
        ax1.add_patch(bloque)

        def update_dibujo(i):
            y = y_vals[i]
            bloque.set_xy((-0.1, y))
            linea.set_data([0, 0], [h, y])
            return bloque, linea

        ani1 = animation.FuncAnimation(fig1, update_dibujo, frames=n_frames, blit=True)
        gif1_path = os.path.join(tmpdir, "anim1.gif")
        ani1.save(gif1_path, writer=PillowWriter(fps=10))
        plt.close(fig1)
        st.image(gif1_path, caption="Vista frontal del sistema físico")

        # Animación 2: Energías
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.set_xlim(0, t_total)
        ax2.set_ylim(0, max(Ep_vals)*1.1)
        ax2.grid(True)
        ax2.set_xlabel("Tiempo (s)")
        ax2.set_ylabel("Energía (J)")
        line_ep, = ax2.plot([], [], color='blue', label='E. Potencial')
        line_ec, = ax2.plot([], [], color='red', label='E. Cinética')
        ax2.legend()

        def update_energia(i):
            line_ep.set_data(t_vals[:i], Ep_vals[:i])
            line_ec.set_data(t_vals[:i], Ec_total_vals[:i])
            return line_ep, line_ec

        ani2 = animation.FuncAnimation(fig2, update_energia, frames=n_frames, blit=True)
        gif2_path = os.path.join(tmpdir, "anim2.gif")
        ani2.save(gif2_path, writer=PillowWriter(fps=10))
        plt.close(fig2)
        st.image(gif2_path, caption="Energía potencial y cinética vs tiempo")

        # Animación 3: Velocidad angular
        fig3, ax3 = plt.subplots()
        ax3.set_xlim(0, t_total)
        ax3.set_ylim(0, max(w_vals)*1.1)
        ax3.grid(True)
        ax3.set_xlabel("Tiempo (s)")
        ax3.set_ylabel("Velocidad Angular (rad/s)")
        line_w, = ax3.plot([], [], color='green')

        def update_w(i):
            line_w.set_data(t_vals[:i], w_vals[:i])
            return line_w,

        ani3 = animation.FuncAnimation(fig3, update_w, frames=n_frames, blit=True)
        gif3_path = os.path.join(tmpdir, "anim3.gif")
        ani3.save(gif3_path, writer=PillowWriter(fps=10))
        plt.close(fig3)
        st.image(gif3_path, caption="Velocidad angular vs tiempo")
        
        st.markdown("""
Para comprobar que esta aplicacíon calcule correctamente cada variable se tomo el ejercicio 9.89 de el Libro 
Física Universitaria
YOUNG • FREEDMAN
Volumen 1
Sears Zemansky

""")

st.markdown("[Haz clic aquí para ir a Google](https://blog.espol.edu.ec/srpinarg/files/2014/05/Fisica-Universitaria-Sears-Zemansky-12ava-Edicion-Vol1.pdf)")