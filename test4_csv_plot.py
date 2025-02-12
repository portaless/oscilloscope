import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --- Charger le fichier CSV ---
csv_filename = "oscilloscope_log_20250204_102119.csv"  # Remplace par ton fichier CSV
df = pd.read_csv(csv_filename)

# --- Création des subplots ---
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# --- Tracer les données pour chaque canal ---
channels = ["CH1 (V)", "CH2 (V)", "CH3 (V)"]
lines = {}

for i, channel in enumerate(channels):
    lines[channel], = axs[i].plot(df["Time (s)"], df[channel], label=channel, color=f"C{i}")
    axs[i].set_ylabel("Tension (V)")
    axs[i].set_title(f"Signal {channel}")
    axs[i].legend()
    axs[i].grid(True)
    axs[i].set_yscale("linear")  # Échelle linéaire par défaut pour les ordonnées

axs[-1].set_xlabel("Temps (s)")

# Ajustement pour bien afficher les subplots
plt.subplots_adjust(hspace=0.3)

# --- Fonction pour basculer l'échelle de tous les subplots sur l'axe des X (temps) ---
def toggle_scale(event):
    if event.key.lower() == "l":  # Appuyer sur "L" pour changer l'échelle
        for ax in axs:
            current_scale_x = ax.get_xscale()  # Vérifie l'échelle de l'axe X
            new_scale_x = "log" if current_scale_x == "linear" else "linear"
            ax.set_xscale(new_scale_x)  # Applique le changement de l'échelle sur l'axe X
        plt.draw()

# --- Fonction pour gérer le zoom/dézoom avec la molette ---
def zoom(event):
    # Ajuster les limites en fonction de la molette
    factor = 1.1
    if event.button == "up":  # Molette vers le haut : zoom avant
        factor = 1 / factor
    elif event.button == "down":  # Molette vers le bas : zoom arrière
        factor = factor
    
    # Mettre à jour les limites des axes
    for ax in axs:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # Calculer les nouvelles limites
        ax.set_xlim([xmin * factor, xmax * factor])
        ax.set_ylim([ymin * factor, ymax * factor])

    plt.draw()

# --- Connecter les événements ---
fig.canvas.mpl_connect("key_press_event", toggle_scale)  # "L" pour log sur l'axe X
fig.canvas.mpl_connect("scroll_event", zoom)  # Molette de la souris pour zoom

# Affichage du graphique
plt.show()
