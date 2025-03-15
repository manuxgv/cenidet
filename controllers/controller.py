import numpy as np
import pandas as pd
import tensorflow as tf
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder
from models.excel_model import ExcelModel

pronostico = 0

class FormController:
    def __init__(self, model, force_train=False):
        self.model = model
        self.step_data = {}
        self.model_path = "models/modeloSMOTE.h5"  # Ruta del modelo preentrenado
        self.dataset_path = "models/correcto.csv"  # Dataset de referencia para SMOTE
        self.force_train = force_train  # Flag para forzar el entrenamiento

        try:
            self.loaded_model = tf.keras.models.load_model(
                self.model_path, custom_objects={'mse': tf.keras.losses.MeanSquaredError()}
            )
            print("✅ Modelo cargado correctamente.")
            if self.force_train:
                print("🔄 Forzando el entrenamiento del modelo...")
                self.loaded_model = None  # Si forzamos el entrenamiento, eliminamos el modelo cargado
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {e}")
            self.loaded_model = None  

    def collect_data(self, step, data):
        """ Guarda los datos de cada paso en el diccionario """
        self.step_data[step] = data

    def save_data(self):
        """ Guarda los datos en las hojas respectivas del Excel """
        try:
            self.model.save_data('ALUMNOS', self.step_data.get(1, []))
            self.model.save_data('CARRERA', self.step_data.get(2, []))
            self.model.save_data('CALIFICACIONES', self.step_data.get(3, []))
            self.model.save_data('MATERIAS', self.step_data.get(4, []))
            self.model.save_data('16FP', self.step_data.get(5, []))
            #self.model.save_data('RESULTADOS', self.step_data.get(6, []))

            # Generar la predicción
            self.generate_prediction()
        except Exception as e:
            print(f"❌ Error al guardar los datos: {e}")

    def generate_prediction(self):
        global pronostico
        """Genera la predicción basada en los datos ingresados"""
        if self.loaded_model is None:
            print("❌ No se puede generar la predicción porque el modelo no se cargó correctamente.")
            print("🔄 Iniciando el proceso de entrenamiento...")

            # Cargar dataset de referencia para aplicar SMOTE
            df_train = pd.read_csv(self.dataset_path)
            df_train = self.preprocess_dataset(df_train)

            # Separar características y etiquetas
            X_train = df_train.drop(columns=['PRONOSTICO'], errors='ignore')
            y_train = df_train['PRONOSTICO']

            # Aplicar SMOTE
            smote = SMOTE(sampling_strategy='auto', k_neighbors=4, random_state=42)  # Ajuste de vecinos
            X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

            # Entrenar el modelo desde cero
            self.loaded_model = self.train_model(X_train_resampled, y_train_resampled, epochs=100)

            # Usamos X_train para obtener el número de características para validación más tarde
            num_features = X_train_resampled.shape[1]
        else:
            # Si el modelo ya está cargado, solo necesitamos el número de características
            num_features = self.loaded_model.input_shape[1]  # Obtenemos las características del modelo

        try:
            # Preprocesar datos de entrada para predicción
            input_data = self.prepare_input_data()
            print("📊 Datos de entrada al modelo:", input_data)

            # Verificar que el número de características de los datos de entrada coincida con el esperado
            if len(input_data) != num_features:  
                print(f"❌ Error: Se esperaban {num_features} columnas, pero se recibieron {len(input_data)}.")
                return

            # Convertir a array NumPy
            input_array = np.array(input_data, dtype=np.float32).reshape(1, -1)

            # Hacer la predicción
            prediction = self.loaded_model.predict(input_array)
            predicted_class = int(np.round(prediction[0][0]))  # Predicción binaria redondeada

            # Guardar el pronóstico en la hoja "RESULTADOS"
            self.step_data[6].append(predicted_class)
            self.model.save_data('RESULTADOS', self.step_data[6])

            print(f"✅ Pronóstico generado: {predicted_class}")
            pronostico = predicted_class

        except Exception as e:
            print(f"❌ Error en la predicción: {e}")
        #return predicted_class

    def preprocess_dataset(self, df):
        """ Limpia el dataset eliminando texto y convirtiendo todo a numérico """
        df['NOMBRE'] = 0.0  # Convertir nombres a 0.0
        df = df.drop(columns=['ID', 'Unnamed: 0'], errors='ignore')

        # Convertir columnas a numéricas y manejar valores faltantes
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Codificar las columnas categóricas
        le = LabelEncoder()
        for column in df.columns:
            if df[column].dtype == 'object':
                df[column] = le.fit_transform(df[column])

        return df

    def prepare_input_data(self):
        """ Organiza los datos en el formato correcto antes de la predicción """
        input_data = []

        if 1 in self.step_data:  # Datos personales
            alumno_data = self.step_data[1]
            input_data.append(0.0)  # Convertir nombre a 0.0
            input_data.append(int(alumno_data[2]))  # SEXO
            input_data.append(int(alumno_data[3]))  # EDAD
            input_data.append(int(alumno_data[5]))  # ESTADO CIVIL

        if 2 in self.step_data:  # Datos de carrera
            carrera_data = self.step_data[2]
            input_data.append(int(carrera_data[2]))  # CARRERA
            input_data.append(float(carrera_data[6]))  # PROMEDIO

        if 5 in self.step_data:  # Factores 16FP (Omitiendo el ID)
            fp_data = self.step_data[5][1:]
            input_data.extend(map(int, fp_data))

        if 6 in self.step_data:  # Factores coincidentes y porcentaje de similitud
            resultados_data = self.step_data[6]
            input_data.append(int(resultados_data[3]))  # Factores Coincidentes
            input_data.append(float(resultados_data[4]))  # Porcentaje de Similitud

        return input_data

    def train_model(self, X_train, y_train, epochs=100):
        """ Entrena el modelo desde cero usando los datos balanceados por SMOTE """
        # Aquí creamos un modelo secuencial simple, puedes ajustarlo según sea necesario
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        # Compilar el modelo
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        # Entrenar el modelo
        print("🔄 Entrenando el modelo...")
        model.fit(X_train, y_train, epochs=epochs, batch_size=32, validation_split=0.2)

        # Guardar el modelo entrenado
        model.save(self.model_path)
        print("✅ Modelo entrenado y guardado correctamente.")
        return model
    
    def get_pronostico(self):
        return pronostico
    

    #MARTES
    def get_all_sheets(self):
        """Obtiene los nombres de todas las hojas del archivo Excel."""
        return self.model.get_all_sheets()

    def get_sheet_data(self, sheet_name):
        """Obtiene los datos de una hoja específica del Excel en formato de lista de diccionarios."""
        return self.model.get_sheet_data(sheet_name)
    
    def get_sheet_dataDCC(self, sheet_name):
        """Obtiene los datos de una hoja específica del Excel en formato de lista de diccionarios."""
        return self.model.get_sheetDCC(sheet_name)

    '''def save_data(self, sheet_name, data):
        """Guarda datos en una hoja específica del Excel."""
        self.model.save_data(sheet_name, data)'''



