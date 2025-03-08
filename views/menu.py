from nicegui import ui
import pandas as pd
import os
from openpyxl import load_workbook
from controllers.controller import FormController
from models.excel_model import ExcelModel


# Instancia del modelo y el controlador
excel_model = ExcelModel('models/BD MCC.xlsx')
controller = FormController(excel_model)



# Función para obtener el último ID de la hoja "ALUMNOS"
def get_last_id():
    file_path = "models/BD MCC.xlsx"  # Asegurar la ruta correcta

    try:
        if not os.path.exists(file_path):
            return 0  # Si no existe el archivo, empezar desde ID 1

        df = pd.read_excel(file_path, sheet_name="ALUMNOS")

        if 'ID' in df.columns and not df.empty:
            return int(df['ID'].max())  # Convertir a entero
        return 0  # Si no hay registros, empezar desde 0

    except Exception as e:
        print(f"Error al obtener el último ID: {e}")
        return 0




# Variable global para controlar el paso del formulario
step = 1

@ui.page('/menu')
def show_menu():
    global menul
    with ui.row().classes('h-screen') as menul:
        with ui.column().classes('w-[150px] bg-gray-200 p-4 shadow-lg fixed h-full'):
            ui.label("Menú").classes('text-lg font-bold mb-4')
            ui.button("Ingresar alumno al modelo", on_click=show_data).classes('w-full mb-2')
            ui.button("Panel de control", on_click=show_levels).classes('w-full mb-2')
            ui.button("Consultar alumno", on_click=show_campus).classes('w-full mb-2')
            ui.button("Acerca de", on_click=show_matriculas).classes('w-full mb-2')
            ui.button("Cerrar sesión", on_click=lambda: ui.navigate.to('/')).classes('w-full bg-red-500 text-white')

        # Área donde aparece el formulario fuera del menú lateral
        global content_area
        with ui.column().classes('flex-grow p-5 ml-[200px]') as content_area:
            ui.label("Bienvenido al sistema").classes('text-2xl font-bold')
            content_area_label = ui.label("").classes('mt-6')  # Aquí se actualizará el contenido dinámico

def show_levels():
    ui.notify("Mostrando Niveles Escolares")

def show_campus():
    ui.notify("Mostrando Campus o Sedes")

def show_matriculas():
    ui.notify("Mostrando Matrículas")

def go_back():
    global step
    step -= 2   # Retroceder al paso anterior
    #ui.notify(step, type="negative")
    show_data()  # Mostrar el paso anterior

def show_data():
    global step
    content_area.clear()  # Limpiar el área principal

    if step == 1:
        show_first_step()
    elif step == 2:
        show_second_step()
    elif step == 3:
        show_third_step()
    elif step == 4:
        show_fourth_step()
    elif step == 5:
        show_fifth_step()
    elif step == 6:
        show_sixth_step()


# Función para guardar los datos y generar un nuevo ID automáticamente
# Inicializar el ID globalmente
current_id = get_last_id() + 1  # Obtener el siguiente ID disponible
 # Obtener el siguiente ID disponible

def save_step_data(step, data):
    global current_id
    data_with_id = [current_id] + data  # Agregar el ID al inicio de la fila
    controller.collect_data(step, data_with_id)  # Guardar datos en el controlador
    step += 2  # Avanzar al siguiente paso
    show_data()



def finish():
    global current_id
    controller.save_data()  # Guardar todos los datos en el archivo Excel
    ui.notify(f"Formulario completado y datos guardados con ID {current_id}.", type="positive")
    
    current_id += 1  # Incrementar el ID para el próximo alumno


    #ui.navigate("/")  # O navegar a donde sea necesario

def save_and_finish(meses, clase, factores_coincidentes, porcentajeS):
    save_step_data(6, [meses, clase, factores_coincidentes,porcentajeS])  # Guarda el último paso
    finish()  # Llama a finish() para guardar todo en Excel




