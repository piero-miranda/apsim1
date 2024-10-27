import streamlit as st
import tensorflow as tf
from PIL import Image
import cv2
import numpy as np
import json
import os
from datetime import datetime

# Estilos personalizados en CSS para una apariencia profesional médica
# Estilos personalizados en CSS para una apariencia profesional médica
st.markdown(
    """
    <style>
    /* Fondo personalizado para toda la app */
    .main {
        background-color: #f7f9fc;
    }
    /* Estilos de títulos y subtítulos */
    h1 {
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
    }
    h2, h3 {
        color: #34495e;
        font-weight: bold;
    }
    h2 {
        font-size: 1.75rem;
    }
    h3 {
        font-size: 1.5rem;
        color: #2ecc71;
    }
    /* Estilo personalizado para advertencias */
    .stAlert {
        background-color: #e74c3c10;
        color: #c0392b;
        font-weight: bold;
        border-left: 5px solid #e74c3c;
        padding: 1rem;
        border-radius: 8px;
    }
    /* Estilo de los botones */
    .stButton > button {
        color: #ffffff;
        background-color: #2ecc71;
        border: none;
        padding: 0.5rem 1.5rem;
        font-size: 1rem;
        font-weight: bold;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3498db;
        color: #ffffff;
    }
    /* Caja de texto */
    input {
        font-size: 1.1rem;
        padding: 0.5rem;
        border: 1px solid #dfe6e9;
        border-radius: 5px;
    }
    /* Caja de selección */
    select {
        font-size: 1rem;
        padding: 0.5rem;
        border: 1px solid #dfe6e9;
        border-radius: 5px;
    }
    /* Estilos para los datos del paciente */
    .patient-info {
        font-size: 1.2rem;
        color: #2c3e50;
        line-height: 1.6;
    }
    .patient-info strong {
        font-weight: bold;
    }
    /* Estilo para el mensaje de bienvenida */
    .welcome-message {
        font-size: 2rem; /* Tamaño de fuente más grande */
        font-weight: bold;
        color: #2c3e50;
    }
    .username-green {
        color: #2ecc71;
    }
    </style>
    """, unsafe_allow_html=True
)

# Rutas de archivos
DATABASE_PATH = "patients_data.json"
USERS_DB_PATH = "users_db.json"
SEGMENTATION_DIR = "segmentations"

# Crear el directorio de segmentaciones si no existe
if not os.path.exists(SEGMENTATION_DIR):
    os.makedirs(SEGMENTATION_DIR)

# Cargar el modelo de TensorFlow
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model('deep_learn.h5')
    return model

model = load_model()

# Función para cargar la lista de pacientes desde JSON
def load_patients_data():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as f:
            st.session_state.patients = json.load(f)
    else:
        st.session_state.patients = []

# Función para guardar la lista de pacientes en JSON
def save_patients_data():
    with open(DATABASE_PATH, "w") as f:
        json.dump(st.session_state.patients, f)

# Función para cargar usuarios desde JSON
def load_users():
    if os.path.exists(USERS_DB_PATH):
        with open(USERS_DB_PATH, 'r') as f:
            st.session_state.users = json.load(f)
    else:
        st.session_state.users = {}

# Función para guardar usuarios en JSON
def save_users():
    with open(USERS_DB_PATH, 'w') as f:
        json.dump(st.session_state.users, f)

