import pandas as pd
import tensorflow as tf
from tensorflow import keras
import numpy as np
from imblearn.over_sampling import SMOTE
import os

# Registrar la función personalizada correctamente
@keras.utils.register_keras_serializable(package='Custom', name='mse')
def mse(y_true, y_pred):
    return tf.keras.losses.mean_squared_error(y_true, y_pred)

class ModeloPredictivo:
    def preprocess_data(self, X):
        # Eliminar la columna 'ID' y 'Unnamed: 0' si existen en el DataFrame
        X = X.drop(columns=['ID', 'Unnamed: 0'], errors='ignore')

        # Convertir columnas a numéricas y manejar valores faltantes
        X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Codificar variables categóricas si las hay
        from sklearn.preprocessing import LabelEncoder
        for column in X.columns:
            if X[column].dtype == 'object':
                le = LabelEncoder()
                X[column] = le.fit_transform(X[column])

        return X

    def train_and_predict(self):
        excel_file = 'models/datos.xlsx'
        model_file = 'models/modeloSMOTE.h5'
        csv_file = 'models/correcto.csv'

        # Verificar archivos
        if not os.path.exists(csv_file):
            raise FileNotFoundError("El archivo correcto.csv no existe.")

        if not os.path.exists(excel_file):
            raise FileNotFoundError("El archivo datos.xlsx no existe.")

        # Cargar datos de entrenamiento
        datos_entrenamiento = pd.read_csv(csv_file)
        X_train = datos_entrenamiento.drop(columns=['PRONOSTICO', 'ID', 'Unnamed: 0'], errors='ignore')
        y_train = datos_entrenamiento['PRONOSTICO']

        X_train = self.preprocess_data(X_train)

        # Aplicar SMOTE
        min_samples_per_class = y_train.value_counts().min()
        smote = SMOTE(sampling_strategy='auto', k_neighbors=min(1, min_samples_per_class - 1), random_state=42)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

        # Cargar el modelo preentrenado con custom_objects actualizado
        if not os.path.exists(model_file):
            raise FileNotFoundError("El modelo preentrenado no existe.")

        model = tf.keras.models.load_model(
            model_file, 
            custom_objects={'mse': tf.keras.losses.MeanSquaredError()}
        )

        # Cargar Excel
        with pd.ExcelFile(excel_file) as xls:
            datos_excel = pd.read_excel(xls, sheet_name=None)

        if 'Alumnos' not in datos_excel:
            raise ValueError("La hoja 'Alumnos' no existe en el archivo Excel.")

        df_alumnos = datos_excel['Alumnos']

        # Filtrar filas a predecir según rol
        filas_a_predecir = df_alumnos[df_alumnos['PRONOSTICO'].isna()]

        if filas_a_predecir.empty:
            print("No hay filas pendientes de predicción.")
            return

        # Preparar datos para predicción
        X_pred = filas_a_predecir.drop(columns=['PRONOSTICO', 'ID'], errors='ignore')
        X_pred = self.preprocess_data(X_pred)

        # Hacer predicciones usando el modelo cargado
        predicciones = model.predict(X_pred)

        # Redondear predicciones
        predicciones_redondeadas = np.round(predicciones.flatten())

        # Asignar predicciones al DataFrame
        df_alumnos.loc[df_alumnos['ID'].isin(filas_a_predecir['ID']), 'PRONOSTICO'] = predicciones_redondeadas

        # Guardar el archivo actualizado
        datos_excel['Alumnos'] = df_alumnos
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for sheet_name, df in datos_excel.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print("Predicciones realizadas correctamente y guardadas en el archivo actualizado.")

# Ejecutar la predicción
modelo = ModeloPredictivo()
modelo.train_and_predict()
