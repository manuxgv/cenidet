from nicegui import app, ui, native
from views import login, menu  # Importa las vistas

# Configuración del modo nativo
app.native.window_args['resizable'] = False  # Evita que el usuario cambie el tamaño de la ventana
app.native.start_args['debug'] = True  # Activa el modo depuración
app.native.settings['ALLOW_DOWNLOADS'] = True  # Permite descargas desde la app

# Ejecutar la app en modo nativo con el tamaño de ventana deseado
ui.run(
    native=True,  # Modo nativo (app de escritorio)
    window_size=(1500, 800),  # Tamaño inicial de la ventana
    fullscreen=False,  # No iniciar en pantalla completa
    reload=False, port=native.find_open_port()
)
