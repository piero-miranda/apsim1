import streamlit as st
import tensorflow as tf
from PIL import Image
import cv2
import numpy as np
import os
from datetime import datetime
import json

# Rutas de archivos
DATABASE_PATH = "patients_data.json"
USERS_DB_PATH = "users_db.json"
SEGMENTATION_DIR = "segmentations"

# Crear el directorio de segmentaciones si no existe
if not os.path.exists(SEGMENTATION_DIR):
    os.makedirs(SEGMENTATION_DIR)

# URL del logo temporal de IEEE
logo_url = "https://cdn3.iconfinder.com/data/icons/science-indigo-vol-1/256/Artificial_Intelligence-512.png"

# Colores personalizados
primary_color = "#0057B7"  # Color azul del logo
background_color = "#f0f4f8"
button_color = "#3498db"
button_hover_color = "#2980b9"
text_color = "#333"

# CSS para estilos personalizados
st.markdown(
    f"""
    <style>
        /* Configuración del fondo y del texto */
        .app-background {{
            background-color: {background_color};
            padding: 20px;
            border-radius: 10px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 30px;
            background-color: {background_color};
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);

        }}
        .header-logo {{
            cursor: pointer;
        }}
        .header-logo img {{
            height: 50px;
        }}
        .header-buttons {{
            display: flex;
            gap: 15px;
        }}
        /* Botón principal */
        .primary-btn {{
            background-color: {button_color};
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .primary-btn:hover {{
            background-color: {button_hover_color};
        }}
        /* Botones secundarios */
        .secondary-btn {{
            background-color: white;
            color: {primary_color};
            font-weight: bold;
            border: 2px solid {primary_color};
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .secondary-btn:hover {{
            background-color: #ecf3fb;
        }}
        /* Título y subtítulo */
        .title {{
            color: {primary_color};
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
        }}
        .subtitle {{
            color: {text_color};
            font-size: 1.5em;
            font-weight: normal;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
        }}
        /* Texto en negrita para opciones */
        .option {{
            font-weight: bold;
            color: {primary_color};
            font-size: 1.2em;
            margin-bottom: 5px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Header con logo y botones de navegación
def header():
    st.markdown(
        f"""
        <style>
            .header-container {{
                display: flex;
                align-items: center;
                justify-content: flex-start;
                background-color: #f0f4f8;
                padding: 15px 30px;
                border-radius: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                width: 100%;
            }}
            .header-logo img {{
                height: 50px;
                cursor: pointer;
            }}
        </style>
        <div class="header-container">
            <div class="header-logo">
                <img src="{logo_url}" alt="IEEE Logo" onclick="window.location.href='/?page=home'" />
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Rutas de archivos
DATABASE_PATH = "patients_data.json"
USERS_DB_PATH = "users_db.json"
SEGMENTATION_DIR = "segmentations"

# Función para cambiar de página
def set_page(page_name):
    st.session_state.page = page_name

# Página de reinicio de base de datos
def reset_database_page():
    header()
    st.markdown(
        "<h1 style='color: #d9534f; margin-top: 20px;'>⚠️ Reiniciar Base de Datos</h1>",
        unsafe_allow_html=True
    )
    st.warning("Esta acción eliminará todos los datos de pacientes y segmentaciones almacenadas. Procede con precaución.")

    # Entrada para la contraseña de confirmación
    password = st.text_input("Introduce la contraseña para confirmar", type="password", key="reset_password")

    # Botón de confirmación
    if st.button("Confirmar"):
        if password == "0000":
            # Borrar datos de pacientes
            st.session_state.patients = []
            save_patients_data()
            
            # Borrar archivos de segmentación
            for file in os.listdir(SEGMENTATION_DIR):
                file_path = os.path.join(SEGMENTATION_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            st.success("Base de datos de pacientes y segmentaciones reiniciada correctamente.")
        else:
            st.error("Contraseña incorrecta. Intenta de nuevo.")

    # Botón "Atrás" para regresar al panel
    if st.button("Atrás"):
        set_page("panel")


# Función para cargar datos de pacientes desde el archivo JSON
def load_patients_data():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'r') as file:
            st.session_state.patients = json.load(file)
    else:
        st.session_state.patients = []  # Inicializar lista vacía si no existe el archivo

# Función para guardar datos de pacientes en el archivo JSON
def save_patients_data():
    with open(DATABASE_PATH, 'w') as file:
        json.dump(st.session_state.patients, file, indent=4)

# Función para cargar usuarios desde el archivo JSON
def load_users_data():
    if os.path.exists(USERS_DB_PATH):
        with open(USERS_DB_PATH, 'r') as file:
            st.session_state.users = json.load(file)
    else:
        st.session_state.users = {}  # Inicializar diccionario vacío si no existe el archivo

# Función para guardar usuarios en el archivo JSON
def save_users_data():
    with open(USERS_DB_PATH, 'w') as file:
        json.dump(st.session_state.users, file, indent=4)

# Inicializar session_state
if 'users' not in st.session_state:
    load_users_data()  # Cargar los datos de usuario desde el archivo al inicio

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

if 'patients' not in st.session_state:
    load_patients_data()  # Cargar los datos de pacientes desde el archivo al inicio


# Define las diferentes páginas de la aplicación
# Página principal con los botones de navegación
def home_page():
    header()
    st.markdown(
        """
        <h1 style='text-align: center; font-size: 2.5em; color: #333; margin-top: 30px;'>
            ¡Bienvenido a SegApp!
        </h1>

        <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
            <img src="https://www.aimtechnologies.co/wp-content/uploads/2023/09/Audience-Segmentation-Marketing-1.png" alt="Imagen de bienvenida" width="400">
        </div>
        
        <p style='text-align: center; font-size: 1.2em; color: #555; margin-top: 30px; margin-bottom: 50px;'>
            Inicia sesión o regístrate para acceder a nuestras herramientas avanzadas de análisis y seguimiento de pacientes.
        </p>
        """,
        unsafe_allow_html=True
    )

    # Configuración de columnas para centrar los botones
    col_left, col_center, col_right = st.columns([1, 0.5, 1])

    with col_center:
        # Botón de "¡Empezar a segmentar!" con estilo primario (azul)
        with st.container():
            st.markdown('<div class="primary-button">', unsafe_allow_html=True)
            if st.button("¡Empezar a segmentar!", key="login_button"):
                set_page("login")
            st.markdown("</div>", unsafe_allow_html=True)

        # Botón de "No tengo cuenta" con estilo secundario (gris)
        with st.container():
            st.markdown('<div class="secondary-button">', unsafe_allow_html=True)
            if st.button("No tengo cuenta", key="register_button"):
                set_page("register")
            st.markdown("</div>", unsafe_allow_html=True)

    # Mensaje informativo
    st.markdown(
        """
        <div style='text-align: justify; font-size: 1em; color: #555; margin-top: 40px;'>
            <p>
                <strong>SegApp</strong> es una aplicación diseñada para facilitar el análisis y seguimiento de heridas 
                en pacientes. A través de nuestra herramienta avanzada de segmentación, los profesionales de la salud 
                pueden analizar imágenes médicas de heridas de manera rápida y precisa. Esto permite mejorar el 
                seguimiento de la evolución de las heridas, detectar cambios relevantes y ajustar tratamientos de 
                acuerdo con las necesidades de cada paciente.
            </p>
            <p>
                Al usar SegApp, podrás acceder a funcionalidades como la carga de imágenes, la segmentación automática
                de áreas afectadas, y la posibilidad de guardar y comparar resultados a lo largo del tiempo. Esta 
                herramienta es ideal para hospitales, clínicas y centros de atención primaria que buscan incorporar 
                tecnología de punta en el cuidado de sus pacientes.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def login_page():
    header()
    st.markdown("<h1 style='font-size: 2em; color: #10579e; margin-top: 30px;'>Iniciar sesión</h1>", unsafe_allow_html=True)
    
    username = st.text_input("Nombre de usuario", key="login_username")
    password = st.text_input("Contraseña", type="password", key="login_password")

    if st.button("Iniciar sesión"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            set_page("panel")
            st.success("Inicio de sesión exitoso.")
        else:
            st.error("Nombre de usuario o contraseña incorrectos.")

    if st.button("Atrás"):
        set_page("home")

# Página de registro
def register_page():
    header()
    st.markdown("<h1 style='font-size: 2em; color: #10579e; margin-top: 30px;'>Regístrate aquí</h1>", unsafe_allow_html=True)

    new_username = st.text_input("Nuevo nombre de usuario", key="register_username")
    new_password = st.text_input("Nueva contraseña", type="password", key="register_password")
    confirm_password = st.text_input("Confirmar contraseña", type="password", key="confirm_password")

    if st.button("Registrarse"):
        if new_password == confirm_password:
            if new_username not in st.session_state.users:
                st.session_state.users[new_username] = new_password
                save_users_data()  # Guardar en archivo JSON
                st.success("Registro exitoso. Ahora puedes iniciar sesión.")
            else:
                st.error("El nombre de usuario ya existe. Por favor elige otro.")
        else:
            st.error("Las contraseñas no coinciden.")

    if st.button("Atrás"):
        set_page("home")



# Página de panel principal
def panel_page():
    header()
    st.markdown(
        f"""
        <h1 style="color: #333; margin-top: 20px;">
            ¡Bienvenido <span style="color: #3498db;">{st.session_state.get('username', 'Usuario')}</span>!
        </h1>
        <h3 style="color: #555;">Selecciona una opción:</h3>
        """,
        unsafe_allow_html=True
    )

    if st.button("Buscar paciente", key="buscar_paciente_button"):
        set_page('buscar_paciente')

    if st.button("Registrar paciente nuevo", key="registrar_paciente_button"):
        set_page('registrar_paciente')

    if st.button("Iniciar la segmentación", key="iniciar_segmentacion_button"):
        set_page('iniciar_segmentacion')

    if st.button("Reiniciar Base de Datos de Pacientes", key="reset_database_button"):
        set_page('reset_database')

    if st.button("Cerrar sesión", key="logout_button"):
        set_page('home')
        st.session_state.logged_in = False
        st.session_state.username = None  # Limpiar el nombre de usuario de la sesión
    st.markdown("</div>", unsafe_allow_html=True)

from io import BytesIO
from fpdf import FPDF

# Función para generar un PDF del paciente
def export_patient_to_pdf(patient):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Información del Paciente", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Nombre: {patient['name']}", ln=True)
    pdf.cell(200, 10, txt=f"Edad: {patient['age']}", ln=True)
    pdf.cell(200, 10, txt=f"Sexo: {patient['sex']}", ln=True)
    pdf.cell(200, 10, txt=f"DNI: {patient['dni']}", ln=True)

    # Agregar imágenes segmentadas al PDF
    if patient.get('segmentations'):
        for idx, seg_path in enumerate(patient['segmentations'], start=1):
            pdf.cell(200, 10, txt=f"Segmentación {idx}", ln=True)
            pdf.image(seg_path, w=100)  # Ajusta el tamaño de la imagen según sea necesario

    # Guardar el PDF en un objeto BytesIO
    pdf_output = BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)
    return pdf_output


# Función principal para buscar paciente y exportar datos
def buscar_paciente():
    header()

    st.markdown(
        """
        <h1 style='font-size: 2em; color: #10579e; margin-top: 30px;'>
            Buscar paciente existente
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    search_dni = st.text_input("Buscar paciente por DNI", key="search_dni")
    
    found = False  # Inicializar found antes de su uso

    if st.button("Buscar", key="buscar_button"):
        for patient in st.session_state.patients:
            if patient['dni'] == search_dni:
                st.write(f"**Nombre:** {patient['name']}")
                st.write(f"**Edad:** {patient['age']}")
                st.write(f"**Sexo:** {patient['sex']}")
                st.write(f"**DNI:** {search_dni}")
                
                st.subheader("Imágenes segmentadas")
                if patient.get('segmentations'):
                    for seg_path in patient['segmentations']:
                        st.image(seg_path, caption=f"Segmentación para {search_dni}", width=250)
                else:
                    st.info("No hay imágenes segmentadas para este paciente.")
                found = True
                break
        if not found:
            st.error("Paciente no encontrado. Verifica el DNI.")

    # Verificar si se encontró al paciente antes de mostrar los botones de exportación
    if found:
        # Botón para exportar la información a PDF
        pdf_data = export_patient_to_pdf(patient)
        st.download_button("Descargar PDF", data=pdf_data, file_name=f"{patient['name']}_info.pdf", mime="application/pdf")

    # Botón "Atrás" para volver a la página del panel
    if st.button("Atrás", key="back_button"):
        set_page('panel')



# Página para registrar un nuevo paciente
def registrar_paciente():
    header()
    st.markdown(
        """
        <h1 style='font-size: 2em; color: #10579e; margin-top: 30px;'>
            Registrar nuevo paciente
        </h1>
        """,
        unsafe_allow_html=True
    )

    p_name = st.text_input("Nombre completo", key="patient_name")
    p_age = st.number_input("Edad", min_value=1, max_value=100, key="patient_age")
    p_sex = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"], key="patient_sex")
    p_id = st.text_input("Número de DNI", key="patient_dni")
    
    if st.button("Guardar perfil", key="save_profile_button"):
        if any(patient['dni'] == p_id for patient in st.session_state.patients):
            st.error("El DNI ya existe. Usa otro DNI.")
        else:
            new_patient = {"name": p_name, "age": p_age, "sex": p_sex, "dni": p_id, "segmentations": []}
            st.session_state.patients.append(new_patient)
            st.success(f"Perfil de {p_name} guardado correctamente.")

    if st.button("Atrás", key="back_to_panel_button"):
        set_page('panel')
    st.markdown("</div>", unsafe_allow_html=True)

# Cargar el modelo SegNet
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model("SegNet_trained.h5")
    return model

# Procesar la imagen con el modelo de segmentación
def process_image_with_model(image, model):
    # Redimensionar la imagen a la entrada del modelo (por ejemplo, 224x224)
    image = image.resize((224, 224))
    image_array = np.array(image) / 255.0  # Normalizar
    image_array = np.expand_dims(image_array, axis=0)  # Agregar dimensión de batch

    # Realizar la predicción
    predicted_mask = model.predict(image_array)[0]  # Obtén la máscara sin la dimensión de batch

    # Asegurarse de que la máscara segmentada esté en formato uint8 y en escala de grises
    predicted_mask = (predicted_mask * 255).astype(np.uint8)
    
    # Si la máscara tiene un solo canal de color, asegurarse de que esté en el formato correcto
    if predicted_mask.ndim == 3 and predicted_mask.shape[-1] == 1:
        predicted_mask = np.squeeze(predicted_mask, axis=-1)
    
    return predicted_mask

def iniciar_segmentacion():
    header()  # Mostrar el encabezado en la página
    
    st.markdown(
        """
        <h1 style='font-size: 2em; color: #10579e; margin-top: 30px;'>
            Iniciar análisis de imágenes
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    image_file = st.file_uploader("Cargar imagen", type=["jpg", "jpeg", "png"], key="upload_image")

    if image_file is not None:
        # Guardar la imagen cargada en session_state
        st.session_state.image_file = image_file
        image = Image.open(image_file)
        
        # Mostrar la imagen cargada en la columna izquierda
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption='Imagen cargada correctamente', use_column_width=False, width=300)

        # Cargar el modelo una sola vez
        model = load_model()

        # Botón para procesar la imagen
        if st.button('Procesar imagen', key="process_image_button"):
            # Procesar la imagen con el modelo SegNet
            processed_image = process_image_with_model(image, model)
            st.session_state.processed_image = processed_image  # Guardar la imagen procesada en session_state
            
            # Guardar el archivo de la máscara segmentada
            filename = save_processed_image(processed_image)
            st.session_state.processed_image_filename = filename  # Guardar la ruta en session_state
            
            # Mostrar la imagen procesada (segmentada) en la columna derecha
            with col2:
                st.image(processed_image, caption='Máscara segmentada', use_column_width=False, width=300)

            # Calcular el porcentaje del área de la herida
            wound_area_percentage = calculate_non_black_pixel_percentage(processed_image)
            st.write(f"**Porcentaje de área de la herida:** {wound_area_percentage:.2f}%")

    # Botón para asignar segmentación solo si existe una imagen procesada
    if "processed_image" in st.session_state and st.session_state.processed_image is not None:
        if st.button("Asignar segmentación a paciente"):
            set_page("asignar_segmentacion")  # Cambiar a la página de asignación

    # Botón "Atrás" para volver a la página del panel
    if st.button("Atrás"):
        set_page("panel")


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

def export_patient_to_pdf(patient):
    # Crear un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        c = canvas.Canvas(tmp_file.name, pagesize=letter)
        
        # Información del paciente
        c.drawString(100, 750, f"Nombre: {patient['name']}")
        c.drawString(100, 730, f"Edad: {patient['age']}")
        c.drawString(100, 710, f"Sexo: {patient['sex']}")
        c.drawString(100, 690, f"DNI: {patient['dni']}")
        
        # Espacio para las segmentaciones
        y_position = 650
        for idx, seg_path in enumerate(patient.get("segmentations", [])):
            c.drawString(100, y_position, f"Segmentación {idx + 1}:")
            y_position -= 20
            
            # Insertar la imagen segmentada
            image = Image.open(seg_path)
            image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            image.save(image_path.name)
            c.drawImage(image_path.name, 100, y_position - 200, width=200, height=200)
            y_position -= 220
            
            # Limitar el número de imágenes por página
            if y_position < 100:
                c.showPage()  # Nueva página
                y_position = 750

        c.save()
        
        # Leer el archivo PDF generado
        tmp_file.seek(0)
        pdf_data = tmp_file.read()
    
    return pdf_data


# Función de asignación de segmentación con verificación de máscara segmentada en session_state
def asignar_segmentacion_page():
    header()
    st.subheader("Asignar segmentación a un paciente")
    
    # Verificar que existe una imagen procesada guardada en session_state
    if "processed_image_filename" not in st.session_state:
        st.warning("No hay una segmentación disponible para asignar. Vuelve a segmentar una imagen.")
        if st.button("Atrás"):
            set_page("iniciar_segmentacion")
        return

    # Mostrar la imagen segmentada actual para confirmación
    st.image(st.session_state.processed_image, caption='Máscara segmentada lista para asignar', use_column_width=False, width=300)

    # Solicitar el DNI del paciente
    dni_input = st.text_input("Ingrese el DNI del paciente", key="dni_for_segmentation")

    # Botón para asignar la segmentación
    if st.button("Asignar"):
        # Buscar el paciente en la lista y asignar la segmentación
        found = False
        for patient in st.session_state.patients:
            if patient['dni'] == dni_input:
                # Asignar la ruta de la imagen procesada al perfil del paciente
                if "segmentations" not in patient:
                    patient["segmentations"] = []
                patient["segmentations"].append(st.session_state.processed_image_filename)
                st.success("Segmentación asignada correctamente al paciente.")
                found = True
                save_patients_data()  # Guardar cambios en la base de datos
                break
        if not found:
            st.error("Paciente no encontrado. Verifica el DNI.")

    # Botón "Atrás" para volver a `iniciar_segmentacion`
    if st.button("Atrás"):
        set_page("iniciar_segmentacion")


# Calcula el porcentaje de píxeles no negros en la imagen procesada
def calculate_non_black_pixel_percentage(mask):
    non_black_pixels = np.sum(mask > 0)
    total_pixels = mask.size
    return (non_black_pixels / total_pixels) * 100

def process_image(image):
    try:
        image = np.array(image)
        image = cv2.resize(image, (224, 224))
        image = image / 255.0
        image = np.expand_dims(image, axis=0)
        mask = np.zeros_like(image[0], dtype=np.uint8)
        return (mask * 255).astype(np.uint8)
    except Exception as e:
        st.write(f"Error al procesar la imagen: {e}")
        return None

# Guarda la imagen segmentada y devuelve la ruta del archivo
def save_processed_image(mask):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SEGMENTATION_DIR}/mask_{timestamp}.png"
    Image.fromarray(mask).save(filename)
    return filename

def assign_segmentation_to_patient(dni, filename):
    found = False
    for patient in st.session_state.patients:
        if patient['dni'] == dni:
            if 'segmentations' not in patient:
                patient['segmentations'] = []
            patient['segmentations'].append(filename)
            st.success(f"Segmentación asignada correctamente al paciente con DNI: {dni}")
            found = True
            break
    if not found:
        st.error("Paciente no encontrado. Verifica el DNI.")
    
    # Guarda los datos actualizados
    save_patients_data()

# Navegación principal
def main():
    page = st.session_state.page
    if page == 'register':
        register_page()
    elif page == 'login':
        login_page()
    elif page == 'panel':
        panel_page()
    elif page == 'buscar_paciente':
        buscar_paciente()
    elif page == 'registrar_paciente':
        registrar_paciente()
    elif page == 'iniciar_segmentacion':
        iniciar_segmentacion()
    elif page == 'asignar_segmentacion':
        asignar_segmentacion_page()
    elif page == 'reset_database':  # Nueva página de reinicio de base de datos
        reset_database_page()
    else:
        home_page()

if __name__ == "__main__":
    main()