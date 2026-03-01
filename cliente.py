import xmlrpc.client
import tkinter as tk
from tkinter import ttk, messagebox
import time

class RentalClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Renta de Autos")
        self.root.geometry("650x750")
        self.root.configure(bg="#f5f7fa")  # Fondo gris claro moderno
        
        self.server = xmlrpc.client.ServerProxy("http://localhost:8000")
        self.vehicles = self.server.get_vehicles()
        self.rentals = 0
        
        # Estilo moderno
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 12), background="#f5f7fa")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1a3c6d")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=12)
        style.map("TButton", background=[("active", "#005f99")], foreground=[("active", "white")])
        style.configure("Accent.TButton", background="#007acc", foreground="white")
        style.map("Accent.TButton", background=[("active", "#005f99")])
        style.configure("TCombobox", font=("Segoe UI", 12))
        style.configure("TEntry", font=("Segoe UI", 12))
        style.configure("Info.TLabel", font=("Segoe UI", 11), foreground="#555")
        
        # Frame principal con padding
        main_frame = ttk.Frame(root, padding=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Renta de Vehículos - Marzo 2026", style="Title.TLabel").pack(pady=(0, 15))
        
        # Contador de rentas
        self.rental_count_label = ttk.Label(main_frame, text="Rentas realizadas: 0 / 3", font=("Segoe UI", 12, "bold"), foreground="#2c7be5")
        self.rental_count_label.pack(pady=(0, 20))
        
        # Sección vehículos disponibles
        vehicle_frame = ttk.LabelFrame(main_frame, text=" Vehículos Disponibles ", padding=15)
        vehicle_frame.pack(fill=tk.X, pady=10)
        
        self.info_text = tk.Text(vehicle_frame, height=7, width=70, bg="#ffffff", relief="flat", font=("Segoe UI", 11), wrap="word")
        self.info_text.pack(fill=tk.X, pady=5)
        self.display_vehicles()
        self.info_text.config(state='disabled')
        
        # Formulario
        form_frame = ttk.LabelFrame(main_frame, text=" Realizar Renta ", padding=20)
        form_frame.pack(fill=tk.X, pady=15)
        
        # Tipo de vehículo + descripción dinámica
        ttk.Label(form_frame, text="Selecciona el vehículo:").grid(row=0, column=0, sticky="w", pady=8)
        self.vehicle_var = tk.StringVar()
        self.vehicle_combo = ttk.Combobox(form_frame, textvariable=self.vehicle_var, values=list(self.vehicles.keys()), state="readonly", width=35)
        self.vehicle_combo.grid(row=0, column=1, pady=8, sticky="ew")
        self.vehicle_combo.bind("<<ComboboxSelected>>", self.update_vehicle_description)
        
        # Descripción dinámica del vehículo seleccionado
        self.desc_label = ttk.Label(form_frame, text="Selecciona un vehículo para ver sus características", style="Info.TLabel", wraplength=550, justify="left")
        self.desc_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="w")
        
        ttk.Label(form_frame, text="Número de ocupantes:").grid(row=2, column=0, sticky="w", pady=8)
        self.occupants_entry = ttk.Entry(form_frame, width=38)
        self.occupants_entry.grid(row=2, column=1, pady=8, sticky="ew")
        
        ttk.Label(form_frame, text="Días de renta:").grid(row=3, column=0, sticky="w", pady=8)
        self.days_entry = ttk.Entry(form_frame, width=38)
        self.days_entry.grid(row=3, column=1, pady=8, sticky="ew")
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        rent_button = ttk.Button(buttons_frame, text="Confirmar Renta", command=self.rent_vehicle, style="Accent.TButton", width=20)
        rent_button.pack(side=tk.LEFT, padx=10)
        
        exit_button = ttk.Button(buttons_frame, text="Salir", command=root.quit, width=12)
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # Barra de progreso (simulada)
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", length=400)
        self.progress.pack(pady=10)
        self.progress.stop()
        
        # Área de resultados
        result_frame = ttk.LabelFrame(main_frame, text=" Resultados ", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.response_text = tk.Text(result_frame, height=10, width=70, bg="#f8fff8", relief="flat", font=("Segoe UI", 11), wrap="word")
        self.response_text.pack(fill=tk.BOTH, expand=True)
    
    def display_vehicles(self):
        self.info_text.delete("1.0", tk.END)
        for key, val in self.vehicles.items():
            self.info_text.insert(tk.END, f"• {key.replace('_', ' ').title()}\n")
            self.info_text.insert(tk.END, f"  Cupo máximo: {val['capacity']} personas\n")
            self.info_text.insert(tk.END, f"  Costo por día: ${val['cost']:,}\n")
            self.info_text.insert(tk.END, f"  Disponible: {val['days_available']}\n\n")
    
    def update_vehicle_description(self, event=None):
        vehicle = self.vehicle_var.get()
        if not vehicle:
            self.desc_label.config(text="Selecciona un vehículo para ver sus características")
            return
        
        v = self.vehicles[vehicle]
        desc = (
            f" {vehicle.replace('_', ' ').title()}\n"
            f"• Capacidad máxima: {v['capacity']} personas\n"
            f"• Costo diario: ${v['cost']:,} MXN\n"
            f"• Días disponibles: {v['days_available']}\n"
            f"Ideal para familias, viajes de trabajo o grupos pequeños/grandes según el modelo."
        )
        self.desc_label.config(text=desc)
    
    def rent_vehicle(self):
        if self.rentals >= 3:
            messagebox.showinfo("Límite alcanzado", "Ya has rentado el máximo permitido (3 vehículos).")
            return
        
        vehicle_type = self.vehicle_var.get()
        if not vehicle_type:
            messagebox.showwarning("Selección requerida", "Por favor selecciona un tipo de vehículo.")
            return
        
        try:
            occupants = int(self.occupants_entry.get())
            days = int(self.days_entry.get())
            if occupants < 1 or days < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Datos inválidos", "Ingresa números enteros positivos para ocupantes y días.")
            return
        
        # Simular procesamiento
        self.progress.start()
        self.root.update()
        time.sleep(1.2)  # Pequeño delay visual
        self.progress.stop()
        
        response = self.server.rent(vehicle_type, occupants, days)
        self.response_text.insert(tk.END, f"→ {response}\n\n")
        
        if "Confirmación" in response:
            self.response_text.tag_add("ok", "end-2l", "end")
            self.response_text.tag_config("ok", foreground="#28a745", font=("Segoe UI", 11, "bold"))
        
        elif "No hay disponibilidad" in response:
            self.response_text.tag_add("wait", "end-2l", "end")
            self.response_text.tag_config("wait", foreground="#dc3545")
        
        self.rentals += 1
        self.rental_count_label.config(text=f"Rentas realizadas: {self.rentals} / 3")
        
        if self.rentals >= 3:
            messagebox.showinfo("¡Completado!", "Has rentado 3 vehículos. Gracias por usar nuestro sistema.")
            self.root.after(1500, self.root.quit)
        else:
            if messagebox.askyesno("Continuar", "¿Deseas rentar otro vehículo?"):
                self.occupants_entry.delete(0, tk.END)
                self.days_entry.delete(0, tk.END)
            else:
                self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = RentalClientGUI(root)
    root.mainloop()