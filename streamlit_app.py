# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Establish the Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Fetch the list of available fruits
fruit_list = my_dataframe.collect()
fruit_names = [row['FRUIT_NAME'] for row in fruit_list]

# Display the multiselect widget for ingredients selection
ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    
    # Fetch and display fruit nutrition information from Fruityvice API
    for fruit_chosen in ingredients_list:
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}")
        if fruityvice_response.status_code == 200:
            fruityvice_data = fruityvice_response.json()
            fv_df = pd.DataFrame([fruityvice_data])
            st.dataframe(fv_df, use_container_width=True)
        else:
            st.write(f"Could not retrieve data for {fruit_chosen}")
    
    # Construct the insert statement
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
                         VALUES ('{ingredients_string}', '{name_on_order}')"""
    
    # Display the submit button
    if st.button('Submit order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# Close the session after use
session.close()
