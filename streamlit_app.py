import streamlit as st

aero_page = st.Page("aero.py", title="Аэрологическая диаграмма")
metar_page = st.Page("metar.py", title="Metar")

pg = st.navigation([aero_page, metar_page])
pg.run()

st.title("My first app")
st.write("Это только начало")