form_data = {}  # Diccionario global para almacenar los valores del formulario
def show_first_step():
    global step
    step = 2  # Cambiar al siguiente paso

    with content_area:
        ui.label("Datos del alumno:").classes('text-2xl font-bold')
        nombreAlumno = ui.input('Nombre*', value=form_data.get('nombreAlumno')).classes('mb-2')
        edadAlumno = ui.number('Edad*', value=form_data.get('edadAlumno')).classes('mb-2')

        sexo_value = ui.label(form_data.get('sexo_value')).classes('mb-2')
        with ui.dropdown_button('Sexo*', auto_close=True).classes('mb-2').props('outline square'):
            ui.item('Hombre', on_click=lambda: sexo_value.set_text('0'))
            ui.item('Mujer', on_click=lambda: sexo_value.set_text('1'))

        region_value = ui.label(form_data.get('region_value')).classes('mb-2')
        with ui.dropdown_button('Entidad federativa', auto_close=True).classes('mb-2').props('outline square'):
            ui.item('Norte', on_click=lambda: region_value.set_text('N'))
            ui.item('Centro', on_click=lambda: region_value.set_text('C'))
            ui.item('Sur', on_click=lambda: region_value.set_text('S'))

        estado_civil_value = ui.label(form_data.get('estado_civil_value')).classes('mb-2')
        with ui.dropdown_button('Estado civil*', auto_close=True).classes('mb-2').props('outline square'):
            ui.item('Soltero(a)', on_click=lambda: estado_civil_value.set_text('10'))
            ui.item('Casado(a)', on_click=lambda: estado_civil_value.set_text('20'))
            ui.item('Unión libre', on_click=lambda: estado_civil_value.set_text('20'))

        # Botón para continuar con validación implícita
        with ui.row().classes('w-full mb-2'):
            ui.button("Continuar", on_click=lambda: (
                ui.notify("Por favor completa todos los campos obligatorios.", type="negative")
                if not (nombreAlumno.value and edadAlumno.value and sexo_value.text and estado_civil_value.text)
                else(
                    form_data.update({
                    'nombreAlumno': nombreAlumno.value,
                    'edadAlumno': edadAlumno.value,
                    'sexo_value': sexo_value.text,
                    'region_value': region_value.text,
                    'estado_civil_value': estado_civil_value.text
                }),
                    save_step_data(1, [
                    nombreAlumno.value, int(sexo_value.text), edadAlumno.value,
                    region_value.text, int(estado_civil_value.text)
                ]))
            )).classes('mt-4')

        # Subir archivo si es necesario
        #ui.upload(on_upload=lambda e: ui.notify(f'Uploaded {e.name}')).classes('ml-[250px] mb-1')


def show_second_step():
    global step
    step = 3  # Cambiar al siguiente paso

    with content_area:
        ui.label("Datos de carrera:").classes('text-2xl font-bold')

        with ui.row().classes('w-full mb-2'):
            tesis = ui.label(form_data.get('tesis')).classes('mb-2')  
            with ui.dropdown_button('Tesis', auto_close=True).classes('mb-2').props('outline square'):
                ui.item('Sí', on_click=lambda: tesis.set_text('SI'))
                ui.item('No', on_click=lambda: tesis.set_text('NO'))

            carrera = ui.label(form_data.get('carrera')).classes('mb-2')  
            with ui.dropdown_button('Carrera*', auto_close=True).classes('mb-2').props('outline square'):
                ui.item('1', on_click=lambda: carrera.set_text('1'))
                ui.item('2', on_click=lambda: carrera.set_text('2'))

            linea = ui.label(form_data.get('linea')).classes('mb-2')  
            with ui.dropdown_button('Línea', auto_close=True).classes('mb-2').props('outline square'):
                ui.item('IS', on_click=lambda: linea.set_text('6'))
                ui.item('SD', on_click=lambda: linea.set_text('2'))
                ui.item('SHI', on_click=lambda: linea.set_text('3'))
                ui.item('IA', on_click=lambda: linea.set_text('4'))
                ui.item('CI', on_click=lambda: linea.set_text('5'))

        generacion = ui.input('Generación', value=form_data.get('generacion')).classes('mb-2')
        semestre = ui.number('Semestre', value=form_data.get('semestre')).classes('mb-2')
        promedio = ui.number('Promedio*', value=form_data.get('promedio')).classes('mb-2')
        creditos = ui.number('Créditos', value=form_data.get('creditos')).classes('mb-2')
        terminacion = ui.number('Terminación', value=form_data.get('terminacion')).classes('mb-2')

        # Validación implícita en el botón
        with ui.row().classes('w-full mb-2'):
            ui.button("Continuar", on_click=lambda: (
                ui.notify("Por favor completa todos los campos obligatorios.", type="negative")
                if not (carrera.text and promedio.value)
                else(
                    form_data.update({
                    'tesis': tesis.text,
                    'carrera': carrera.text,
                    'linea': linea.text,
                    'generacion': generacion.value,
                    'semestre': semestre.value,
                    'promedio': promedio.value,
                    'creditos': creditos.value,
                    'terminacion': terminacion.value
                }),
                    save_step_data(2, [
                    tesis.text, int(carrera.text), linea.text,
                    generacion.value, semestre.value, promedio.value, creditos.value, terminacion.value
                ]))
            )).classes('mt-2')

            ui.button("Regresar", on_click=lambda: go_back()).classes('mt-2')

            #ui.label("Agregar excel").classes('ml-[320px]')
            #ui.upload(on_upload=lambda e: ui.notify(f'Uploaded {e.name}')).classes('ml-[450px] mb-1')


