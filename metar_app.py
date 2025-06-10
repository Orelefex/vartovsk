import streamlit as st
from metar import Metar

# Должен быть самым первым вызовом в скрипте!
st.set_page_config(page_title="Расшифровщик METAR", page_icon="✈️")

# Только после этого идут остальные импорты и код
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