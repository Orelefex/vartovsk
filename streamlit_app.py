import streamlit as st

# aero_page = st.Page("aero_app.py", title="Аэрологическая диаграмма")
# metar_page = st.Page("metar_app.py", title="METAR")
test_page=st.Page("test_page.py", title="Тестовая страница")

pg = st.navigation([test_page])
st.set_page_config(page_title="Помощник синоптика", page_icon=":material/edit:")
pg.run()

