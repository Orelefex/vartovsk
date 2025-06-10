import streamlit as st
import requests

st.title('METAR Decoder (API)')

metar_code = st.text_input("Введите METAR код:", "UUEE 141830Z 13003MPS")

if st.button('Расшифровать через API'):
    try:
        response = requests.get(f"https://avwx.rest/api/metar/{metar_code}?options=translate", 
                              headers={"Authorization": "POTAUFgKSXEpZVfx64B_epiSQi2_ou3sQ9gnc4WuIBo"	
})
        if response.status_code == 200:
            data = response.json()
            st.json(data)  # или красиво оформите вывод
        else:
            st.error(f"Ошибка API: {response.status_code}")
    except Exception as e:
        st.error(f"Ошибка: {e}")
