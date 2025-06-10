import streamlit as st
import requests

st.title('✈️ Декодер METAR (metartaf.ru)')
icao = st.text_input('Введите код ИКАО аэропорта:', 'UUEE').upper()

if st.button('Получить METAR'):
    try:
        response = requests.get(f'https://metartaf.ru/{icao}.xml')
        if response.status_code == 200:
            metar = response.json().get('metar', '')
            st.success(f'METAR для {icao}:')
            st.code(metar)
        else:
            st.error('Ошибка при запросе данных')
    except Exception as e:
        st.error(f'Ошибка: {e}')