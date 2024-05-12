from streamlit import session_state as ss
import streamlit as st
import pandas as pd 
import numpy as np
from plot_sankey.AutoSankey import AutoSankeyFunnel
import io

st.set_page_config(
    layout="wide"
)

# Config the muti-select input to not truncate
st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 500px;
            font-size: 0.8rem;
        }
    </style>
    """, unsafe_allow_html=True)

if 'tb' not in ss:
    ss['tb'] = None
if 'input_method' not in ss:
    ss['input_method'] = 'Upload .csv file'
# data uploader
data_input, file_uploader, get_data_button = st.columns([40,40,20])

ss['input_method'] = st.selectbox(
    label = 'How do you want to import data?',
    options = ['Upload .csv file', 'Paste the table as a csv string']
)

if ss['input_method'] == 'Upload .csv file':
    raw_data = st.file_uploader("Upload your .csv file")
else:
    raw_data = st.text_area(
         label='Copy your data table as a csv string'
    )

get_data = st.button('Import Data')

if get_data:
    if (raw_data is not None) & (ss['input_method']=='Upload .csv file'):
        tb = pd.read_csv(raw_data)
        ss['tb'] = tb

    else:
        raw_data = io.StringIO(raw_data)
        tb = pd.read_csv(raw_data)
        ss['tb'] = tb
if ss['tb'] is not None:
    column_arrangement = st.multiselect(
        label = 'Select Columns to include and arrange order',
        options = ss['tb'].columns.values,
        default = ss['tb'].columns.values
    )

    re_arrange = st.button('Re Arrange')
    
    if re_arrange:
        ss['tb'] = ss.tb[column_arrangement]
    displayed_table, inputs = st.columns([80, 20])
    
    with displayed_table:
        st.dataframe(ss['tb'], use_container_width=True)

    with inputs:
        metric_col = st.selectbox(
            label = 'Specify the name of the metric column',
            options = ss['tb'].columns
        )
        mother_node = st.text_input(
            label = 'Specify the name of the mother node (Top of funnel)'
        )
        orientation = st.selectbox(
            label = 'select orientation of plot',
            options = ['h','v']
        )
        plot = st.button('Plot Sankey')

    if plot:
        sankey = AutoSankeyFunnel(agg_table=ss['tb'], metric_col=metric_col, mother_node=mother_node).plot_sankey(plot_orientation=orientation)
        st.plotly_chart(sankey, use_container_width=True)

    
    st.divider()
    funnel_input_selectors, funnel_chart = st.columns([20,80])

    with funnel_input_selectors:
        for col in ss['tb'].drop(metric_col,axis=1).columns:
            st.selectbox(
                label=col,
                options = list(set(ss['tb'][col])),
                key='k-'+col
            )
            ss['funnel_visible_class_dict'][col] = ss['k-'+col]
        # plot_funnel_button = st.button('Plot Funnel')
    
    with funnel_chart:
        # if plot_funnel_button:
        funnel = AutoSankeyFunnel(agg_table=ss['tb'], metric_col=metric_col, mother_node=mother_node).plot_funnel(ss['funnel_visible_class_dict'])
        st.plotly_chart(funnel, use_container_width=True)
            

            


