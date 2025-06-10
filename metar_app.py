import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


st.title('✈️  METAR ')

# Функция для получения данных
def get_metar(icao):
    try:
        response = requests.get(f"https://metartaf.ru/{icao}.json", timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'json' in content_type:
                return response.json(), 'json'
            elif 'xml' in content_type:
                return BeautifulSoup(response.text, 'xml'), 'xml'
        return None, None
    except Exception as e:
        st.error(f"Ошибка запроса для {icao}: {str(e)}")
        return None, None

# Функция для обработки нескольких аэропортов
def process_airports(icao_list):
    results = []
    progress_bar = st.progress(0)
    total_airports = len(icao_list)
    
    for i, icao in enumerate(icao_list):
        icao = icao.strip().upper()
        if not icao.isalpha() or len(icao) != 4:
            continue
            
        progress = (i + 1) / total_airports
        progress_bar.progress(progress)
        
        data, data_format = get_metar(icao)
        if data:
            metar_text = data.get('metar', 'N/A') if data_format == 'json' else (
                data.find('metar').text if data.find('metar') else 'N/A'
            )
            results.append({
                'ИКАО': icao,
                'METAR': metar_text,
                'Время': datetime.now().strftime('%H:%M:%S'),
                'Статус': '✅ Успешно'
            })
        else:
            results.append({
                'ИКАО': icao,
                'METAR': 'N/A',
                'Время': datetime.now().strftime('%H:%M:%S'),
                'Статус': '❌ Ошибка'
            })
    
    progress_bar.empty()
    return pd.DataFrame(results)

# Интерфейс
input_mode = st.radio("Режим ввода:", ["Один аэропорт", "Несколько аэропортов"])

if input_mode == "Один аэропорт":
    icao = st.text_input('Введите код ИКАО аэропорта:', 'UUEE').upper()
    if st.button('Получить METAR'):
        if not icao.isalpha() or len(icao) != 4:
            st.error('Код аэропорта должен состоять из 4 букв (например: UUEE)')
        else:
            with st.spinner('Получаем данные...'):
                data, data_format = get_metar(icao)
                if data:
                    st.success(f"METAR для {icao}:")
                    st.code(data.get('metar', 'N/A') if data_format == 'json' else (
                        data.find('metar').text if data.find('metar') else 'N/A'
                    ))
                else:
                    st.error("Не удалось получить данные")

else:
    icao_input = st.text_area(
        'Введите коды ИКАО через пробел:', 
        'UUEE UUDD ULLI',
        help='Например: UUEE UUDD KJFK EGLL'
    )
    
    if st.button('Получить METAR для всех'):
        icao_list = icao_input.split()
        if not icao_list:
            st.error("Введите хотя бы один код ИКАО")
        else:
            with st.spinner('Получаем данные для всех аэропортов...'):
                df = process_airports(icao_list)
                st.dataframe(
                    df,
                    column_config={
                        "METAR": st.column_config.TextColumn("METAR", width="large"),
                        "Статус": st.column_config.TextColumn("Статус", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
# Примеры кодов
with st.expander("Примеры кодов ИКАО"):
    st.table(pd.DataFrame({
        "Аэропорт": ["Шереметьево", "Домодедово", "Пулково", "Хитроу", "Кеннеди"],
        "Код ИКАО": ["UUEE", "UUDD", "ULLI", "EGLL", "KJFK"]
    }))

st.markdown("---")
st.caption("Данные предоставляются сервисом metartaf.ru | Обновлено: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))