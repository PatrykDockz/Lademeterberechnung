import tkinter as tk
from tkinter import messagebox, ttk
import urllib.parse
import urllib.request
import json
import ssl

def get_kilometer_von_orten(start, ziel):
    """Berechnet die Entfernung zwischen zwei Orten - vereinfachte Luftlinie"""
    try:
        # SSL-Context für macOS erstellen
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Geocoding mit Nominatim (OpenStreetMap)
        def get_coords(ort):
            ort_encoded = urllib.parse.quote(ort)
            url = f"https://nominatim.openstreetmap.org/search?q={ort_encoded}&format=json&limit=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Lademeter-Tool/1.0'})
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
                data = json.loads(response.read().decode())
                if not data:
                    raise ValueError(f"Ort '{ort}' nicht gefunden")
                return [float(data[0]['lat']), float(data[0]['lon'])]
        
        start_coords = get_coords(start)
        ziel_coords = get_coords(ziel)
        
        # Berechne Luftlinie mit Haversine-Formel (genauer als API bei Timeout-Problemen)
        import math
        lat1, lon1 = math.radians(start_coords[0]), math.radians(start_coords[1])
        lat2, lon2 = math.radians(ziel_coords[0]), math.radians(ziel_coords[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Erdradius in km
        r = 6371
        luftlinie = r * c
        
        # Faktor für Straßenentfernung (ca. 1.3x Luftlinie)
        strassen_km = luftlinie * 1.3
        
        return round(strassen_km, 1)
    except Exception as e:
        raise Exception(f"Fehler bei der Routenberechnung: {str(e)}")

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
    grundpreis = 65.0
    grund_km = 40
    km_preise = {
        "Sprinter": 0.35,
        "Planensprinter": 0.50,
        "Klein LKW": 0.55,
        "7,5 Tonnen LKW": 0.65,
        "Tautliner": 0.75,
        "Mega": 0.85,
        "Jumbo": 1.00
    }
    km_preis = km_preise.get(fahrzeug, 0.30)
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
        fahrzeug = combo_fahrzeug.get()
        
        # Prüfe ob Orte oder Kilometer eingegeben wurden
        startort = entry_start.get().strip()
        zielort = entry_ziel.get().strip()
        km_manuell = entry_km.get().strip()
        
        if startort and zielort:
            # Berechne Kilometer automatisch (kostenlos, kein API-Key nötig)
            try:
                label_ergebnis.config(text="🔄 Berechne Route...")
                root.update()
                kilometer = get_kilometer_von_orten(startort, zielort)
                label_ergebnis.config(text=f"📍 Entfernung berechnet: {kilometer} km")
                root.update()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler bei der Routenberechnung: {e}\n\nBitte trage die Kilometer manuell ein.")
                return
        elif km_manuell:
            # Verwende manuelle Kilometereingabe
            kilometer = float(km_manuell)
        else:
            messagebox.showerror("Fehler", "Bitte gib entweder Start- und Zielort ODER die Kilometer manuell ein.")
            return
        
        if stapelbarkeit == 0:
            messagebox.showinfo("Hinweis", "Stapelbarkeit 0 bedeutet: Paletten sind nicht stapelbar.")
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gib gültige Zahlen ein.")
        label_ergebnis.config(text="❌ Fehlerhafte Eingabe!")
        return

    lademeter = berechne_lademeter(palettengroesse, menge, stapelbarkeit)
    preis = berechne_preis(kilometer, fahrzeug)
    label_ergebnis.config(
        text=f"✅ Die berechneten Lademeter betragen: {lademeter} m\n📏 Entfernung: {kilometer} km\n💶 Ungefährer Preis: {preis} €"
    )

root = tk.Tk()
root.title("Lademeter-Berechnungstool")

# Font-Definitionen
label_font = ("Arial", 12)
entry_font = ("Arial", 12)

tk.Label(root, text="Palettengröße (z.B. 120x100x100):", font=label_font).grid(row=0, column=0, sticky="e", padx=10, pady=8)
entry_groesse = tk.Entry(root, width=30, font=entry_font)
entry_groesse.grid(row=0, column=1, padx=10, pady=8)

tk.Label(root, text="Anzahl der Paletten:", font=label_font).grid(row=1, column=0, sticky="e", padx=10, pady=8)
entry_menge = tk.Entry(root, width=30, font=entry_font)
entry_menge.grid(row=1, column=1, padx=10, pady=8)

tk.Label(root, text="Stapelbarkeit (z.B. 1, 2, 3):", font=label_font).grid(row=2, column=0, sticky="e", padx=10, pady=8)
entry_stapel = tk.Entry(root, width=30, font=entry_font)
entry_stapel.grid(row=2, column=1, padx=10, pady=8)

# Trennlinie für Route/Kilometer Sektion
tk.Label(root, text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", font=("Arial", 10)).grid(row=3, column=0, columnspan=2, pady=10)

tk.Label(root, text="Startort (z.B. Berlin):", font=label_font).grid(row=4, column=0, sticky="e", padx=10, pady=8)
entry_start = tk.Entry(root, width=30, font=entry_font)
entry_start.grid(row=4, column=1, padx=10, pady=8)

tk.Label(root, text="Zielort (z.B. München):", font=label_font).grid(row=5, column=0, sticky="e", padx=10, pady=8)
entry_ziel = tk.Entry(root, width=30, font=entry_font)
entry_ziel.grid(row=5, column=1, padx=10, pady=8)

tk.Label(root, text="───── ODER ─────", font=("Arial", 10)).grid(row=6, column=0, columnspan=2, pady=8)

tk.Label(root, text="Kilometer (manuell):", font=label_font).grid(row=7, column=0, sticky="e", padx=10, pady=8)
entry_km = tk.Entry(root, width=30, font=entry_font)
entry_km.grid(row=7, column=1, padx=10, pady=8)

tk.Label(root, text="Fahrzeugtyp:", font=label_font).grid(row=8, column=0, sticky="e", padx=10, pady=8)
combo_fahrzeug = ttk.Combobox(root, values=[
    "Sprinter", "Planensprinter", "Klein LKW", "7,5 Tonnen LKW", "Tautliner", "Mega", "Jumbo"
], width=28, font=entry_font, state="readonly")
combo_fahrzeug.current(0)
combo_fahrzeug.grid(row=8, column=1, padx=10, pady=8)

tk.Label(root, text="").grid(row=9)  # Leerzeile für Abstand
tk.Label(root, text="💡 Tipp: Einfach Start- und Zielort eingeben - Entfernung wird automatisch berechnet!", font=("Arial", 10)).grid(row=10, column=0, columnspan=2, pady=5)
tk.Label(root, text="Hinweis: Stapelbarkeit 0 bedeutet, dass Paletten nicht stapelbar sind.", font=("Arial", 10)).grid(row=11, column=0, columnspan=2, pady=3)
tk.Label(root, text="Die Berechnung des Preises ist eine Schätzung und kann variieren.", font=("Arial", 10)).grid(row=12, column=0, columnspan=2, pady=3)

btn_berechnen = tk.Button(root, text="Berechnen", command=berechnen, bg="#2196F3", fg="white", font=("Arial", 14, "bold"), padx=40, pady=10, cursor="hand2")
btn_berechnen.grid(row=13, column=0, columnspan=2, pady=15)

label_ergebnis = tk.Label(root, text="Ergebnis wird hier angezeigt.", font=("Arial", 12), wraplength=500)
label_ergebnis.grid(row=14, column=0, columnspan=2, pady=10)

root.mainloop()