def show_third_step():
    global step
    step = 4  # Cambiar al siguiente paso

    with content_area:
        ui.label("Calificaciones:").classes('text-2xl font-bold')

        with ui.row().classes('w-full mb-2'):
            promedio1 = ui.number('Promedio semestre 1', value=form_data.get('p1')).classes('mb-2')
            creditos1 = ui.number('Créditos cursados', value=form_data.get('c1')).classes('mb-2')

        with ui.row().classes('w-full mb-2'):
            promedio2 = ui.number('Promedio semestre 2', value=form_data.get('p2')).classes('mb-2')
            creditos2 = ui.number('Créditos cursados', value=form_data.get('c2')).classes('mb-2')

        with ui.row().classes('w-full mb-2'):
            promedio3 = ui.number('Promedio semestre 3', value=form_data.get('p3')).classes('mb-2')
            creditos3 = ui.number('Créditos cursados', value=form_data.get('c3')).classes('mb-2')

        with ui.row().classes('w-full mb-2'):
            promedio4 = ui.number('Promedio semestre 4', value=form_data.get('p4')).classes('mb-2')
            creditos4 = ui.number('Créditos cursados', value=form_data.get('c4')).classes('mb-2')

        with ui.row().classes('w-full mb-2'):
            promedio5 = ui.number('Promedio semestre 5', value=form_data.get('p5')).classes('mb-2')
            creditos5 = ui.number('Créditos cursados', value=form_data.get('c5')).classes('mb-2')

        with ui.row().classes('w-full mb-2'):
            promedio6 = ui.number('Promedio semestre 6', value=form_data.get('p6')).classes('mb-2')
            creditos6 = ui.number('Créditos cursados', value=form_data.get('c6')).classes('mb-2')

        # Botones para continuar y regresar
        with ui.row().classes('w-full mb-2'):
            ui.button("Continuar", on_click=lambda:(
                    form_data.update({
                    'p1': promedio1.value,
                    'c1': creditos1.value,
                    'p2': promedio3.value,
                    'c2': creditos2.value,
                    'p3': promedio3.value,
                    'c3': creditos3.value,
                    'p4': promedio4.value,
                    'c4': creditos4.value,
                    'p5': promedio5.value,
                    'c5': creditos5.value,
                    'p6': promedio6.value,
                    'c6': creditos6.value
                }),
                      save_step_data(3, [
            promedio1.value, creditos1.value, promedio2.value, creditos2.value,
            promedio3.value, creditos3.value, promedio4.value, creditos4.value,
            promedio5.value, creditos5.value, promedio6.value, creditos6.value
        ]))).classes('mt-2')
            ui.button("Regresar", on_click=lambda: go_back()).classes('mt-2')

