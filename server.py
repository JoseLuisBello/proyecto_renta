import threading
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class RentalService:
    def __init__(self):
        self.vehicles = {
            "auto 4 puertas": {"capacity": 4, "cost": 600, "units": 5, "days_available": "lunes a domingo"},
            "camioneta 4 puertas": {"capacity": 5, "cost": 750, "units": 5, "days_available": "martes a domingo"},
            "camioneta 3 puertas": {"capacity": 10, "cost": 1200, "units": 3, "days_available": "lunes a domingo"},
        }
        self.lock = threading.Lock()

    def get_vehicles(self):
        # Devuelve info pública sin units para el cliente
        info = {}
        for key, val in self.vehicles.items():
            info[key] = {
                "capacity": val["capacity"],
                "cost": val["cost"],
                "days_available": val["days_available"]
            }
        return info

    def rent(self, vehicle_type, occupants, days):
        if vehicle_type not in self.vehicles:
            return "Tipo de vehículo inválido"
        
        veh = self.vehicles[vehicle_type]
        if occupants > veh["capacity"]:
            return "Excede el cupo máximo"
        
        if days <= 0:
            return "Número de días inválido"
        
        # Aquí podrías agregar validación de fechas si se proveen, pero no se incluyen en la solicitud
        with self.lock:
            if veh["units"] > 0:
                veh["units"] -= 1
                amount = days * veh["cost"]
                return f"Confirmación de renta para {vehicle_type}, {occupants} ocupantes, {days} días. Monto a pagar: ${amount}"
            else:
                return "No hay disponibilidad, por favor espere la atención"

# Iniciar el servidor
server = ThreadedXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()
server.register_instance(RentalService())
print("Servidor RPC iniciado en http://localhost:8000")
server.serve_forever()