# Función para reiniciar la base de datos de pacientes y eliminar segmentaciones
def reset_patients_database():
    st.markdown(
        "<div class='stAlert'>"
        "⚠️ <strong>Advertencia:</strong> Esta acción eliminará de forma permanente toda la base de datos de pacientes y todas las segmentaciones almacenadas."
        "</div>", unsafe_allow_html=True
    )
    st.markdown(
        """
        <ul style="font-size: 1.1rem;">
            <li>Todos los registros de pacientes serán eliminados.</li>
            <li>Todas las imágenes de segmentación almacenadas en el sistema serán eliminadas permanentemente.</li>
        </ul>
        <p style="font-size: 1.1rem; color: #e74c3c;"><strong>Por favor, asegúrese de que esta acción es realmente necesaria, ya que no se podrá deshacer.</strong></p>
        """, unsafe_allow_html=True
    )
    password = st.text_input("Ingrese la contraseña para confirmar:", type="password")
    
    if st.button("Confirmar eliminación"):
        if password == "0000":
            st.session_state.patients = []
            save_patients_data()
            for filename in os.listdir(SEGMENTATION_DIR):
                file_path = os.path.join(SEGMENTATION_DIR, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    st.error(f"No se pudo eliminar {file_path}: {e}")
            st.success("La base de datos de pacientes y las segmentaciones han sido reiniciadas.")
        else:
            st.error("Contraseña incorrecta")

# Función para cambiar de página
def set_page(page_name):
    st.session_state.page = page_name

# Inicializar session_state
if 'patients' not in st.session_state:
    load_patients_data()

if 'users' not in st.session_state:
    load_users()

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Inicializar processed_image para mantenerla en session_state
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

def main():
    if st.session_state.page == 'home':
        home_page()
    elif st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'register':
        register_page()
    elif st.session_state.page == 'panel':
        panel_page()
    elif st.session_state.page == 'buscar_paciente':
        buscar_paciente()
    elif st.session_state.page == 'registrar_paciente':
        registrar_paciente()
    elif st.session_state.page == 'iniciar_segmentacion':
        iniciar_segmentacion()
    elif st.session_state.page == 'asignar_segmentacion':
        asignar_segmentacion_page()
    elif st.session_state.page == 'reset_database':
        reset_database_page()

def home_page():
    st.markdown("<h1>SEGAp</h1>", unsafe_allow_html=True)
    if st.button("Iniciar Sesión", key="login"):
        set_page('login')
    if st.button("Registrarse", key="register"):
        set_page('register')

def login_page():
    st.subheader("Iniciar sesión")
    username = st.text_input("Nombre de usuario")
    password = st.text_input("Contraseña", type='password')
    if st.button("Login", key="login_button"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            set_page('panel')
        else:
            st.error("Nombre de usuario o contraseña incorrectos")
    if st.button("Atrás", key="back_login"):
        set_page('home')

def panel_page():
    st.markdown(
        f"""
        <div class="welcome-message">
            ¡Bienvenido <span class="username-green">{st.session_state.username}</span>!
        </div>
        """, unsafe_allow_html=True
    )
    st.subheader("Selecciona una opción:")

    if st.button("Buscar paciente", key="buscar_button"):
        set_page('buscar_paciente')

    if st.button("Registrar paciente nuevo", key="registrar_paciente"):
        set_page('registrar_paciente')

    if st.button("Iniciar la segmentación", key="segmentacion_button"):
        set_page('iniciar_segmentacion')

    if st.button("Reiniciar Base de Datos de Pacientes", key="reset_database"):
        set_page('reset_database')

    if st.button("Cerrar sesión", key="logout_button"):
        set_page('home')

def buscar_paciente():
    st.subheader("Buscar paciente existente")
    search_dni = st.text_input("Buscar paciente por DNI")
    
    if st.button("Buscar", key="buscar_paciente_button"):
        found = False
        for patient in st.session_state.patients:
            if patient['dni'] == search_dni:
                # Usamos la clase CSS patient-info para los datos
                st.markdown(
                    f"""
                    <div class="patient-info">
                        <p><strong>Nombre:</strong> {patient['name']}</p>
                        <p><strong>Edad:</strong> {patient['age']}</p>
                        <p><strong>Sexo:</strong> {patient['sex']}</p>
                        <p><strong>DNI:</strong> {search_dni}</p>
                    </div>
                    """, unsafe_allow_html=True
                )
                
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
    
    if st.button("Atrás", key="back_buscar"):
        set_page('panel')

def registrar_paciente():
    st.subheader("Registrar nuevo paciente")
    p_name = st.text_input("Nombre completo")
    p_age = st.number_input("Edad", min_value=1, max_value=100)
    p_sex = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
    p_id = st.text_input("Número de DNI")
    
    if st.button("Guardar perfil", key="guardar_perfil"):
        if any(patient['dni'] == p_id for patient in st.session_state.patients):
            st.error("El DNI ya existe. Usa otro DNI.")
        else:
            new_patient = {"name": p_name, "age": p_age, "sex": p_sex, "dni": p_id, "segmentations": []}
            st.session_state.patients.append(new_patient)
            save_patients_data()
            st.success(f"Perfil de {p_name} guardado correctamente.")

    if st.button("Atrás", key="back_registrar"):
        set_page('panel')

def iniciar_segmentacion():
    st.subheader("Análisis de imágenes médicas")
    image_file = st.file_uploader("Cargar imagen", type=["jpg", "jpeg", "png"])

    if image_file is not None:
        st.session_state.image_file = image_file
        image = Image.open(image_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption='Imagen cargada correctamente', use_column_width=False, width=300)

        if st.button('Procesar imagen', key="procesar_imagen"):
            processed_image = process_image(image, model)
            st.session_state.processed_image = processed_image
            with col2:
                st.image(processed_image, caption='Máscara segmentada', use_column_width=False, width=300)
            wound_area_percentage = calculate_non_black_pixel_percentage(processed_image)
            st.write(f"Porcentaje de área de la herida: {wound_area_percentage:.2f}%")

    if st.session_state.processed_image is not None:
        if st.button("Asignar segmentación"):
            set_page('asignar_segmentacion')

    if st.button("Atrás", key="back_segmentacion"):
        set_page('panel')

def asignar_segmentacion_page():
    st.subheader("Asignar segmentación a un paciente")
    dni_input = st.text_input("Ingrese el DNI del paciente")

    if st.button("Asignar"):
        if st.session_state.processed_image is not None:
            filename = save_processed_image(st.session_state.processed_image)
            assign_segmentation_to_patient(dni_input, filename)
        else:
            st.error("No hay una segmentación disponible para asignar.")

    if st.button("Atrás", key="back_to_segmentation"):
        set_page('iniciar_segmentacion')

def calculate_non_black_pixel_percentage(mask):
    non_black_pixels = np.sum(mask > 0)
    total_pixels = mask.size
    non_black_pixel_percentage = (non_black_pixels / total_pixels) * 100
    return non_black_pixel_percentage

def process_image(image, model):
    try:
        image = np.array(image)
        image = cv2.resize(image, (224, 224))
        image = image / 255.0
        image = np.expand_dims(image, axis=0)

        prediction = model.predict(image)
        mask = prediction.squeeze()
        mask = (mask * 255).astype(np.uint8)

        return mask
    except Exception as e:
        st.write(f"Error al procesar la imagen: {e}")
        return None

def save_processed_image(mask):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SEGMENTATION_DIR}/mask_{timestamp}.png"
    mask_image = Image.fromarray(mask)
    mask_image.save(filename)
    return filename

def assign_segmentation_to_patient(dni, filename):
    for patient in st.session_state.patients:
        if patient['dni'] == dni:
            if 'segmentations' not in patient:
                patient['segmentations'] = []
            patient['segmentations'].append(filename)
            save_patients_data()
            st.success("Segmentación asignada correctamente.")
            return
    st.error("Paciente no encontrado.")

if __name__ == '__main__':
    main()
