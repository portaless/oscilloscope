import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time

# Connexion à l'oscilloscope
visa_address = 'USB0::0x0699::0x03C7::C010286::INSTR'
rm = pyvisa.ResourceManager()
dpo2k = rm.open_resource(visa_address)
dpo2k.timeout = 60000  # Timeout augmenté à 60s pour éviter les blocages

# Configuration
dpo2k.write("ACQUIRE:STATE RUN")  # Acquisition continue
dpo2k.write("HEADER OFF")  # Désactiver les en-têtes
dpo2k.write("DATA:ENC RIB")  # Format binaire MSB
dpo2k.write("DATA:START 1")
dpo2k.write("DATA:STOP 1000")  # Réduire le nombre d'échantillons pour éviter la surcharge

# Mode interactif Matplotlib
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], label="CH1")
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Voltage (V)")
ax.legend()
ax.grid(True)

# Fonction d'acquisition continue
def update_plot():
    dpo2k.write("DATA:SOURCE CH1")
    dpo2k.write("CURVE?")
    raw_data = dpo2k.read_raw()

    # Traitement des données
    header_length = int(raw_data[1:2])
    data_length = int(raw_data[2:2+header_length])
    samples = np.frombuffer(raw_data[2+header_length:2+header_length+data_length], dtype=np.int8)

    # Mise à l'échelle
    x_incr = float(dpo2k.query("WFMO:XINCR?"))
    y_mult = float(dpo2k.query("WFMO:YMULT?"))
    y_off = float(dpo2k.query("WFMO:YOFF?"))
    y_zero = float(dpo2k.query("WFMO:YZERO?"))

    scaled_samples = (samples * y_mult) + (y_zero + y_off)
    time_base = np.linspace(0, len(scaled_samples) * x_incr, len(scaled_samples))

    # Mise à jour du graphique
    line.set_xdata(time_base)
    line.set_ydata(scaled_samples)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.1)  # Pause pour laisser le temps à l'affichage

# Boucle d'acquisition en continu
try:
    while True:
        update_plot()
        time.sleep(0.5)  # Réduction de la charge CPU
except KeyboardInterrupt:
    print("Arrêt par l'utilisateur.")
    dpo2k.close()
