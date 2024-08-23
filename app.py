import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
from utils import extract_from_csv, transform, load_to_csv
import io


st.set_page_config(page_title="GGives Tagger", 
                #    page_icon=banner,
                   layout="wide", 
                   initial_sidebar_state="auto", 
                   menu_items=None)

st.image('assets/GGIVES-BANNER.png', use_column_width="auto")

st.header('GGives Merchant Brand Tagging', divider='grey')
st.write("This tool simplifies the cleaning and tagging of Merchants' Raw Data by transforming the raw extracted data and loading it into clear and understandable manner, and downloadable table.")


file_up1, file_up2, file_up3 = st.columns(3)
raw_data_file = file_up1.file_uploader(label="Merchants' Raw Data:", type="csv")
merchant_tags_file = file_up2.file_uploader(label="Partners' Brand and Keywords", type="csv")
industry_guide_file = file_up3.file_uploader(label="Industry Keyword Guide", type="csv")

if raw_data_file is not None and merchant_tags_file is not None and industry_guide_file is not None:
    main_df, brand_keyword_df, industry_tags_df = extract_from_csv(raw_data_file, merchant_tags_file, industry_guide_file)
    transformed_df = transform(main_df, brand_keyword_df, industry_tags_df)

    # buffer to use for excel writer
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write the styled DataFrame to Excel
        transformed_df.to_excel(writer, sheet_name='Transformed Data', index=False)

    # Reset the buffer position
    buffer.seek(0)

    # Displaying the new DataFrame with styled cells
    st.dataframe(transformed_df, use_container_width=True)

    # Provide a download button
    download = st.download_button(
        label="Download Data as Excel",
        data=buffer,
        file_name='transformed_merchants_data.xlsx',
        mime='application/vnd.ms-excel'
    )
