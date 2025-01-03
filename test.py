import pyvisa
import time

rm = pyvisa.ResourceManager()
oscilloscope = rm.open_resource("USB0::0x0699::0x03C7::C010286::INSTR")
oscilloscope.timeout = 20000  # Timeout de 20 secondes

try:
    # Identifiez l'instrument
    print("IDN:", oscilloscope.query("*IDN?"))

    # Activez le canal 3
    oscilloscope.write(":CHANnel3:DISPlay ON")

    # Attendez un peu pour la configuration
    time.sleep(1)

    # Essayez de mesurer la tension d'amplitude
    print("Essai de mesure d'amplitude...")
    response = oscilloscope.query(":MEASure:VAMPlitude?")
    print("Amplitude mesurée :", response)

except pyvisa.errors.VisaIOError as e:
    print(f"Erreur VISA : {e}")
finally:
    oscilloscope.close()
    rm.close()
