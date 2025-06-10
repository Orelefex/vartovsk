import streamlit as st
import requests

st.title('✈️ Простой декодер METAR')
st.write("Введите 4-буквенный код аэропорта (например, UUEE для Шереметьево)")

# Ваш API ключ (получите бесплатно на avwx.rest)
API_KEY = "AL2owhedvyAnChsCApVcZ-OpF_H0JSQ7FfC5ia5ILPU"  # Замените на реальный ключ!

# Функция для получения METAR
def get_metar(icao_code):
    url = f"https://avwx.rest/api/metar/{icao_code}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на ошибки
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при запросе данных: {str(e)}")
        return None

# Основной интерфейс
icao = st.text_input("Код аэропорта (ИКАО):", "UUEE").strip().upper()

if st.button("Получить погоду"):
    if not icao.isalpha() or len(icao) != 4:
        st.error("Код аэропорта должен состоять из 4 букв (например: UUEE, KJFK)")
    else:
        with st.spinner("Загружаем данные..."):
            metar_data = get_metar(icao)
            
            if metar_data:
                st.success(f"Данные для {icao} получены!")
                
                # Вывод сырых данных METAR
                st.subheader("METAR:")
                st.code(metar_data.get("raw", "Нет данных"))
                
                # Основная информация
                st.subheader("Основные данные:")
                cols = st.columns(2)
                cols[0].metric("Аэропорт", metar_data.get("station", "—"))
                cols[1].metric("Время", metar_data.get("time", {}).get("repr", "—"))
                
                # Ветер
                if "wind" in metar_data:
                    wind = metar_data["wind"]
                    wind_str = f"{wind['direction']['repr']}° {wind['speed']['repr']} {wind['speed']['unit']}"
                    if "gust" in wind:
                        wind_str += f", порывы {wind['gust']['repr']}"
                    st.metric("Ветер", wind_str)
                
                # Температура и видимость
                if "temperature" in metar_data:
                    cols = st.columns(2)
                    cols[0].metric("Температура", f"{metar_data['temperature']['repr']}°C")
                    if "dewpoint" in metar_data:
                        cols[1].metric("Точка росы", f"{metar_data['dewpoint']['repr']}°C")
                
                if "visibility" in metar_data:
                    st.metric("Видимость", f"{metar_data['visibility']['repr']} {metar_data['visibility']['unit']}")

# Примеры кодов аэропортов
st.markdown("---")
st.write("Популярные коды аэропортов:")
st.code("""UUEE - Шереметьево (Москва)
UUDD - Домодедово (Москва)
ULLI - Пулково (Санкт-Петербург)
EGLL - Хитроу (Лондон)
KJFK - Кеннеди (Нью-Йорк)
LFPG - Шарль-де-Голль (Париж)""")

# Информация о API
st.markdown("---")
st.caption("Для работы приложения требуется API ключ от avwx.rest. Бесплатная версия позволяет 100 запросов в день.")