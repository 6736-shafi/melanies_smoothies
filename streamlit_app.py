# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:',name_on_order)
# Establish the Snowflake session
session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Fetch the list of available fruits
fruit_list = my_dataframe.collect()
fruit_names = [row['FRUIT_NAME'] for row in fruit_list]

# Display the multiselect widget for ingredients selection
ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    fruit_names
    ,max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    # Construct the insert statement
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order) 
                        VALUES ('{ingredients_string}', '{name_on_order}')""";
    # st.write(my_insert_stmt);
    # st.stop()
    # Display the submit button
    if st.button('Submit order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
