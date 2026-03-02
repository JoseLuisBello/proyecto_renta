import threading
import socket
import tkinter as tk
from tkinter import ttk, scrolledtext
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer


# =============================
# SERVIDOR MULTIHILO
# =============================

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


# =============================
# SERVICIO PRINCIPAL
# =============================

class RentalService:

    def __init__(self, logger):

        self.logger = logger

        self.vehicles = {
            "Auto 4 Puertas": {
                "capacity": 4,
                "cost": 600,
                "units": 5,
                "days": "Lunes a Domingo"
            },

            "Camioneta 4 Puertas": {
                "capacity": 5,
                "cost": 750,
                "units": 4,
                "days": "Martes a Domingo"
            },

            "Camioneta 3 Puertas": {
                "capacity": 10,
                "cost": 1200,
                "units": 3,
                "days": "Lunes a Domingo"
            }
        }

        self.lock = threading.Lock()


    def log(self, msg):

        self.logger(msg)


    def get_vehicles(self):

        self.log("Cliente solicitó lista de vehículos")

        info = {}

        for k, v in self.vehicles.items():

            info[k] = {
                "capacity": v["capacity"],
                "cost": v["cost"],
                "available": v["units"],
                "days": v["days"]
            }

        return info


    def rent(self, vehicle, persons, days):

        self.log(f"Solicitud: {vehicle}")

        if vehicle not in self.vehicles:
            return "Vehículo inválido"

        if persons <= 0 or days <= 0:
            return "Datos incorrectos"

        data = self.vehicles[vehicle]

        if persons > data["capacity"]:
            return "Excede capacidad"

        with self.lock:

            if data["units"] <= 0:
                self.log("Sin unidades")
                return "No disponible"

            data["units"] -= 1

            total = days * data["cost"]

            self.log(f"Renta confirmada: {vehicle}")

            return (
                "RENTA CONFIRMADA\n"
                f"Vehículo: {vehicle}\n"
                f"Personas: {persons}\n"
                f"Días: {days}\n"
                f"Total: ${total} MXN"
            )


# =============================
# INTERFAZ SERVIDOR
# =============================

class ServerGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("Servidor de Rentas")
        self.root.geometry("650x500")


        self.create_widgets()


        threading.Thread(
            target=self.start_server,
            daemon=True
        ).start()


    def create_widgets(self):

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)


        ttk.Label(
            frame,
            text="Servidor de Rentas",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)


        self.ip_label = ttk.Label(frame, text="Iniciando...")
        self.ip_label.pack(pady=5)


        self.log_area = scrolledtext.ScrolledText(
            frame,
            height=20,
            font=("Consolas", 11)
        )

        self.log_area.pack(fill="both", expand=True, pady=10)


    def log(self, msg):

        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)


    def start_server(self):

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)


        server = ThreadedXMLRPCServer(("0.0.0.0", 8000))

        service = RentalService(self.log)

        server.register_instance(service)


        self.ip_label.config(
            text=f"Servidor activo en: http://{ip}:8000"
        )

        self.log("Servidor iniciado")
        self.log(f"IP: {ip}")

        server.serve_forever()



# =============================
# MAIN
# =============================

def main():

    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()