import tkinter as tk
from tkinter import messagebox

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

def berechnen():
    palettengroesse = entry_groesse.get()
    try:
        menge = int(entry_menge.get())
        stapelbarkeit = int(entry_stapel.get())
        print(f"Berechne mit Stapelbarkeit: {stapelbarkeit}")  # Debug-Ausgabe
        if stapelbarkeit == 0:
            messagebox.showinfo("Hinweis", "Stapelbarkeit 0 bedeutet: Paletten sind nicht stapelbar.")
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gib ganze Zahlen für Menge und Stapelbarkeit ein.")
        label_ergebnis.config(text="❌ Fehlerhafte Eingabe!")
        return

    lademeter = berechne_lademeter(palettengroesse, menge, stapelbarkeit)
    label_ergebnis.config(text=f"✅ Die berechneten Lademeter betragen: {lademeter} m")

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

btn_berechnen = tk.Button(root, text="Berechnen", command=berechnen)
btn_berechnen.grid(row=3, column=0, columnspan=2, pady=10)

label_ergebnis = tk.Label(root, text="Ergebnis wird hier angezeigt.")
label_ergebnis.grid(row=4, column=0, columnspan=2)

root.mainloop()