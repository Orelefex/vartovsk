import streamlit as st
import requests

st.title('🌦️ METAR Decoder with API')
st.markdown("Введите код METAR для получения расшифровки")

# Поле для ввода с примером
metar_code = st.text_area(
    "Введите METAR код:", 
    "UUEE 141830Z 13003MPS 100V160 9999 SCT037 08/04 Q1012 R88/010070 NOSIG",
    height=100
)

# Разделение на колонки для кнопки и выбора формата
col1, col2 = st.columns([1, 3])
with col1:
    decode_button = st.button('Расшифровать METAR')
with col2:
    output_format = st.selectbox("Формат вывода", ["Текст", "JSON"])

if decode_button and metar_code:
    # Формируем запрос
    api_url = "https://avwx.rest/api/metar"
    headers = {
        "Authorization": "AL2owhedvyAnChsCApVcZ-OpF_H0JSQ7FfC5ia5ILPU"  # Замените на ваш ключ
    }
    
    params = {
        "options": "translate,summary,speech",
        "airport": True,
        "reporting": True,
        "format": "json"
    }
    
    try:
        response = requests.get(
            f"{api_url}{metar_code.strip()}",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if output_format == "JSON":
                st.json(data)
            else:
                # Красивый текстовый вывод
                st.success("✅ Успешно расшифровано")
                
                st.subheader("Основная информация")
                cols = st.columns(2)
                cols[0].metric("Аэропорт", data.get("station", "N/A"))
                cols[1].metric("Время наблюдения", data.get("time", {}).get("repr", "N/A"))
                
                if "wind" in data:
                    st.subheader("Ветер")
                    st.write(f"Направление: {data['wind']['direction']['repr']}°")
                    st.write(f"Скорость: {data['wind']['speed']['repr']} {data['wind']['speed']['unit']}")
                    if 'gust' in data['wind']:
                        st.write(f"Порывы: {data['wind']['gust']['repr']} {data['wind']['gust']['unit']}")
                
                if "visibility" in data:
                    st.subheader("Видимость")
                    st.write(f"{data['visibility']['repr']} {data['visibility']['unit']}")
                
                if "temperature" in data:
                    st.subheader("Температура")
                    cols = st.columns(2)
                    cols[0].metric("Температура", f"{data['temperature']['repr']}°C")
                    cols[1].metric("Точка росы", f"{data['dewpoint']['repr']}°C")
                
                if "altimeter" in data:
                    st.subheader("Давление")
                    st.write(f"{data['altimeter']['repr']} {data['altimeter']['unit']}")
                
                if "clouds" in data:
                    st.subheader("Облачность")
                    for cloud in data['clouds']:
                        st.write(f"- {cloud['repr']}")
                
                if "remarks" in data:
                    st.subheader("Примечания")
                    st.write(data['remarks'])
            
        elif response.status_code == 400:
            error_data = response.json()
            st.error(f"Ошибка 400: Неверный запрос. Детали: {error_data.get('message', 'Проверьте правильность METAR кода')}")
        elif response.status_code == 401:
            st.error("Ошибка 401: Не авторизован. Проверьте API ключ")
        else:
            st.error(f"Ошибка API: {response.status_code}. {response.text}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка соединения: {e}")
    except ValueError as e:
        st.error(f"Ошибка обработки ответа: {e}")
else:
    st.warning("Введите код METAR для расшифровки")

# Добавляем примеры для быстрого тестирования
with st.expander("Примеры METAR для теста"):
    examples = {
        "Москва Шереметьево (UUEE)": "UUEE 141830Z 13003MPS 100V160 9999 SCT037 08/04 Q1012 R88/010070 NOSIG",
        "Нью-Йорк (KJFK)": "KJFK 141851Z 16008KT 10SM FEW250 23/18 A3005",
        "Лондон Хитроу (EGLL)": "EGLL 141920Z 24015KT 9999 FEW035 BKN048 16/12 Q1018"
    }
    
    selected = st.selectbox("Выберите пример", list(examples.keys()))
    st.code(examples[selected])