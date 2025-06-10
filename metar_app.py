import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

st.title('✈️  METAR & TAF ')

# Функция для получения данных
def get_metar_taf(icao):
    try:
        response = requests.get(f"https://metartaf.ru/{icao}.json", timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'json' in content_type:
                data = response.json()
                metar = data.get('metar', 'N/A')
                taf = data.get('taf', 'N/A')
                return metar, taf
            elif 'xml' in content_type:
                soup = BeautifulSoup(response.text, 'xml')
                metar = soup.find('metar').text if soup.find('metar') else 'N/A'
                taf = soup.find('taf').text if soup.find('taf') else 'N/A'
                return metar, taf
        return 'N/A', 'N/A'
    except Exception as e:
        st.error(f"Ошибка запроса для {icao}: {str(e)}")
        return 'N/A', 'N/A'

# Функция для обработки нескольких аэропортов
def process_airports(icao_list):
    metar_results = []
    taf_results = []
    progress_bar = st.progress(0)
    total_airports = len(icao_list)
    
    for i, icao in enumerate(icao_list):
        icao = icao.strip().upper()
        if not icao.isalpha() or len(icao) != 4:
            continue
            
        progress = (i + 1) / total_airports
        progress_bar.progress(progress)
        
        metar, taf = get_metar_taf(icao)
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Добавляем данные METAR
        metar_results.append({
            'ИКАО': icao,
            'METAR': metar,
            'Время': current_time,
            'Статус': '✅ Успешно' if metar != 'N/A' else '❌ Ошибка'
        })
        
        # Добавляем данные TAF
        taf_results.append({
            'ИКАО': icao,
            'TAF': taf,
            'Время': current_time,
            'Статус': '✅ Успешно' if taf != 'N/A' else '❌ Ошибка'
        })
    
    progress_bar.empty()
    return pd.DataFrame(metar_results), pd.DataFrame(taf_results)

# Интерфейс
input_mode = st.radio("Режим ввода:", ["Один аэропорт", "Несколько аэропортов"])

if input_mode == "Один аэропорт":
    icao = st.text_input('Введите код ИКАО аэропорта:', 'UUEE').upper()
    if st.button('Получить данные'):
        if not icao.isalpha() or len(icao) != 4:
            st.error('Код аэропорта должен состоять из 4 букв (например: UUEE)')
        else:
            with st.spinner('Получаем данные...'):
                metar, taf = get_metar_taf(icao)
                
                if metar != 'N/A' or taf != 'N/A':
                    st.success(f"Данные для {icao}:")
                    
                    # METAR
                    st.subheader('METAR')
                    st.code(metar if metar != 'N/A' else "Данные METAR недоступны")
                    
                    # TAF
                    st.subheader('TAF')
                    st.code(taf if taf != 'N/A' else "Данные TAF недоступны")
                else:
                    st.error("Не удалось получить данные")

else:
    icao_input = st.text_area(
        'Введите коды ИКАО через пробел:', 
        'UUEE UUDD ULLI',
        help='Например: UUEE UUDD KJFK EGLL'
    )
    
    if st.button('Получить данные для всех'):
        icao_list = icao_input.split()
        if not icao_list:
            st.error("Введите хотя бы один код ИКАО")
        else:
            with st.spinner('Получаем данные для всех аэропортов...'):
                metar_df, taf_df = process_airports(icao_list)
                
                # Показываем таблицу METAR
                st.subheader('METAR данные')
                st.dataframe(
                    metar_df,
                    column_config={
                        "METAR": st.column_config.TextColumn("METAR", width="large"),
                        "Статус": st.column_config.TextColumn("Статус", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Показываем таблицу TAF
                st.subheader('TAF данные')
                st.dataframe(
                    taf_df,
                    column_config={
                        "TAF": st.column_config.TextColumn("TAF", width="large"),
                        "Статус": st.column_config.TextColumn("Статус", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )

st.markdown("---")
st.caption("Данные предоставляются сервисом metartaf.ru | Обновлено: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))