import streamlit as st
from PIL import Image
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

st.title("TU TITULO AQUI - Agenda de Citas")
st.subheader("Tu descripcion Aqui...")
st.write("[Tu Link Web Aqui: Mapa,Redes,Etc](https://google.com") 
img = Image.open("imagen1.jpg")
st.image(img, use_column_width=True)

# Scopes para Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Autenticar y devolver el servicio de Google Calendar."""
    creds = None
    if 'token' in st.session_state:
        creds = Credentials.from_authorized_user_info(st.session_state['token'], SCOPES)
    else:
        try:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            st.session_state['token'] = creds.to_json()
        except Exception as e:
            st.error(f"Error en la autenticación: {e}")
            return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Error al conectar con Google Calendar: {e}")
        return None

def is_time_available(service, date, time, duration=30):
    """Verificar disponibilidad del horario solicitado."""
    start_datetime = datetime.datetime.combine(date, time)
    end_datetime = start_datetime + datetime.timedelta(minutes=duration)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_datetime.isoformat() + 'Z',
        timeMax=end_datetime.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return len(events) == 0  # Devuelve True si no hay eventos en ese rango

def create_event(service, name, email, date, time, duration=30):
    """Crear un evento en Google Calendar."""
    start_datetime = datetime.datetime.combine(date, time)
    end_datetime = start_datetime + datetime.timedelta(minutes=duration)

    event = {
        'summary': f'Cita con {name}',
        'description': f'Cliente: {name}, Email: {email}',
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/Montevideo',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/Montevideo',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

# Formulario para agendar citas
with st.form("appointment_form"):
    name = st.text_input("Nombre completo")
    email = st.text_input("email o Celular")
    date = st.date_input("Fecha")
    time = st.time_input("Hora")
    submitted = st.form_submit_button("Agendar Cita")

    if submitted:
        if name and email:
            service = get_calendar_service()
            if service:
                try:
                    if is_time_available(service, date, time):
                        event = create_event(service, name, email, date, time)
                        st.success(f"Cita creada exitosamente: [Ver en Google Calendar]({event['htmlLink']})")
                    else:
                        st.warning("El horario seleccionado no está disponible. Por favor, elige otro.")
                except Exception as e:
                    st.error(f"Error al crear la cita: {e}")
        else:
            st.warning("Por favor, completa todos los campos.")
