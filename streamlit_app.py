import streamlit as st

aero_page = st.Page("aero.py", title="Аэрологическая диаграмма")
metar_page = st.Page("metar.py", title="Metar")

pg = st.navigation([aero_page, metar_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()

