import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
import time

# Adresse de l'oscilloscope
visa_address = 'USB0::0x0699::0x03C7::C010286::INSTR'

# Connexion à l'oscilloscope
rm = pyvisa.ResourceManager()
dpo2k = rm.open_resource(visa_address)
dpo2k.timeout = 20000  # Augmenter le timeout pour éviter les erreurs
dpo2k.read_termination = '\n'
dpo2k.write_termination = '\n'

# Vérifier la connexion avec l'oscilloscope
print(dpo2k.query('*IDN?'))

# Récupérer les paramètres du temps/div de l'oscilloscope
time_div = float(dpo2k.query('horizontal:scale?'))  # En secondes/division
total_time = time_div * 10  # Oscilloscope affiche sur 10 divisions

# Définir le nombre de points en fonction de l'échelle de temps
if total_time > 1:  # Si on est en 1s/div ou plus
    record = 1000  # Réduire le nombre de points pour éviter la surcharge
else:
    record = 2000  # Nombre de points en temps court

# Configurer les paramètres de l'oscilloscope
dpo2k.write('wfmo:byt_n 1')  # Format de données en byte
dpo2k.write('header 0')  # Désactiver les en-têtes
dpo2k.write('data:encdg rib')  # Encodage signé, MSB en premier
dpo2k.write('data:comp singular_yt')  # Compression des données
dpo2k.write('data:resolution full')  # Résolution maximale
dpo2k.write(f'data:start 1')
dpo2k.write(f'data:stop {record}')

# Variables pour stocker les données
data_ch1, data_ch2, data_ch3 = np.zeros(record), np.zeros(record), np.zeros(record)
time_base = np.linspace(0, total_time, record)  # Ajustement dynamique du temps

# Fonction pour récupérer les données d'un canal
def get_channel_data(channel):
    dpo2k.write(f'data:source CH{channel}')  # Sélectionner le canal
    dpo2k.write('curve?')  # Demander les données de la courbe
    raw_data = dpo2k.read_raw()  # Lire les données brutes

    # Extraction et conversion des données
    header_length = int(raw_data[1:2])
    data_length = int(raw_data[2:2+header_length])
    samples = np.frombuffer(raw_data[2+header_length:2+header_length+data_length], dtype=np.int8)

    # Récupérer les valeurs de mise à l'échelle
    y_incr = float(dpo2k.query('wfmo:ymult?'))  # Incrément vertical (volts/div)
    y_off = float(dpo2k.query('wfmo:yoff?'))    # Décalage vertical
    y_zero = float(dpo2k.query('wfmo:yzero?'))  # Référence verticale

    # Appliquer les échelles et les décalages
    scaled_samples = (samples * y_incr) + (y_zero + y_off)

    return scaled_samples

# Fonction pour l'acquisition des données en continu
def acquire_data():
    global data_ch1, data_ch2, data_ch3
    while True:
        start_time = time.time()
        
        # Récupérer les données
        data_ch1 = get_channel_data(1)
        data_ch2 = get_channel_data(2)
        data_ch3 = get_channel_data(3)

        # Adapter le délai d'acquisition pour éviter les pertes de données
        elapsed_time = time.time() - start_time
        sleep_time = max(0.05, total_time / 10 - elapsed_time)  # Ajustement dynamique
        time.sleep(sleep_time)

# Fonction pour mettre à jour le graphique
def update(frame):
    axs[0].cla()
    axs[1].cla()
    axs[2].cla()

    axs[0].plot(time_base, data_ch1, label='CH1', color='blue')
    axs[0].set_ylabel("Voltage (V)")
    axs[0].set_title("Channel 1")
    axs[0].grid(True)

    axs[1].plot(time_base, data_ch2, label='CH2', color='green')
    axs[1].set_ylabel("Voltage (V)")
    axs[1].set_title("Channel 2")
    axs[1].grid(True)

    axs[2].plot(time_base, data_ch3, label='CH3', color='red')
    axs[2].set_xlabel("Time (s)")
    axs[2].set_ylabel("Voltage (V)")
    axs[2].set_title("Channel 3")
    axs[2].grid(True)

    plt.tight_layout()

# Création des figures
fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)

# Lancer l'acquisition dans un thread séparé
acquisition_thread = Thread(target=acquire_data, daemon=True)
acquisition_thread.start()

# Animation du graphique
ani = FuncAnimation(fig, update, interval=max(100, total_time * 100), blit=False)

# Afficher le graphique
plt.show()

# Fermer la session de l'oscilloscope après la fin de l'acquisition
dpo2k.close()

