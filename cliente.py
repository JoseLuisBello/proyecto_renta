import xmlrpc.client
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time


# =============================
# CONFIG
# =============================

SERVER_IP = "10.10.200.6"   # 👈 CAMBIA ESTA IP
PORT = 8000


# =============================
# CLIENTE APP
# =============================

class ClientGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("Cliente de Rentas")
        self.root.geometry("750x600")
        self.root.configure(bg="#f1f5f9")


        self.connect()


        self.setup_style()
        self.create_widgets()


    # =============================
    # CONECTAR
    # =============================

    def connect(self):

        try:

            self.server = xmlrpc.client.ServerProxy(
                f"http://{SERVER_IP}:{PORT}",
                allow_none=True
            )

            self.vehicles = self.server.get_vehicles()

        except:

            messagebox.showerror(
                "Error",
                "No se pudo conectar al servidor"
            )

            self.root.quit()


    # =============================
    # ESTILO
    # =============================

    def setup_style(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold"),
            foreground="#1e40af",
            background="#f1f5f9"
        )

        style.configure(
            "TLabel",
            font=("Segoe UI", 12),
            background="#f1f5f9"
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            background="#2563eb",
            foreground="white"
        )


    # =============================
    # UI
    # =============================

    def create_widgets(self):

        main = ttk.Frame(self.root, padding=25)
        main.pack(fill="both", expand=True)


        ttk.Label(
            main,
            text="Cliente de Renta",
            style="Title.TLabel"
        ).pack(pady=10)


        # Tabla
        table_frame = ttk.LabelFrame(
            main,
            text="Disponibles",
            padding=15
        )

        table_frame.pack(fill="x", pady=10)


        self.tree = ttk.Treeview(
            table_frame,
            columns=("Tipo", "cap", "cost", "units", "days"),
            show="headings",
            height=6
        )
        
        self.tree.heading("Tipo", text="Vehiculo")
        self.tree.heading("cap", text="Capacidad")
        self.tree.heading("units", text="Unidades")
        self.tree.heading("cost", text="Costo")
        self.tree.heading("days", text="Días")


        for col in ("Tipo", "cap", "cost", "units", "days"):
            self.tree.column(col, anchor="center", width=120)


        self.tree.pack(fill="x")


        self.load_data()


        # Formulario
        form = ttk.LabelFrame(
            main,
            text="Rentar",
            padding=20
        )

        form.pack(fill="x", pady=15)


        ttk.Label(form, text="Vehículo:").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Personas:").grid(row=1, column=0, sticky="w")
        ttk.Label(form, text="Días:").grid(row=2, column=0, sticky="w")


        self.vehicle = tk.StringVar()
        self.persons = tk.StringVar()
        self.days = tk.StringVar()


        self.combo = ttk.Combobox(
            form,
            values=list(self.vehicles.keys()),
            textvariable=self.vehicle,
            state="readonly",
            width=35
        )

        self.combo.grid(row=0, column=1, pady=5)


        ttk.Entry(form, textvariable=self.persons).grid(row=1, column=1, pady=5)
        ttk.Entry(form, textvariable=self.days).grid(row=2, column=1, pady=5)


        # Botones
        btns = ttk.Frame(main)
        btns.pack(pady=15)


        ttk.Button(
            btns,
            text="Rentar",
            style="Accent.TButton",
            command=self.start_rent,
            width=14
        ).pack(side="left", padx=6)


        ttk.Button(
            btns,
            text="Actualizar",
            command=self.refresh,
            width=14
        ).pack(side="left", padx=6)


        ttk.Button(
            btns,
            text="Salir",
            command=self.root.quit,
            width=14
        ).pack(side="left", padx=6)


        # Historial
        history = ttk.LabelFrame(
            main,
            text="Historial",
            padding=15
        )

        history.pack(fill="both", expand=True)


        self.text = tk.Text(
            history,
            height=8,
            font=("Consolas", 11),
            bg="#f8fafc"
        )

        self.text.pack(fill="both", expand=True)


    # =============================
    # DATOS
    # =============================

    def load_data(self):

        for row in self.tree.get_children():
            self.tree.delete(row)


        for name, v in self.vehicles.items():

            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    v["capacity"],
                    f"${v['cost']}",
                    v["available"],
                    v["days"]
                )
            )


    # =============================
    # RENTA
    # =============================

    def start_rent(self):

        threading.Thread(
            target=self.rent
        ).start()


    def rent(self):

        try:

            vehicle = self.vehicle.get()
            persons = int(self.persons.get())
            days = int(self.days.get())

        except:

            messagebox.showwarning(
                "Error",
                "Datos inválidos"
            )

            return


        response = self.server.rent(
            vehicle,
            persons,
            days
        )


        self.text.insert(
            tk.END,
            response + "\n\n"
        )


        self.refresh()


    # =============================
    # REFRESH
    # =============================

    def refresh(self):

        self.vehicles = self.server.get_vehicles()

        self.load_data()



# =============================
# MAIN
# =============================

def main():

    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()