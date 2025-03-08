import pandas as pd
import openpyxl  # Necesario para leer archivos .xlsx

def verificar_credenciales(usuario, password, tipo):
    archivo = f"models/{tipo} USERS.xlsx"

    try:
        df = pd.read_excel(archivo, engine="openpyxl")  # Cargar Excel
        df.columns = df.columns.str.strip()  # Limpiar nombres de columnas

        # Verificar credenciales
        user_data = df[(df["USUARIO"] == usuario) & (df["CONTRASEÑA"] == password)]

        if not user_data.empty:
            return user_data.iloc[0]["ROL"]  # Retornar el rol del usuario
        return None  # Usuario no encontrado
    except FileNotFoundError:
        return "Archivo no encontrado"
    except Exception as e:
        return f"Error al leer el archivo: {e}"
