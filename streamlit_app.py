import streamlit as st
import tensorflow as tf
from PIL import Image
import cv2
import numpy as np

# Cargar el modelo de TensorFlow
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model('SegNet_trained.h5')  # Cambia la ruta si es necesario
    return model

model = load_model()

# Diccionario temporal para almacenar usuarios registrados
if 'users' not in st.session_state:
    st.session_state.users = {}

# Almacenar el estado de la página actual
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # Página principal por defecto

def main():
    session_state = st.session_state

    # Mostrar la página correspondiente según el estado actual
    if session_state.page == 'home':
        home_page(session_state)
    elif session_state.page == 'login':
        login_page(session_state)
    elif session_state.page == 'register':
        register_page(session_state)
    elif session_state.page == 'panel':
        show_page(session_state)
    elif session_state.page == 'buscar_paciente':
        buscar_paciente(session_state)
    elif session_state.page == 'registrar_paciente':
        registrar_paciente(session_state)
    elif session_state.page == 'iniciar_segmentacion':
        iniciar_segmentacion(session_state)

def home_page(session_state):
    """Página de inicio con título y botones centrados"""
    st.markdown("<h1 style='text-align: center;'>SEGAp</h1>", unsafe_allow_html=True)

    # Centrando los botones en una columna
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

    if st.button("Iniciar Sesión", key="login"):
        session_state.page = 'login'

    st.markdown("<br>", unsafe_allow_html=True)  # Añadir un espacio

    if st.button("Registrarse", key="register"):
        session_state.page = 'register'

    st.markdown("</div>", unsafe_allow_html=True)

def login_page(session_state):
    """Página de inicio de sesión"""
    st.subheader("Iniciar sesión")
    username = st.text_input("Nombre de usuario")
    password = st.text_input("Contraseña", type='password')
    
    if st.button("Login"):
        # Verificar si el usuario existe y la contraseña es correcta
        if username in session_state.users and session_state.users[username] == password:
            session_state.logged_in = True
            session_state.username = username
            # Cambiar al panel principal
            session_state.page = 'panel'
        else:
            st.error("Nombre de usuario o contraseña incorrectos")
    
    if st.button("Atrás"):
        session_state.page = 'home'

def register_page(session_state):
    """Página de registro"""
    st.subheader("Registrarse")
    new_username = st.text_input("Nuevo nombre de usuario")
    new_password = st.text_input("Nueva contraseña", type='password')
    confirm_password = st.text_input("Confirmar contraseña", type='password')
    
    if st.button("Registrarse"):
        if new_password == confirm_password:
            # Almacenar el nuevo usuario en el diccionario
            session_state.users[new_username] = new_password
            st.success(f"Registrado con éxito. Ahora puedes iniciar sesión con {new_username}")
        else:
            st.error("Las contraseñas no coinciden")

    if st.button("Atrás"):
        session_state.page = 'home'

def show_page(session_state):
    """Mostrar la página principal con opciones."""
    st.title(f"Bienvenido {session_state.username}")
    st.subheader("Selecciona una opción:")

    # Centrando los botones en una columna
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

    if st.button("Buscar paciente"):
        session_state.page = 'buscar_paciente'

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Registrar paciente nuevo"):
        session_state.page = 'registrar_paciente'

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Iniciar la segmentación"):
        session_state.page = 'iniciar_segmentacion'

    st.markdown("<br>", unsafe_allow_html=True)

    # Botón de cerrar sesión
    if st.button("Cerrar sesión"):
        session_state.page = 'home'

    st.markdown("</div>", unsafe_allow_html=True)

def buscar_paciente(session_state):
    """Función para buscar paciente"""
    st.subheader("Buscar paciente existente")
    search = st.text_input("Buscar paciente por DNI")
    if st.button("Buscar"):
        st.write(f"Resultados de la búsqueda para el DNI: {search}")
    if st.button("Atrás"):
        session_state.page = 'panel'

def registrar_paciente(session_state):
    """Función para registrar nuevo paciente"""
    st.subheader("Registrar nuevo paciente")
    p_name = st.text_input("Nombre completo")
    p_age = st.number_input("Edad", min_value=1, max_value=100)
    p_sex = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
    p_id = st.text_input("Número de DNI")
    if st.button("Guardar perfil"):
        st.success(f"Perfil de {p_name} guardado correctamente.")
    if st.button("Atrás"):
        session_state.page = 'panel'

def iniciar_segmentacion(session_state):
    """Función para iniciar la segmentación"""
    st.subheader("Análisis de imágenes médicas")
    image_file = st.file_uploader("Cargar imagen", type=["jpg", "jpeg", "png"])

    if image_file is not None:
        image = Image.open(image_file)

        # Limitar el tamaño de la imagen
        resized_image = image.resize((300, 300))  # Cambiar a las dimensiones que desees
        
        # Crear dos columnas: una para la imagen original y otra para la imagen segmentada
        col1, col2 = st.columns(2)

        with col1:
            st.image(resized_image, caption='Imagen cargada correctamente', use_column_width=True)

        if st.button('Procesar imagen'):
            processed_image = process_image(image, model)
            with col2:
                if processed_image is not None:
                    st.image(processed_image, caption='Máscara segmentada', use_column_width=True)
    
    # Botón para volver a la interfaz principal
    if st.button("Atrás"):
        session_state.page = 'panel'

# Función para preprocesar y procesar la imagen utilizando el modelo
def process_image(image, model):
    try:
        image = np.array(image)
        image = cv2.resize(image, (224, 224))  # Cambiar a las dimensiones necesarias para el modelo
        image = image / 255.0  # Normalizar la imagen
        image = np.expand_dims(image, axis=0)

        # Hacer la predicción con el modelo
        prediction = model.predict(image)

        # Procesar la predicción para hacerla visible (normalizar a 0-255)
        mask = prediction.squeeze()  # Eliminar dimensiones adicionales
        mask = (mask * 255).astype(np.uint8)  # Normalizar a rango [0, 255]

        return mask  # Retornar la máscara segmentada como imagen
    except Exception as e:
        st.write(f"Error al procesar la imagen: {e}")
        return None

if __name__ == '__main__':
    main()
