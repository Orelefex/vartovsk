import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="METAR Decoder", page_icon="✈️")

# Стилизация
st.markdown("""
<style>
    .metar-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .section-title {
        color: #1e88e5;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title('✈️ Расшифровка METAR')
st.markdown("Введите код ИКАО аэропорта (например, UUEE) или полный METAR для расшифровки")

# Выбор режима ввода
input_mode = st.radio("Режим ввода:", ["Код ИКАО аэропорта", "Полный METAR"])

if input_mode == "Код ИКАО аэропорта":
    icao_code = st.text_input("Введите 4-буквенный код ИКАО:", "UUEE").strip().upper()
    metar_code = ""
else:
    metar_code = st.text_area(
        "Введите METAR:",
        "UUEE 141830Z 13003MPS 100V160 9999 SCT037 08/04 Q1012 R88/010070 NOSIG",
        height=100
    )
    icao_code = ""

# Кнопка расшифровки
if st.button('Получить и расшифровать'):
    with st.spinner('Получаем данные...'):
        api_url = "https://avwx.rest/api/metar/"
        headers = {"Authorization": "Bearer YOUR_API_KEY"}  # Замените на ваш ключ
        
        try:
            # Если введен код аэропорта, сначала получаем актуальный METAR
            if input_mode == "Код ИКАО аэропорта":
                if len(icao_code) != 4 or not icao_code.isalpha():
                    st.error("Код ИКАО должен состоять из 4 букв (например, UUEE, KJFK)")
                    st.stop()
                
                response = requests.get(
                    f"{api_url}{icao_code}",
                    headers=headers,
                    params={"options": "translate,summary"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    metar_code = data['raw']
                    st.markdown(f"<div class='metar-box'><strong>Полученный METAR:</strong><br>{metar_code}</div>", 
                               unsafe_allow_html=True)
                else:
                    st.error(f"Ошибка получения METAR: {response.status_code}. {response.text}")
                    st.stop()
            
            # Расшифровка METAR (полученного или введенного вручную)
            if metar_code:
                response = requests.get(
                    f"{api_url}{metar_code.strip()}",
                    headers=headers,
                    params={"options": "translate,summary,speech"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Успешно расшифровано")
                    
                    # Основная информация
                    st.markdown("<h3 class='section-title'>Основная информация</h3>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    cols[0].metric("Аэропорт", data.get("station", "N/A"))
                    cols[1].metric("Время", data.get("time", {}).get("repr", "N/A"))
                    cols[2].metric("Статус", "Актуальный" if not data.get("remarks", "").startswith("AUTO") else "Автоматический")
                    
                    # Ветер
                    if "wind" in data:
                        st.markdown("<h3 class='section-title'>Ветер</h3>", unsafe_allow_html=True)
                        wind_cols = st.columns(3)
                        wind_cols[0].metric("Направление", f"{data['wind']['direction']['repr']}°")
                        wind_cols[1].metric("Скорость", f"{data['wind']['speed']['repr']} {data['wind']['speed']['unit']}")
                        if 'gust' in data['wind']:
                            wind_cols[2].metric("Порывы", f"{data['wind']['gust']['repr']} {data['wind']['gust']['unit']}")
                    
                    # Видимость и погода
                    st.markdown("<h3 class='section-title'>Видимость и погода</h3>", unsafe_allow_html=True)
                    vis_cols = st.columns(2)
                    if "visibility" in data:
                        vis_cols[0].metric("Видимость", f"{data['visibility']['repr']} {data['visibility']['unit']}")
                    if "weather" in data and data['weather']:
                        vis_cols[1].metric("Погодные явления", ", ".join([w['repr'] for w in data['weather']]))
                    
                    # Температура и давление
                    st.markdown("<h3 class='section-title'>Температура и давление</h3>", unsafe_allow_html=True)
                    temp_cols = st.columns(2)
                    if "temperature" in data:
                        temp_cols[0].metric("Температура", f"{data['temperature']['repr']}°C")
                    if "dewpoint" in data:
                        temp_cols[0].metric("Точка росы", f"{data['dewpoint']['repr']}°C")
                    if "altimeter" in data:
                        temp_cols[1].metric("Давление", f"{data['altimeter']['repr']} {data['altimeter']['unit']}")
                    
                    # Облачность
                    if "clouds" in data and data['clouds']:
                        st.markdown("<h3 class='section-title'>Облачность</h3>", unsafe_allow_html=True)
                        for cloud in data['clouds']:
                            st.write(f"- {cloud['repr']}")
                    
                    # Дополнительная информация
                    if "remarks" in data and data['remarks']:
                        st.markdown("<h3 class='section-title'>Дополнительная информация</h3>", unsafe_allow_html=True)
                        st.write(data['remarks'])
                    
                    # Время обновления
                    st.caption(f"Данные обновлены: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                else:
                    st.error(f"Ошибка расшифровки: {response.status_code}. {response.text}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка соединения: {e}")
        except Exception as e:
            st.error(f"Неожиданная ошибка: {e}")

# Примеры популярных аэропортов
with st.expander("Примеры кодов ИКАО"):
    st.write("""
    | Аэропорт          | Код ИКАО |
    |-------------------|----------|
    | Шереметьево (Москва) | UUEE    |
    | Домодедово (Москва) | UUDD    |
    | Пулково (Санкт-Петербург) | ULLI |
    | Франкфурт (Германия) | EDDF   |
    | Хитроу (Лондон)  | EGLL     |
    | Кеннеди (Нью-Йорк) | KJFK    |
    | Шарль де Голль (Париж) | LFPG |
    """)

# Информация о сервисе
st.markdown("---")
st.caption("""
Используется API сервиса AVWX. Для работы требуется API ключ.
METAR - стандартизированный формат сводок о погоде в аэропортах.
""")