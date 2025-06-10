import streamlit as st
import requests

st.title('🍃 Простой декодер METAR')
st.write('Введите код аэропорта (например, UUEE для Шереметьево)')

# Поле для ввода кода аэропорта
icao = st.text_input('Код ИКАО аэропорта:', 'UUEE').upper()

if st.button('Получить METAR'):
    if len(icao) != 4 or not icao.isalpha():
        st.error('Ошибка: код должен быть 4 буквы (например, UUEE)')
    else:
        try:
            # Получаем данные METAR
            response = requests.get(
                f'https://avwx.rest/api/metar/{icao}',
                headers={'Authorization': 'AL2owhedvyAnChsCApVcZ-OpF_H0JSQ7FfC5ia5ILPU'},
                params={'options': 'translate'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Выводим основные данные
                st.success(f'Текущий METAR для {icao}:')
                st.code(data['raw'])
                
                st.subheader('Расшифровка:')
                st.write(f"**Аэропорт:** {data.get('station', '—')}")
                st.write(f"**Время:** {data.get('time', {}).get('repr', '—')}")
                
                if 'wind' in data:
                    wind = data['wind']
                    st.write(f"**Ветер:** {wind['direction']['repr']}° {wind['speed']['repr']} {wind['speed']['unit']}")
                
                if 'temperature' in data:
                    st.write(f"**Температура:** {data['temperature']['repr']}°C")
                
                if 'visibility' in data:
                    st.write(f"**Видимость:** {data['visibility']['repr']} {data['visibility']['unit']}")
                
                if 'clouds' in data:
                    st.write('**Облачность:**')
                    for cloud in data['clouds']:
                        st.write(f"- {cloud['repr']}")
            
            else:
                st.error(f'Ошибка: {response.status_code}. Не удалось получить данные.')
        
        except Exception as e:
            st.error(f'Произошла ошибка: {str(e)}')

# Подсказка с примерами
st.markdown('---')
st.write('Примеры кодов аэропортов:')
st.write('- UUEE - Шереметьево (Москва)')
st.write('- UUDD - Домодедово (Москва)')
st.write('- EGLL - Хитроу (Лондон)')
st.write('- KJFK - Кеннеди (Нью-Йорк)')