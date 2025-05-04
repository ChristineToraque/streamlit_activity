import streamlit as st

st.title("Hello, Streamlit!")
st.header("This is a header")
st.write("Hello, Streamlit World")

# Text Input
user_text = st.text_input("Enter some text here:", "Default text")
st.write("You entered:", user_text)

# Number Input
user_number = st.number_input("Enter a number:", min_value=0, max_value=100, value=25, step=1)
st.write("You entered the number:", user_number)