def show_fourth_step():
    global step
    step = 5  # Cambiar al siguiente paso

    with content_area:
        ui.label("Materias:").classes('text-2xl font-bold')

        with ui.row().classes('w-full mb-2'):
            b1 = ui.number('B1', value=form_data.get('b1', None)).classes('mb-2')
            b2 = ui.number('B2', value=form_data.get('b2', None)).classes('mb-2')  
            b3 = ui.number('B3', value=form_data.get('b3', None)).classes('mb-2')
            b4 = ui.number('B4', value=form_data.get('b4', None)).classes('mb-2')

        with ui.row().classes('w-full mb-2'):
            o1 = ui.number('O1', value=form_data.get('o1', None)).classes('mb-2')
            o2 = ui.number('O2', value=form_data.get('o2', None)).classes('mb-2')
            o3 = ui.number('O3', value=form_data.get('o3', None)).classes('mb-2')
            o4 = ui.number('O4', value=form_data.get('o4', None)).classes('mb-2')
            o5 = ui.number('O5', value=form_data.get('o5', None)).classes('mb-2')

        with ui.row().classes('w-full mb-2'):
            s1 = ui.number('S1', value=form_data.get('s1', None)).classes('mb-2')
            s2 = ui.number('S2', value=form_data.get('s2', None)).classes('mb-2')
            s3 = ui.number('S3', value=form_data.get('s3', None)).classes('mb-2')

        # Botones para continuar y regresar
        with ui.row().classes('w-full mb-2'):
            ui.button("Continuar", on_click=lambda: (
                form_data.update({
                    'b1': b1.value, 'b2': b2.value, 'b3': b3.value, 'b4': b4.value,
                    'o1': o1.value, 'o2': o2.value, 'o3': o3.value, 'o4': o4.value, 'o5': o5.value,
                    's1': s1.value, 's2': s2.value, 's3': s3.value
                }),
                save_step_data(4, [
                    b1.value, b2.value, b3.value, b4.value,
                    o1.value, o2.value, o3.value, o4.value, o5.value,
                    s1.value, s2.value, s3.value
                ])
            )).classes('mt-2')

            ui.button("Regresar", on_click=lambda: go_back()).classes('mt-2')


def show_fifth_step():
    global step
    step = 6  # Cambiar al siguiente paso

    with content_area:
        ui.label("16FP:").classes('text-2xl font-bold')

        with ui.row().classes('w-full mb-2 grid grid-cols-4 gap-4'):  
            fp1 = ui.number('FP1*', value=form_data.get('fp1', None)).classes('mb-2')
            factor1 = ui.number('Factor 1*', value=form_data.get('factor1', None)).classes('mb-2')

            fp2 = ui.number('FP2*', value=form_data.get('fp2', None)).classes('mb-2')
            factor2 = ui.number('Factor 2*', value=form_data.get('factor2', None)).classes('mb-2')

            fp3 = ui.number('FP3*', value=form_data.get('fp3', None)).classes('mb-2')
            factor3 = ui.number('Factor 3*', value=form_data.get('factor3', None)).classes('mb-2')

            fp4 = ui.number('FP4*', value=form_data.get('fp4', None)).classes('mb-2')
            factor4 = ui.number('Factor 4*', value=form_data.get('factor4', None)).classes('mb-2')

            fp5 = ui.number('FP5*', value=form_data.get('fp5', None)).classes('mb-2')
            factor5 = ui.number('Factor 5*', value=form_data.get('factor5', None)).classes('mb-2')

            fp6 = ui.number('FP6*', value=form_data.get('fp6', None)).classes('mb-2')
            factor6 = ui.number('Factor 6*', value=form_data.get('factor6', None)).classes('mb-2')

            fp7 = ui.number('FP7*', value=form_data.get('fp7', None)).classes('mb-2')
            factor7 = ui.number('Factor 7*', value=form_data.get('factor7', None)).classes('mb-2')

            fp8 = ui.number('FP8*', value=form_data.get('fp8', None)).classes('mb-2')
            factor8 = ui.number('Factor 8*', value=form_data.get('factor8', None)).classes('mb-2')

            fp9 = ui.number('FP9*', value=form_data.get('fp9', None)).classes('mb-2')
            factor9 = ui.number('Factor 9*', value=form_data.get('factor9', None)).classes('mb-2')

            fp10 = ui.number('FP10*', value=form_data.get('fp10', None)).classes('mb-2')
            factor10 = ui.number('Factor 10*', value=form_data.get('factor10', None)).classes('mb-2')

            fp11 = ui.number('FP11*', value=form_data.get('fp11', None)).classes('mb-2')
            factor11 = ui.number('Factor 11*', value=form_data.get('factor11', None)).classes('mb-2')

            fp12 = ui.number('FP12*', value=form_data.get('fp12', None)).classes('mb-2')
            factor12 = ui.number('Factor 12*', value=form_data.get('factor12', None)).classes('mb-2')

            fp13 = ui.number('FP13*', value=form_data.get('fp13', None)).classes('mb-2')
            factor13 = ui.number('Factor 13*', value=form_data.get('factor13', None)).classes('mb-2')

            fp14 = ui.number('FP14*', value=form_data.get('fp14', None)).classes('mb-2')
            factor14 = ui.number('Factor 14*', value=form_data.get('factor14', None)).classes('mb-2')

            fp15 = ui.number('FP15*', value=form_data.get('fp15', None)).classes('mb-2')
            factor15 = ui.number('Factor 15*', value=form_data.get('factor15', None)).classes('mb-2')

            fp16 = ui.number('FP16*', value=form_data.get('fp16', None)).classes('mb-2')
            factor16 = ui.number('Factor 16*', value=form_data.get('factor16', None)).classes('mb-2')

        # Botones para continuar y regresar con validación de campos obligatorios
        def is_not_empty(value):
            return value is not None and value != ""

        with ui.row().classes('w-full mb-2'):
            ui.button("Continuar", on_click=lambda: (
                ui.notify("Por favor completa todos los campos obligatorios.", type="negative")
                if not all(is_not_empty(v) for v in [
                    fp1.value, factor1.value, fp2.value, factor2.value, fp3.value, factor3.value,
                    fp4.value, factor4.value, fp5.value, factor5.value, fp6.value, factor6.value,
                    fp7.value, factor7.value, fp8.value, factor8.value, fp9.value, factor9.value,
                    fp10.value, factor10.value, fp11.value, factor11.value, fp12.value, factor12.value,
                    fp13.value, factor13.value, fp14.value, factor14.value, fp15.value, factor15.value,
                    fp16.value, factor16.value
                ])
                else (
                    form_data.update({
                        'fp1': fp1.value, 'factor1': factor1.value, 'fp2': fp2.value, 'factor2': factor2.value,
                        'fp3': fp3.value, 'factor3': factor3.value, 'fp4': fp4.value, 'factor4': factor4.value,
                        'fp5': fp5.value, 'factor5': factor5.value, 'fp6': fp6.value, 'factor6': factor6.value,
                        'fp7': fp7.value, 'factor7': factor7.value, 'fp8': fp8.value, 'factor8': factor8.value,
                        'fp9': fp9.value, 'factor9': factor9.value, 'fp10': fp10.value, 'factor10': factor10.value,
                        'fp11': fp11.value, 'factor11': factor11.value, 'fp12': fp12.value, 'factor12': factor12.value,
                        'fp13': fp13.value, 'factor13': factor13.value, 'fp14': fp14.value, 'factor14': factor14.value,
                        'fp15': fp15.value, 'factor15': factor15.value, 'fp16': fp16.value, 'factor16': factor16.value
                    }),
                    save_step_data(5, [
                        fp1.value, factor1.value, fp2.value, factor2.value, fp3.value, factor3.value,
                        fp4.value, factor4.value, fp5.value, factor5.value, fp6.value, factor6.value,
                        fp7.value, factor7.value, fp8.value, factor8.value, fp9.value, factor9.value,
                        fp10.value, factor10.value, fp11.value, factor11.value, fp12.value, factor12.value,
                        fp13.value, factor13.value, fp14.value, factor14.value, fp15.value, factor15.value,
                        fp16.value, factor16.value
                    ])
                )
            )).classes('mt-2')


            ui.button("Regresar", on_click=lambda: go_back()).classes('mt-2')


