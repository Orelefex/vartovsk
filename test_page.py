import streamlit as st
import requests
import polars as pl
from datetime import datetime
import re

st.title('✈️ Авиационная метеоинформация')

# Стили для улучшенного отображения
st.markdown("""
<style>
    .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .metar-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .taf-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .weather-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    .section-title {
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .airport-card {
        border-left: 4px solid #1e3a8a;
        padding-left: 1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Кэшируем запросы к API и загрузку данных
@st.cache_data(ttl=3600)
def get_metar_taf(icao):
    try:
        response = requests.get(f"https://metartaf.ru/{icao}.json", timeout=10)
        response.raise_for_status()
        
        if 'application/json' in response.headers.get('content-type', ''):
            data = response.json()
            return data.get('metar', 'N/A'), data.get('taf', 'N/A')
        return 'N/A', 'N/A'
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка запроса для {icao}: {str(e)}")
        return 'N/A', 'N/A'

@st.cache_data
def load_airport_data():
    try:
        df = pl.read_excel("ICAO.xls")
        required_columns = {"icao_code", "name_rus", "name_eng", "city_rus", "city_eng", "country_rus"}
        
        if not required_columns.issubset(df.columns):
            st.error(f"Файл ICAO.xls должен содержать столбцы: {required_columns}")
            return None
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки файла ICAO.xls: {str(e)}")
        return None

# Функции для расшифровки METAR/TAF
def decode_metar(metar):
    if metar == 'N/A':
        return "Данные METAR недоступны"
    
    decoded = []
    parts = metar.split()
    
    # Словари для расшифровки
    DIRECTIONS = {
        'N': 'северный', 'NE': 'северо-восточный', 'E': 'восточный',
        'SE': 'юго-восточный', 'S': 'южный', 'SW': 'юго-западный',
        'W': 'западный', 'NW': 'северо-западный'
    }
    
    CLOUD_TYPES = {
        'FEW': 'незначительная (1-2/8 неба)',
        'SCT': 'разрозненные (3-4/8 неба)',
        'BKN': 'значительная (5-7/8 неба)',
        'OVC': 'сплошная (8/8 неба)'
    }
    
    # Обработка каждой части METAR
    for part in parts:
        # Дата и время
        if re.match(r'^\d{6}Z$', part):
            time_str = f"{part[2:4]}:{part[4:6]} UTC {part[:2]} числа"
            decoded.append(f"🕒 Время наблюдения: {time_str}")
        
        # Ветер
        elif re.match(r'^(\d{3})(\d{2,3})(G\d{2,3})?(KT|MPS|KMH)$', part):
            match = re.match(r'^(\d{3})(\d{2,3})(G\d{2,3})?(KT|MPS|KMH)?$', part)
            wind_dir = int(match.group(1))
            wind_speed = match.group(2)
            gust = match.group(3)[1:] if match.group(3) else None
            unit = 'м/с' if match.group(4) == 'MPS' else 'узлов'
            
            # Определение направления
            dir_deg = (wind_dir + 22) // 45 * 45 % 360
            compass = {
                0: 'северный', 45: 'северо-восточный', 90: 'восточный',
                135: 'юго-восточный', 180: 'южный', 225: 'юго-западный',
                270: 'западный', 315: 'северо-западный'
            }.get(dir_deg, '')
            
            wind_str = f"🌬️ Ветер: {wind_dir}° ({compass}) {wind_speed} {unit}"
            if gust:
                wind_str += f", порывы до {gust} {unit}"
            decoded.append(wind_str)
        
        # Видимость
        elif re.match(r'^\d{4}$', part):
            vis = int(part)
            if vis >= 10000:
                decoded.append("👀 Видимость: 10+ км")
            else:
                decoded.append(f"👀 Видимость: {vis//1000 if vis%1000==0 else vis/1000:.1f} км")
        elif part == 'CAVOK':
            decoded.append("👀 Видимость: 10+ км, без осадков и значительной облачности")
        
        # Облачность
        elif re.match(r'^(FEW|SCT|BKN|OVC)\d{3}(CB|TCU)?$', part):
            cloud_type = CLOUD_TYPES.get(part[:3], part[:3])
            height = int(part[3:6]) * 30
            cloud_str = f"   - {cloud_type} на {height} метрах"
            if 'CB' in part:
                cloud_str += " (кучево-дождевые)"
            elif 'TCU' in part:
                cloud_str += " (башнеобразные)"
            
            if not any('☁️ Облачность:' in s for s in decoded):
                decoded.append("☁️ Облачность:")
            decoded.append(cloud_str)
        
        # Температура и точка росы
        elif re.match(r'^(M?\d{2})/(M?\d{2})$', part):
            temp, dew = part.split('/')
            temp = temp.replace('M', '-')
            dew = dew.replace('M', '-')
            decoded.append(f"🌡️ Температура: {temp}°C, точка росы: {dew}°C")
        
        # Давление
        elif re.match(r'^Q\d{4}$', part):
            pressure = part[1:]
            decoded.append(f"⏱️ Давление: {pressure} гПа (QNH)")
    
    return "\n".join(decoded)

def decode_taf(taf):
    if taf == 'N/A':
        return "Данные TAF недоступны"
    
    decoded = ["🕒 Основной прогноз:"]
    current_block = []
    
    # Разбиваем TAF на временные блоки
    parts = re.split(r'(TEMPO|BECMG|FM\d{6}|PROB\d{2})', taf)
    period_type = "MAIN"
    
    for part in parts:
        if part in ['TEMPO', 'BECMG'] or part.startswith(('FM', 'PROB')):
            # Сохраняем предыдущий блок
            if current_block:
                decoded.append("\n".join(current_block))
                current_block = []
            
            # Определяем тип нового блока
            if part == 'TEMPO':
                period_type = "TEMPO"
                current_block.append("⏳ Временные изменения (TEMPO):")
            elif part == 'BECMG':
                period_type = "BECMG"
                current_block.append("🔄 Постепенные изменения (BECMG):")
            elif part.startswith('FM'):
                period_type = "FM"
                time_str = f"{part[2:4]}:{part[4:6]} UTC {part[6]} числа"
                current_block.append(f"⌛ С {time_str}:")
            elif part.startswith('PROB'):
                period_type = "PROB"
                prob = part[4:6]
                current_block.append(f"❔ Вероятность {prob}%:")
        else:
            # Обрабатываем метеоданные внутри блока
            metar_lines = decode_metar(part).split('\n')
            
            # Добавляем информацию о нижней границе облачности
            cloud_info = []
            for line in metar_lines:
                if line.startswith('☁️ Облачность:'):
                    cloud_info.append(line)
                elif 'на' in line and ('метрах' in line or 'футах' in line):
                    cloud_info.append(line)
            
            if cloud_info:
                current_block.append("\n".join(cloud_info))
            
            for line in metar_lines:
                if line.startswith(('🕒', '🌬️', '👀', '🌡️', '⏱️')):
                    if period_type in ["TEMPO", "BECMG", "FM", "PROB"]:
                        current_block.append(f"   {line}")
                    else:
                        current_block.append(line)
    
    if current_block:
        decoded.append("\n".join(current_block))
    
    # Улучшаем форматирование для Streamlit
    final_output = []
    for line in decoded:
        if line.startswith(('⏳', '🔄', '⌛', '❔')):
            final_output.append("\n" + line)
        else:
            final_output.append(line)
    
    return "\n".join(final_output)

# Загрузка данных
name_icao_df = load_airport_data()
if name_icao_df is None:
    st.stop()

def get_airport_info(icao_code):
    result = name_icao_df.filter(pl.col("icao_code") == icao_code)
    
    if result.is_empty():
        return None
    
    row = result.row(0, named=True)
    
    return {
        "Название": row["name_rus"] if row["name_rus"] else row["name_eng"],
        "Город": row["city_rus"] if row["city_rus"] else row["city_eng"],
        "Страна": row["country_rus"],
        "ИКАО": icao_code
    }

# Интерфейс
st.sidebar.header("Настройки")
mode = st.sidebar.radio("Режим работы:", ["Один аэропорт", "Несколько аэропортов"])

if mode == "Один аэропорт":
    icao_code = st.sidebar.text_input('Введите код ИКАО аэропорта (4 буквы):', 'UUEE').strip().upper()
    
    if icao_code:
        if len(icao_code) != 4 or not icao_code.isalpha():
            st.error("Код ИКАО должен состоять из 4 букв")
        else:
            airport_info = get_airport_info(icao_code)
            
            if airport_info:
                st.markdown(f"<div class='airport-card'>", unsafe_allow_html=True)
                st.subheader(f"{airport_info['Название']} ({airport_info['ИКАО']})")
                st.write(f"📍 **Город:** {airport_info['Город']}")
                st.write(f"🌍 **Страна:** {airport_info['Страна']}")
                
                # Автоматически получаем метеоданные
                with st.spinner('Получаем актуальные метеоданные...'):
                    metar, taf = get_metar_taf(icao_code)
                    
                    # METAR
                    st.markdown("**METAR (актуальная погода):**")
                    if metar != 'N/A':
                        with st.expander("Показать оригинал METAR"):
                            st.code(metar, language="text")
                        st.markdown("**Расшифровка:**")
                        st.write(decode_metar(metar))
                    else:
                        st.warning("Данные METAR недоступны")
                    
                    # TAF
                    st.markdown("**TAF (прогноз погоды):**")
                    if taf != 'N/A':
                        with st.expander("Показать оригинал TAF"):
                            st.code(taf, language="text")
                        st.markdown("**Расшифровка:**")
                        st.write(decode_taf(taf))
                    else:
                        st.warning("Данные TAF недоступны")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning(f"Аэропорт с кодом {icao_code} не найден в базе данных")

else:  # Несколько аэропортов
    icao_codes_input = st.sidebar.text_area(
        'Введите коды ИКАО аэропортов (по одному на строку или через запятую/пробел):',
        'UUEE\nUUDD\nULLI'
    ).strip().upper()
    
    # Разбираем ввод пользователя
    icao_list = []
    for line in icao_codes_input.split('\n'):
        for part in re.split(r'[,;\s]+', line):
            if len(part) == 4 and part.isalpha():
                icao_list.append(part)
    
    if icao_list:
        st.sidebar.success(f"Найдено аэропортов: {len(icao_list)}")
        
        # Ограничим количество аэропортов для производительности
        if len(icao_list) > 10:
            st.warning("Выбрано слишком много аэропортов. Показаны первые 10.")
            icao_list = icao_list[:10]
        
        progress_bar = st.progress(0)
        total_airports = len(icao_list)
        
        for i, icao_code in enumerate(icao_list):
            progress_bar.progress((i + 1) / total_airports)
            
            airport_info = get_airport_info(icao_code)
            
            if airport_info:
                st.markdown(f"<div class='airport-card'>", unsafe_allow_html=True)
                st.subheader(f"{airport_info['Название']} ({airport_info['ИКАО']})")
                st.write(f"📍 **Город:** {airport_info['Город']}")
                st.write(f"🌍 **Страна:** {airport_info['Страна']}")
                
                # Получаем метеоданные
                metar, taf = get_metar_taf(icao_code)
                
                # METAR
                with st.expander(f"METAR для {icao_code}"):
                    if metar != 'N/A':
                        st.code(metar, language="text")
                        st.markdown("**Расшифровка:**")
                        st.write(decode_metar(metar))
                    else:
                        st.warning("Данные METAR недоступны")
                
                # TAF
                with st.expander(f"TAF для {icao_code}"):
                    if taf != 'N/A':
                        st.code(taf, language="text")
                        st.markdown("**Расшифровка:**")
                        st.write(decode_taf(taf))
                    else:
                        st.warning("Данные TAF недоступны")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning(f"Аэропорт с кодом {icao_code} не найден в базе данных")

# Подвал
st.markdown("---")
st.caption(f"ℹ️ Данные предоставляются сервисом metartaf.ru | Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")