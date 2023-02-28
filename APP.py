import pandas as pd
import streamlit as st
import DASHBOARD_FUNCTIONS
from sqlalchemy import create_engine


engine = create_engine("postgresql://app_user_9191:app_pass9191@20.169.221.14:9191/root")


DASHBOARD_FUNCTIONS.wide()

sidebar = DASHBOARD_FUNCTIONS.selectbox.sel_box()


if sidebar == 'Overview':
    DASHBOARD_FUNCTIONS.title_centered_h1('Overview')
    DASHBOARD_FUNCTIONS.overview.container_overveiw_data(connection=engine)
    DASHBOARD_FUNCTIONS.overview.container_overview_lineplot(connection=engine)
    DASHBOARD_FUNCTIONS.overview.plots_distribution_three(connection=engine)



if sidebar == 'Timing':
    DASHBOARD_FUNCTIONS.title_centered_h1('Timing')
    DASHBOARD_FUNCTIONS.timing.timing_header(connection=engine)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.timing.build_timing_variant(connection= engine)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.title_centered_h3('Progress Analysis')
    option = DASHBOARD_FUNCTIONS.process.build_slider_complex()
    DASHBOARD_FUNCTIONS.timing.build_conatiner_DFG(options =option,connection=engine,area_height=830)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.timing.build_variant_activity(connection=engine)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.title_centered_h3('Gantt Chart')
    DASHBOARD_FUNCTIONS.timing.build_gantt(connection=engine)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.timing.build_variant_case_identifier(connection=engine)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.timing.progress_line_plot(connection=engine)



if sidebar == 'Process':
    DASHBOARD_FUNCTIONS.title_centered_h1('Process')
    option = DASHBOARD_FUNCTIONS.process.build_slider_complex()
    DASHBOARD_FUNCTIONS.process.build_container_top(A_height=830, con=engine, option = option)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.title_centered_h4('Business Process Model Network ')
    DASHBOARD_FUNCTIONS.process.build_process_BPMNs(connection=engine, option = option)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.process.buil_variants_con_process(connection=engine)
    DASHBOARD_FUNCTIONS.line()
    DASHBOARD_FUNCTIONS.process.build_sankey_(option = option, c_height=500)
    DASHBOARD_FUNCTIONS.line()

    
    
if sidebar == "Data":
    DASHBOARD_FUNCTIONS.data.data_page(connection=engine)