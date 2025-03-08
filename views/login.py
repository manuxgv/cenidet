from nicegui import ui
from controllers.auth_controller import autenticar

@ui.page('/')
def show_login():
    with ui.card().classes('w-96 mx-auto mt-20 p-5 shadow-lg'):
        ui.label("Iniciar Sesión").classes('text-2xl font-bold mb-4 text-center')
        
        auth_method = ui.toggle(["MCC", "DCC"], value="MCC").classes('mb-4')
        usuario = ui.input("Usuario").classes('w-full mb-2')
        password = ui.input("Contraseña", password=True).classes('w-full mb-4')
        
        with ui.row().classes('justify-between w-full'):
            ui.button("Ingresar", on_click=lambda: autenticar(usuario.value.strip(), password.value.strip(), auth_method.value)).classes('w-1/2 bg-blue-500 hover:bg-blue-700 text-white')
