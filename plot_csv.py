import pandas as pd
import matplotlib.pyplot as plt

def plot_csv_data(filename="oscilloscope_data.csv"):
    """Trace la courbe des données enregistrées dans un CSV."""
    try:
        # Lire le fichier CSV
        df = pd.read_csv(filename)

        # Vérifier si le fichier contient des données
        if df.empty:
            print("Le fichier CSV est vide.")
            return

        # Extraire les colonnes
        time_values = df.iloc[:, 0]  # Première colonne (temps)
        voltage_values = df.iloc[:, 1]  # Deuxième colonne (tension)

        # Tracer la courbe
        plt.figure(figsize=(10, 5))
        plt.plot(time_values, voltage_values, label="Signal mesuré", color="b")

        # Ajouter des labels et un titre
        plt.xlabel("Temps (s)")
        plt.ylabel("Tension (V)")
        plt.title("Signal mesuré par l'oscilloscope")
        plt.legend()
        plt.grid()

        # Afficher la courbe
        plt.show()

    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")

# --- Exécuter la fonction ---
plot_csv_data("data.csv")  # Remplace "data.csv" par ton fichier CSV réel
