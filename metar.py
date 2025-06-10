import streamlit as st
from metar import Metar

st.set_page_config(page_title="Расшифровщик METAR", page_icon="✈️")

# Функция для красивой расшифровки
def decode_metar(metar_text):
    try:
        obs = Metar.Metar(metar_text)
        decoded = {
            "Аэропорт": obs.station_id,
            "Время наблюдения": obs.time.strftime("%d.%m.%Y %H:%M UTC"),
            "Ветер": f"{obs.wind_speed.value} м/с, направление {obs.wind_dir.value}°" if obs.wind_speed else "Штиль",
            "Порывы ветра": f"{obs.wind_gust.value} м/с" if obs.wind_gust else "Нет",
            "Видимость": f"{obs.visibility().replace('Visibility:', '').strip()}",
            "Погодные явления": obs.present_weather() or "Нет значимых явлений",
            "Облачность": obs.sky_conditions(" | "),
            "Температура": f"{obs.temp.value}°C",
            "Точка росы": f"{obs.dewpt.value}°C",
            "Давление (QNH)": f"{obs.press.value} гПа ({round(obs.press.value * 0.750062, 1)} мм рт. ст.)"
        }
        return decoded, None
    except Metar.ParserError as e:
        return None, f"Ошибка: {e}"

# Интерфейс
st.title("✈️ Профессиональный расшифровщик METAR")
st.caption("Используется библиотека Metar для точного разбора авиационных метеосообщений")

with st.expander("ℹ️ Примеры METAR"):
    st.code("""
    METAR UUEE 141630Z 12004MPS 9999 -RA FEW007 BKN016 OVC025 03/02 Q1009 R32L/290050 NOSIG
    METAR LFPG 141730Z 24015G25KT 200V280 8000 -SHRA SCT012 BKN020CB 08/04 Q0988 TEMPO 4000 TSRA
    METAR KJFK 141751Z 36010KT 10SM FEW030 BKN250 22/18 A2992 RMK AO2 SLP130 T02220183
    """)

metar_input = st.text_area(
    "Введите METAR-сообщение:",
    value="METAR UUEE 141630Z 12004MPS 9999 -RA FEW007 BKN016 OVC025 03/02 Q1009 R32L/290050 NOSIG",
    height=100
)

if st.button("Расшифровать", type="primary"):
    if metar_input.strip():
        result, error = decode_metar(metar_input)
        
        if error:
            st.error(error)
            st.markdown("**Проверьте:**")
            st.markdown("- Формат должен начинаться с `METAR` или `SPECI`")
            st.markdown("- Даты/время в формате `DDHHMMZ`")
            st.markdown("- Нет опечаток в кодах облачности/явлений")
        else:
            st.success("Успешно расшифровано!")
            
            cols = st.columns(2)
            for i, (key, value) in enumerate(result.items()):
                cols[i % 2].markdown(f"**{key}:** {value}")
            
            st.divider()
            st.subheader("Raw METAR Parsing:")
            st.code(str(Metar.Metar(metar_input))), None
    else:
        st.warning("Введите METAR-сообщение для расшифровки")

st.markdown("---")
