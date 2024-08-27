import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
from utils import extract_from_csv, transform, load_to_csv, get_metric, plot_bar_brands, plot_bar_channel

import io


st.set_page_config(page_title="GGives Tagger", 
                #    page_icon=banner,
                   layout="wide", 
                   initial_sidebar_state="auto", 
                   menu_items=None)

st.image('assets\GGIVES_MERCHANT_BRAND_TAGGING_[DRAFT 1].svg', use_column_width="auto")

st.header('GGives Merchant Brand Tagging', divider='grey')
st.write("This tool simplifies the cleaning and tagging of Merchants' Raw Data by transforming the raw extracted data and loading it into clear and understandable manner, and downloadable table.")


file_up1, file_up2, file_up3 = st.columns(3)
raw_data_file = file_up1.file_uploader(label="Merchants' Raw Data:", type="csv")
merchant_tags_file = file_up2.file_uploader(label="Partners' Brand and Keywords", type="csv")
industry_guide_file = file_up3.file_uploader(label="Industry Keyword Guide", type="csv")

if raw_data_file is not None and merchant_tags_file is not None and industry_guide_file is not None:
    main_df, brand_keyword_df, industry_tags_df = extract_from_csv(raw_data_file, merchant_tags_file, industry_guide_file)
    transformed_df = transform(main_df, brand_keyword_df, industry_tags_df)
    total_transactions, matched_transactions, number_of_merchants, number_of_matched_merchants = get_metric(transformed_df)

    st.subheader('Summary', divider='grey')
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric(label="Number of Merchants", value=number_of_merchants)
    metric_2.metric(label="Total Transactions", value=total_transactions)
    metric_3.metric(label="Tagged Merchants (Key Partners)", value=number_of_matched_merchants)
    metric_4.metric(label="Tagged Transactions", value=matched_transactions)

    graph_1, graph_2 = st.columns(2)
    graph_1.plotly_chart(plot_bar_brands(transformed_df))
    graph_2.plotly_chart(plot_bar_channel(transformed_df))

    # Create the two tables and display them
    table_1, table_2 = st.columns(2)

    with table_1:
        with st.expander("Output 1"):
            # Display DataFrame for Output 1
            output_1 = transformed_df[['merchant_id', 'submerchant_id', "rfi (don't mind)", 'wallet_id',
                                    'channel', 'Channel Tags', 'merchant_name', 'Brand Tagging', 'Partner Keyword Matched']]
            st.dataframe(output_1)

            # Create a buffer for Output 1
            buffer_1 = io.BytesIO()

            # Write Output 1 to Excel using the buffer
            with pd.ExcelWriter(buffer_1, engine='xlsxwriter') as writer:
                output_1.to_excel(writer, sheet_name='Output 1', index=False)

            # Reset the buffer position for Output 1
            buffer_1.seek(0)

            # Provide a download button for Output 1
            st.download_button(
                label="Download Output 1 as Excel",
                data=buffer_1,
                file_name='output_1.xlsx',
                mime='application/vnd.ms-excel'
            )

    with table_2:
        with st.expander("Output 2"):
            # Group by 'Brand Tagging' and aggregate for Output 2
            output_2 = transformed_df.groupby('Brand Tagging').agg({
                'Industry': lambda x: x.mode().iloc[0],  # Get the most frequent industry
                'Channel Tags': lambda x: ', '.join(x.unique())  # Get all unique channel tags concatenated
            }).reset_index()
            st.dataframe(output_2)

            # Create a buffer for Output 2
            buffer_2 = io.BytesIO()

            # Write Output 2 to Excel using the buffer
            with pd.ExcelWriter(buffer_2, engine='xlsxwriter') as writer:
                output_2.to_excel(writer, sheet_name='Output 2', index=False)

            # Reset the buffer position for Output 2
            buffer_2.seek(0)

            # Provide a download button for Output 2
            st.download_button(
                label="Download Output 2 as Excel",
                data=buffer_2,
                file_name='output_2.xlsx',
                mime='application/vnd.ms-excel'
            )