import tkinter as tk
from tkinter import messagebox, ttk
import requests

def get_kilometer_von_orten(start, ziel, api_key):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {'Authorization': api_key}
    # Hole Koordinaten
    def get_coords(ort):
        geo_url = f"https://api.openrouteservice.org/geocode/search?api_key={api_key}&text={ort}"
        resp = requests.get(geo_url).json()
        coords = resp['features'][0]['geometry']['coordinates']
        return coords
    start_coords = get_coords(start)
    ziel_coords = get_coords(ziel)
    body = {
        "coordinates": [start_coords, ziel_coords]
    }
    resp = requests.post(url, json=body, headers=headers)
    dist_m = resp.json()['features'][0]['properties']['segments'][0]['distance']
    return round(dist_m / 1000, 1)

def berechne_lademeter(palettengroesse: str, menge: int, stapelbarkeit: int) -> float:
    try:
        teile = palettengroesse.lower().replace(" ", "").split("x")
        if len(teile) != 3:
            raise ValueError("Ungültiges Format. Bitte verwende das Format 'LxBxH' in cm.")

        laenge_cm = float(teile[0])
        breite_cm = float(teile[1])

        laenge_m = laenge_cm / 100
        breite_m = breite_cm / 100

        lademeter_pro_palette = (breite_m / 2.4) * laenge_m
        gesamt_lademeter = lademeter_pro_palette * menge

        # Stapelbarkeit berücksichtigen
        if stapelbarkeit > 0:
            gesamt_lademeter = gesamt_lademeter / (2 ** stapelbarkeit)
        # stapelbarkeit == 0: keine Änderung

        return round(gesamt_lademeter, 2)

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler: {e}")
        return 0.0

def berechne_preis(kilometer: float, fahrzeug: str) -> float:
    grundpreis = 80.0
    grund_km = 40
    km_preise = {
        "Sprinter": 0.40,
        "Planensprinter": 0.60,
        "Klein LKW": 0.65,
        "7,5 Tonnen LKW": 0.75,
        "Tautliner": 0.90,
        "Mega": 1.00,
        "Jumbo": 1.20
    }
    km_preis = km_preise.get(fahrzeug, 0.35)
    if kilometer <= grund_km:
        preis = grundpreis
    else:
        preis = grundpreis + (kilometer - grund_km) * km_preis
    return round(preis, 2)

def berechnen():
    palettengroesse = entry_groesse.get()
    try:
        menge = int(entry_menge.get())
        stapelbarkeit = int(entry_stapel.get())
        kilometer = float(entry_km.get())
        fahrzeug = combo_fahrzeug.get()
        if stapelbarkeit == 0:
            messagebox.showinfo("Hinweis", "Stapelbarkeit 0 bedeutet: Paletten sind nicht stapelbar.")
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gib gültige Zahlen ein.")
        label_ergebnis.config(text="❌ Fehlerhafte Eingabe!")
        return

    lademeter = berechne_lademeter(palettengroesse, menge, stapelbarkeit)
    preis = berechne_preis(kilometer, fahrzeug)
    label_ergebnis.config(
        text=f"✅ Die berechneten Lademeter betragen: {lademeter} m\n💶 Ungefährer Preis: {preis} €"
    )

root = tk.Tk()
root.title("Lademeter-Berechnungstool")

tk.Label(root, text="Palettengröße (z.B. 120x100x100):").grid(row=0, column=0, sticky="e")
entry_groesse = tk.Entry(root)
entry_groesse.grid(row=0, column=1)

tk.Label(root, text="Anzahl der Paletten:").grid(row=1, column=0, sticky="e")
entry_menge = tk.Entry(root)
entry_menge.grid(row=1, column=1)

tk.Label(root, text="Stapelbarkeit (z.B. 1, 2, 3):").grid(row=2, column=0, sticky="e")
entry_stapel = tk.Entry(root)
entry_stapel.grid(row=2, column=1)

tk.Label(root, text="Kilometer:").grid(row=3, column=0, sticky="e")
entry_km = tk.Entry(root)
entry_km.grid(row=3, column=1)

tk.Label(root, text="Fahrzeugtyp:").grid(row=4, column=0, sticky="e")
combo_fahrzeug = ttk.Combobox(root, values=[
    "Sprinter", "Planensprinter", "Klein LKW", "7,5 Tonnen LKW", "Tautliner", "Mega", "Jumbo"
])
combo_fahrzeug.current(0)
combo_fahrzeug.grid(row=4, column=1)

tk.Label(root, text="").grid(row=6)  # Leerzeile für Abstand
tk.Label(root, text="Hinweis: Stapelbarkeit 0 bedeutet, dass Paletten nicht stapelbar sind.").grid(row=5, column=0, columnspan=2)
tk.Label(root, text="").grid(row=6)  # Leerzeile für Abstand
tk.Label(root, text="Die Berechnung des Preises ist eine Schätzung und kann je nach Fahrzeug und Route variieren.").grid(row=6, column=0, columnspan=2)

btn_berechnen = tk.Button(root, text="Berechnen", command=berechnen)
btn_berechnen.grid(row=7, column=0, columnspan=2, pady=10)

label_ergebnis = tk.Label(root, text="Ergebnis wird hier angezeigt.")
label_ergebnis.grid(row=8, column=0, columnspan=2)

root.mainloop()


