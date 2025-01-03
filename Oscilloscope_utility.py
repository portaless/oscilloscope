import pyvisa

class OscilloscopeHandler:
    def __init__(self, resource_manager_backend='@ivi'):
        self.rm = pyvisa.ResourceManager(resource_manager_backend)
        self.oscilloscope = None

    def list_resources(self):
        """List available VISA resources."""
        try:
            resources = self.rm.list_resources()
            print("Ressources disponibles :", resources)
            return resources
        except pyvisa.errors.VisaIOError as e:
            print(f"Erreur lors de la liste des ressources : {e}")
            return []

    def connect_to_instrument(self, resource_name):
        """Connect to an instrument by its resource name."""
        try:
            self.oscilloscope = self.rm.open_resource(resource_name)
            idn = self.oscilloscope.query("*IDN?")
            print("Instrument trouvé :", idn)
            return idn
        except pyvisa.errors.VisaIOError as e:
            print(f"Erreur lors de la connexion à l'instrument : {e}")
            return None

    def capture_screenshot(self, filename="oscilloscope_screenshot.png"):
        """Capture a screenshot from the oscilloscope and save it to a file."""
        if not self.oscilloscope:
            print("Aucun instrument connecté.")
            return

        try:
            # Configure screenshot format and trigger capture
            self.oscilloscope.write("HARDCOPY:FORMAT PNG")
            self.oscilloscope.write("HARDCOPY START")

            # Read binary screenshot data
            screenshot_data = self.oscilloscope.read_raw()

            # Save screenshot to file
            with open(filename, "wb") as screenshot_file:
                screenshot_file.write(screenshot_data)

            print(f"Capture d'écran enregistrée sous '{filename}'")
        except pyvisa.errors.VisaIOError as e:
            print(f"Erreur lors de la capture d'écran : {e}")

    def close(self):
        """Close the connection to the oscilloscope."""
        if self.oscilloscope:
            self.oscilloscope.close()
            print("Connexion à l'instrument fermée.")
        self.rm.close()
        print("Gestionnaire de ressources fermé.")

# Exemple d'utilisation
def main():
    handler = OscilloscopeHandler()

    try:
        # Lister les ressources disponibles
        resources = handler.list_resources()

        if resources:
            # Connecter au premier instrument détecté
            handler.connect_to_instrument(resources[0])

            # Capturer une capture d'écran
            handler.capture_screenshot()
        else:
            print("Aucune ressource VISA disponible.")
    finally:
        # Assurez-vous de fermer la connexion
        handler.close()

if __name__ == "__main__":
    main()
