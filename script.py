from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

# Cargar el dataset
df = pd.read_csv("DatasetProject2.csv")

df["NOMBRE"] = 0

# Eliminar columnas irrelevantes
columns_to_drop = ["Unnamed: 0","CARRERA"]  # "CARRERA" solo tiene un valor
df_cleaned = df.drop(columns=columns_to_drop)

# Normalizar las características numéricas
scaler = StandardScaler()
features = df_cleaned.drop(columns=["PRONOSTICO"])
X_scaled = scaler.fit_transform(features)

# Variable objetivo
y = df_cleaned["PRONOSTICO"].values

# Dividir en conjunto de entrenamiento y prueba (80% - 20%)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, stratify=y, random_state=42)

# Verificar la distribución después del preprocesamiento
print(np.unique(y_train, return_counts=True))
print(np.unique(y_test, return_counts=True))