def show_sixth_step():
    global step
    step = 7
    content_area.clear()

    with content_area:
        ui.label("Resultados 16FP:").classes('text-2xl font-bold')

        meses = ui.number('Meses', value=form_data.get('meses', None)).classes('mb-2')
        clase = ui.input('Clase', value=form_data.get('clase', '')).classes('mb-2')
        factores_coincidentes = ui.number('Factores coincidentes*', value=form_data.get('factores_coincidentes', None)).classes('mb-2')
        porcentajeS = ui.number('Porcentaje de similitud*', value=form_data.get('porcentajeS', None)).classes('mb-2')

        # Botón "Finalizar" con validación implícita y persistencia de datos
        ui.button("Finalizar", on_click=lambda: (
            ui.notify("Por favor completa todos los campos obligatorios.", type="negative")
            if not (factores_coincidentes.value and porcentajeS.value)
            else (
                form_data.update({
                    'meses': meses.value,
                    'clase': clase.value,
                    'factores_coincidentes': factores_coincidentes.value,
                    'porcentajeS': porcentajeS.value
                }),
                save_and_finish(meses.value, clase.value, factores_coincidentes.value, porcentajeS.value)
            )
        )).classes('mt-2')

        ui.button("Regresar", on_click=lambda:( 
                    form_data.update({
                    'meses': meses.value,
                    'clase': clase.value,
                    'factores_coincidentes': factores_coincidentes.value,
                    'porcentajeS': porcentajeS.value
                })
            ,go_back())).classes('mt-2')


# Llamar a la función inicial para mostrar el menú
ui.run()
