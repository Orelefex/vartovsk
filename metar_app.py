import streamlit as st
import requests
from datetime import datetime
from bs4 import BeautifulSoup  # Для XML-парсинга


st.title('✈️ Полный декодер METAR (metartaf.ru)')

# Функция для получения данных
def get_metar(icao):
    try:
        # Пробуем получить JSON
        json_url = f"https://metartaf.ru/{icao}.json"
        response = requests.get(json_url)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            
            if 'json' in content_type:
                return response.json(), 'json'
            elif 'xml' in content_type:
                return BeautifulSoup(response.text, 'xml'), 'xml'
        
        return None, None
    except Exception as e:
        st.error(f"Ошибка запроса: {str(e)}")
        return None, None

# Функция для расшифровки
def decode_metar(data, format_type):
    result = {}
    
    try:
        if format_type == 'json':
            result['raw'] = data.get('metar', 'N/A')
            result['station'] = data.get('station', 'N/A')
            result['time'] = data.get('time', 'N/A')
        elif format_type == 'xml':
            result['raw'] = data.find('metar').text if data.find('metar') else 'N/A'
            result['station'] = data.find('station').text if data.find('station') else 'N/A'
            result['time'] = data.find('time').text if data.find('time') else 'N/A'
        
        # Разбираем сырой METAR
        metar_parts = result['raw'].split()
        if len(metar_parts) > 2:
            result['wind'] = metar_parts[2]  # Ветер
            result['visibility'] = metar_parts[3]  # Видимость
            result['clouds'] = metar_parts[4] if len(metar_parts) > 4 else 'N/A'  # Облачность
            result['temp'] = metar_parts[5] if len(metar_parts) > 5 else 'N/A'  # Температура
            result['pressure'] = metar_parts[6] if len(metar_parts) > 6 else 'N/A'  # Давление
        
        return result
    except Exception as e:
        st.error(f"Ошибка расшифровки: {str(e)}")
        return None

# Интерфейс
icao = st.text_input('Введите код ИКАО аэропорта:', 'UUEE').upper()

if st.button('Получить и расшифровать METAR'):
    if not icao.isalpha() or len(icao) != 4:
        st.error('Код аэропорта должен состоять из 4 букв (например: UUEE)')
    else:
        with st.spinner('Получаем данные...'):
            data, data_format = get_metar(icao)
            
            if data:
                st.success(f"Данные получены в формате {data_format.upper()}")
                decoded = decode_metar(data, data_format)
                
                if decoded:
                    st.subheader("Результат расшифровки:")
                    
                    # Основная информация
                    cols = st.columns(3)
                    cols[0].metric("Аэропорт", decoded['station'])
                    cols[1].metric("Время", decoded['time'])
                    cols[2].metric("Формат", data_format.upper())
                    
                    # Сырые данные
                    with st.expander("Показать сырой METAR"):
                        st.code(decoded['raw'])
                    
                    # Детализированная информация
                    st.subheader("Детали:")
                    
                    # Ветер
                    if 'wind' in decoded:
                        wind = decoded['wind']
                        direction = wind[:3] if wind[:3].isdigit() else 'N/A'
                        speed = wind[3:5] if wind[3:5].isdigit() else 'N/A'
                        st.write(f"**Ветер:** {direction}° {speed} м/с")
                    
                    # Видимость
                    if 'visibility' in decoded:
                        st.write(f"**Видимость:** {decoded['visibility']} метров")
                    
                    # Температура и давление
                    if 'temp' in decoded:
                        temp_parts = decoded['temp'].split('/')
                        if len(temp_parts) == 2:
                            st.write(f"**Температура:** {temp_parts[0]}°C, **Точка росы:** {temp_parts[1]}°C")
                    
                    if 'pressure' in decoded and decoded['pressure'].startswith('Q'):
                        st.write(f"**Давление (QNH):** {decoded['pressure'][1:]} гПа")
                    
                    # Облачность
                    if 'clouds' in decoded:
                        st.write(f"**Облачность:** {decoded['clouds']}")
                    
                    # Время обработки
                    st.caption(f"Данные обработаны: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.error("Не удалось расшифровать данные")
            else:
                st.error("Не удалось получить данные для этого аэропорта")

# Примеры кодов
st.markdown("---")
st.write("**Примеры кодов ИКАО:**")
st.code("""UUEE - Шереметьево (Москва)
UUDD - Домодедово (Москва)
ULLI - Пулково (Санкт-Петербург)
EGLL - Хитроу (Лондон)
KJFK - Кеннеди (Нью-Йорк)""")