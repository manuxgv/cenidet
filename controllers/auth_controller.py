from nicegui import ui
from models.auth_model import verificar_credenciales

def autenticar(usuario, password, tipo):
    resultado = verificar_credenciales(usuario, password, tipo)

    if resultado is None:
        ui.notify("❌ Usuario o contraseña incorrectos", type="negative")
    elif resultado == "Archivo no encontrado":
        ui.notify("⚠️ Archivo de usuarios no encontrado.", type="negative")
    elif "Error al leer el archivo" in resultado:
        ui.notify(f"⚠️ {resultado}", type="negative")
    else:
        ui.notify(f"✅ Autenticación exitosa como {resultado}", type="positive")
        ui.timer(1, lambda: ui.navigate.to('/menu'))  # Redirigir al menú
