import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import streamlit as st
import streamlit_nested_layout
import plotly.express as plx
import datetime
from PIL import Image
from io import BytesIO
import json
import random
import streamlit.components.v1 as components



def title_centered_h3(str_):
    title = st.markdown("""<h3 style='text-align: center'>""" + str(str_) +"""</h3>""",unsafe_allow_html =True)
    return title
def title_centered_h4(str_):
    title = st.markdown("""<h4 style='text-align: center'>""" + str(str_) +"""</h4>""",unsafe_allow_html =True)
    return title
def title_centered_h1(str_):
    title = st.markdown("""<h1 style='text-align: center'>""" + str(str_) +"""</h1>""",unsafe_allow_html =True)
    return title
def cent_text(str_):
    title = st.markdown("""<p style='text-align: center'>""" + str(str_) +"""</p>""",unsafe_allow_html =True)
    return title
def line():
    return st.markdown("""<hr>""",unsafe_allow_html=True)
def space():
    return st.markdown("""<br>""",unsafe_allow_html =True)
def wide():
    return st.set_page_config(layout="wide")



def get_gantt(xes_df :pd.DataFrame, id_):
    if id != None:
        xes_df_subset = xes_df[xes_df['case:concept:name'] == str(id_)]
        xes_df_subset = xes_df_subset[['concept:name','time:timestamp','case:concept:name']]
        xes_df_subset['time:timestamp']  = pd.to_datetime(xes_df_subset['time:timestamp'],utc=True)
        new_task = []
        for a,b in zip(xes_df_subset['concept:name'],range(len(xes_df_subset))):
            new_task.append(a+'_'+str(b))
        xes_df_subset['new_task'] = new_task
        xes_df_subset['time_end'] = xes_df_subset['time:timestamp'].shift(-1)
        return plx.timeline(xes_df_subset,x_start='time:timestamp',x_end='time_end', y ='new_task',color='new_task')



class selectbox:
    
    def sel_box():
        selectbox_ = st.sidebar.selectbox("Available Options for you to explore",('Overview','Timing','Process','Data'))
        with st.sidebar:
            space()
            st.info("If assistance is required contact platform admin")
        return selectbox_


class overview:

    def container_overveiw_data(schema= 'public',table= 'overview_header',connection=""):
        script = """SELECT * FROM """ + schema + """."""+ table
        dataframe = pd.read_sql(sql= script,con=connection)
        year_selected = st.selectbox('Year', dataframe['year'].unique().tolist())
        dataframe2 = dataframe[dataframe['year'] == year_selected]
        container_overveiw = st.container()
        with container_overveiw:    
            f1,f2,f3,f4 = st.columns(4)
            with f1:
                title_centered_h3('Cases')
                cent_text(str(dataframe2['cases'].to_list()[0]))
            with f2:
                title_centered_h3('Events')
                cent_text(str(dataframe2['events'].to_list()[0]))
            with f3:
                title_centered_h3('Activities')
                cent_text(str(dataframe2['activities'].to_list()[0]))
            with f4:
                title_centered_h3('Variants')
                cent_text(str(dataframe2['variants'].to_list()[0]))        
        return container_overveiw

    def container_overview_lineplot(schema ="public", table = "eventlog_df",connection="",cont_width =True):
        container_lineplot_1 = st.container()
        with container_lineplot_1:
            fg1, fg2 = st.columns(2)
            with fg1:
                global selection_fg1
                selection_fg1 = st.radio('Year - Month',['Year','month'])
            if selection_fg1 == 'Year':
                script = """SELECT "time:timestamp" ::date as date, count("case:concept:name") FROM """  + schema +""".""" + table + """  GROUP BY date  order by date """
                dataframe = pd.read_sql(con= connection,sql= script)
                dataframe['date'] = pd.to_datetime(dataframe['date'])
                with fg2:
                    global selector_fg2_1
                    selector_fg2_1 = st.selectbox('Select Year', dataframe['date'].dt.year.drop_duplicates().to_list() + ['total'])
                if selector_fg2_1 == 'total':
                    plot_1 = plx.area(data_frame = dataframe, x='date',y='count')
                    st.plotly_chart(plot_1,use_container_width=cont_width)
                else:
                    df = dataframe[dataframe['date'].dt.year == selector_fg2_1]
                    plot_1 = plx.area(data_frame = df, x='date',y='count')
                    st.plotly_chart(plot_1,use_container_width=cont_width)
            else:
                with fg2:
                    st.error('Monthly Analysis')
                script = """SELECT TO_CHAR("time:timestamp" ::date, 'Month') ,COUNT("case:concept:name") FROM """ +  schema + """.""" + table + """ GROUP BY TO_CHAR("time:timestamp" ::date, 'Month');"""
                dataframe = pd.read_sql(con= connection,sql= script)
                dataframe.columns = ['month','count']
                plot_1 = plx.area(data_frame = dataframe, x='month',y='count')
                st.plotly_chart(plot_1,use_container_width=cont_width)

    def plots_distribution_three(schema = "public",table ="variants_info",connection=""):
        d_container = st.container()
        with d_container:
            yu1,yu2 = st.columns(2)
            with yu1:
                title_centered_h3("Variants")
                script_01 = """SELECT "Variant Label" , ROUND("PERCENTAGE"::numeric,2) as percentage FROM """  + schema  + """.""" + table
                dataframe = pd.read_sql(sql = script_01,con= connection)
                plot_01 = plx.bar(data_frame = dataframe.head(10), x = "Variant Label", y = "percentage")
                st.plotly_chart(plot_01,use_conatiner_width = True)
                #st.markdown(script_01)
            with yu2:
                title_centered_h3('Events per case')
                script_02 = """SELECT "count" as "#activities",COUNT("dummy") as count, (COUNT("dummy") / sum(COUNT("dummy")) OVER () * 100) AS PERCENTAGE 
                        FROM (SELECT "case:concept:name" as "case", 1 as dummy, count("time:timestamp") 
                        FROM """ +  schema + """.""" + """eventlog_df GROUP BY "case") Q1 GROUP BY "#activities" ORDER BY percentage DESC"""             
                dataframe02 = pd.read_sql(sql = script_02,con= connection)
                plot_02 = plx.bar(data_frame = dataframe02.head(10), y = '#activities', x = "percentage", orientation = "h")
                st.plotly_chart(plot_02,use_conatiner_width = True)
                #st.markdown(script_02)
            #with yu3:
            #    title_centered_h3("Activities")
            #    script_03 = """ SELECT "Variant Label", "count", ("count"/sum("count") over() * 100) as percentage
            #            FROM
            #            (SELECT "Variant Label", count("ID_y") FROM """ +  schema + """.""" + """variants_info_percase
            #            GROUP BY "Variant Label") as q2
            #            ORDER BY percentage DESC  """
            #    dataframe_03 = pd.read_sql(sql = script_03,con= connection)
            #    plot = plx.bar(data_frame = dataframe_03.head(10), x = "Variant Label", y = "percentage")
            #    st.plotly_chart(plot,use_conatiner_width = True)
            #    #st.markdown(script_03)
        return d_container


class process: 
    
    def __init__(slider_complexity):

        process.slider_complexity = slider_complexity

    def build_slider_complex():
        slider_complexity = st.select_slider(label = 'Slide',options = range(0,101,1), label_visibility ='hidden',value=30)
        return slider_complexity

    def build_container_top(A_height = 800, con= '', option = None): 
        _container_ = st.container()
        with _container_:
            GFF1, GFF2 = st.columns([3,1])
            with GFF1:
                HtmlFile = open(f"Network_Code/{option}.html", 'r', encoding='utf-8')
                source_code = HtmlFile.read() 
                components.html(source_code,height = A_height)
            with GFF2:
                percentage_query = f"""SELECT MAX("CUMSUM") FROM public.variants_info where "COMPLEX_PERC" <= {option} """
                df_cumsum = pd.read_sql(con=con, sql= percentage_query)
                query_start = f""" SELECT "Activity","Number of Cases", ROUND("Number of Cases" ::numeric / (SELECT sum("Number of Cases") FROM  public.start_activities WHERE complexity = {option} ),2) * 100 AS "Percentage" FROM public.start_activities WHERE complexity = {option} """
                df_start = pd.read_sql(con=con, sql=query_start )
                query_end = f""" SELECT "Activity","Number of Cases", ROUND("Number of Cases" ::numeric / (SELECT sum("Number of Cases") FROM  public.end_activities WHERE complexity = {option} ),2) * 100 AS "Percentage" FROM public.end_activities WHERE complexity = {option} """
                df_end = pd.read_sql(con= con, sql=query_end)
                for i in range(5):
                    space()
                cent_text(f"{df_cumsum.values[0][0]:.2f} % of the data represented in this Network")
                line()
                title_centered_h4('Starting Activities')
                st.table(df_start)
                line()
                title_centered_h4('Ending Activities')
                st.table(df_end)
            line()

            with st.expander("Additional Info"):
                title_centered_h3("Percentage of Ending Activities")
                plot_ending = plx.bar(x = df_end['Activity'], y = df_end['Percentage'] )
                st.plotly_chart(plot_ending,use_container_width =True)
        
        return 2+2

    def build_process_BPMNs(option = None , connection =None, schema= "public", table= "process_bpmn_images"):
        images_dataframes = pd.read_sql(con = connection, sql = """SELECT image ::bytea,complexity FROM """ + schema + """.""" + table)
        _d_container_ = st.container()
        with _d_container_:
            byte_im = images_dataframes[images_dataframes['complexity'] == option]['image'].to_list()[0]
            image_bin = Image.open(BytesIO(byte_im))
            st.image(image_bin,use_column_width =True)
        return _d_container_
    
    def build_sankey_(option = None, c_height = 600):

        __c_container__ = st.container()
        with __c_container__:
                
                
                sd1, sd2  =  st.columns([1,40])
                with  sd2:
                    HtmlFile = open(f"Sankey_Code/{option}.html", 'r', encoding='utf-8')
                    source_code = HtmlFile.read() 
                    components.html(source_code, height = c_height)

    def build_additional_maps(connection =None,option=None):
        
        script_other_maps = f"""SELECT complexity, "Petri_Net_Inductive"::bytea, "Petri_Net_Alpha"::bytea, "Petri_Net_Alpha_plus"::bytea  FROM public.additional_maps WHERE complexity = {option}"""
        data_other_maps = pd.read_sql(con = connection, sql = script_other_maps)

        d1,d2 = st.columns ([5,1])
        with d1:
            big_image_byte = data_other_maps['Petri_Net_Inductive'].to_list()[0]
            image_ = Image.open(BytesIO(big_image_byte))
            st.image(image_,use_column_width=True)
        with d2:
            st.download_button("Download Petri Net Inductive", data = BytesIO(data_other_maps['Petri_Net_Inductive'].to_list()[0]),mime= 'image/jpeg')
            st.download_button("Download Petri Net Alpha", data = BytesIO(data_other_maps['Petri_Net_Alpha'].to_list()[0]),mime= 'image/jpeg')
            st.download_button("Download Petri Net Alpha Plus", data = BytesIO(data_other_maps['Petri_Net_Alpha_plus'].to_list()[0]),mime= 'image/jpeg')

    def buil_variants_con_process(connection = ""):

        query_data = """
        SELECT 
            "TRACE",
            "PERCENTAGE",
            "Variant Label",
            ((CHAR_LENGTH("TRACE") - CHAR_LENGTH(REPLACE("TRACE", ',', ''))) / CHAR_LENGTH(',')) + 1 AS "length of Variant"
        FROM
            public.variants_info """
        df_data = pd.read_sql(con= connection, sql =query_data)
        df_data['PERCENTAGE'] = pd.to_numeric(df_data['PERCENTAGE'])
        container_l = st.container()
        with container_l:
            title_centered_h3("Variants")
            l1,l2,l3 = st.columns([2,1,1])
            with l1:
                title_centered_h4("Select Variant")
                global selector_variant
                selector_variant = st.selectbox("select Variant",df_data["Variant Label"].to_list())   
            df_trimmed = df_data[df_data['Variant Label'] == selector_variant]
            with l2:
                title_centered_h4("Length of the Trace")
                num_ele = df_trimmed["length of Variant"].to_list()[0]
                perc_ocurr = df_trimmed["PERCENTAGE"].to_list()[0]
                st.info(f"Number of elements: {num_ele}")
                st.info(f"Number of elements: {perc_ocurr:.2f}")
            with l3:
                title_centered_h4("Elements of the Trace")
                cent_text(df_trimmed['TRACE'].to_list()[0])

            s1,s2 = st.columns(2)
            with s1:
                global sel_opt
                sel_opt = st.radio(label ="selection",label_visibility= "hidden",options = ['length of variance', 'Ocurrance of Variance'], horizontal = True)
            with  s2:
                global number
                number = st.number_input('Insert a number ov Variants to view', value = 150)
            
            if sel_opt == 'length of variance':
                plot_len = plx.bar(data_frame = df_data.head(number), x = "Variant Label", y = "length of Variant")
                st.plotly_chart(plot_len, use_container_width = True)            
            else:
                plot_len = plx.bar(data_frame = df_data.head(number), x =  "Variant Label", y = 'PERCENTAGE')
                st.plotly_chart(plot_len, use_container_width = True)


class timing:

    def build_conatiner_DFG(options = None, area_height = 800,connection = None):
        
        script_1 = f""" SELECT * FROM public.timing_visual WHERE "complexity" = '{options}' """
        data_timing = pd.read_sql(con= connection, sql = script_1)

        CONTAINER_FULL = st.container()
        with CONTAINER_FULL:
            column1 , columns2 = st.columns([1,3])
            with column1:
                df_time_header = pd.DataFrame(json.loads(data_timing.iloc[0,1]))  
                subcol1, subcol2, subcol3 = st.columns(3)
                with subcol1:
                    title_centered_h4('Days')
                    cent_text(df_time_header.iloc[0,2])
                with subcol2:
                    title_centered_h4('Hours')
                    cent_text(df_time_header.iloc[0,3])
                with subcol3:
                    title_centered_h4('Minutes')
                    cent_text(df_time_header.iloc[0,4])
                line()
                st.table(pd.DataFrame(json.loads(data_timing.iloc[0,-1])))
            with columns2:
                HtmlFile = open(f"DFG_Code/{options}.html", 'r', encoding='utf-8')
                source_code = HtmlFile.read() 
                components.html(source_code,height = area_height)

    def timing_header(connection = None):

        initial_query = """SELECT min("time:timestamp") as "MIN", max("time:timestamp") as "MAX" FROM public.eventlog_df"""
        df_initial = pd.read_sql(con= connection, sql = initial_query)
        initial_value = df_initial['MIN'].to_list()[0]
        ending_value = df_initial['MAX'].to_list()[0]

        query_time_diff = """SELECT EXTRACT(epoch FROM max("time:timestamp")  - min("time:timestamp")) / 86400 AS days_diff FROM public.eventlog_df"""
        time_diff_df  = pd.read_sql(con= connection, sql = query_time_diff)
        val = time_diff_df['days_diff'].to_list()[0]
        days_val = int(val)
        hours = (val % 1) * 24
        hours_val = int(hours)
        mins = (hours%1) * 60 
        mins_val = int(mins)
        secs = mins%1
        secs_val = int(secs)

        d_container= st.container()
        with d_container:
            f1,f2,f3,f4,f5,f6 = st.columns(6)
            for i in [f2,f3,f4,f5]:
                with i:
                    line()
            with f1:
                title_centered_h3('Initial Time')
                cent_text(initial_value)
            with f6:
                title_centered_h3('Initial Time')
                cent_text(ending_value)
        
            with st.expander('Time elapsed Details'):
                g1,g2,g3,g4 =  st.columns(4)

                with g1:
                    title_centered_h4('Days')
                    cent_text(days_val)
                with g2:
                    title_centered_h4('Hours')
                    cent_text(hours_val)
                with g3:
                    title_centered_h4('Minutes')
                    cent_text(mins_val)
                with g4:
                    title_centered_h4('Seconds')
                    cent_text(secs_val)

    def build_timing_variant(connection=None):

        SCRIPT1 = """SELECT "ID_y" FROM public.variants_info_percase """
        cases_list = pd.read_sql(con= connection, sql = SCRIPT1)
        col1 , col2 = st.columns([2,1])
        with col1:
            global case_selector
            global df2_
            case_selector = st.selectbox(label = "Select Case", options =  cases_list['ID_y'].to_list())
            idx_list = (cases_list.index.to_list())
            rand_list = []
            for i in np.arange(5):
                rand_list.append(random.randrange(len(idx_list)))
            elems = []
            for i in rand_list:
                elems.append(cases_list.loc[i,'ID_y'])
    
            elems_tuple_str = str(tuple(elems + [case_selector]))
            SCRIPT2 = f"""
            SELECT 
                "case:concept:name" as Case, 
                ROUND(EXTRACT(EPOCH FROM (max - min)) / 60,2) as Interval 
            FROM (
                SELECT 
                    "case:concept:name" , 
                    MIN("time:timestamp") AS MIN , 
                    MAX("time:timestamp") AS MAX
                FROM public.eventlog_df 
                WHERE "case:concept:name" IN {elems_tuple_str} 
                GROUP BY "case:concept:name") AS Q """
            df2_ = pd.read_sql(con= connection, sql = SCRIPT2)
            bar_plot_len_case = plx.bar(data_frame = df2_, x = 'case', y = 'interval')
            st.plotly_chart(bar_plot_len_case,use_container_width = True)
        
        with col2:
            cd1, cd2, cd3 = st.columns(3)
            with cd1:
                title_centered_h4("Variant")
                script3 = f"""SELECT "Variant Label" FROM public.variants_info_percase WHERE "ID_y" = '{case_selector}'""" 
                d_df =  pd.read_sql(con=connection,sql = script3)
                space()
                cent_text(d_df["Variant Label"].to_list()[0])
            with cd2:
                title_centered_h4("Case")
                space()
                cent_text(case_selector)
            with cd3:
                title_centered_h4("Time Elapsed In Hours")
                cent_text(str(df2_[df2_['case'] == case_selector]['interval'].to_list()[0]))
            line()

            script4 = f"""
                    SELECT 
                        "time:timestamp" AS TIME , 
                        "concept:name" AS ACTIVITY ,
                        "case:concept:name" AS CASE  FROM public.eventlog_df   
                    WHERE 
                        "case:concept:name" =  '{case_selector}' """
            
            df__ = pd.read_sql(con=connection,sql=script4)
            df__['time'] = pd.to_datetime(df__['time'])
            df__['shifted'] = df__['time'].shift(-1)
            df__['interval'] = df__['shifted'] - df__['time']  
            df__['interval'] = df__['interval'].astype('timedelta64[m]')
            df__['interval'] = df__['interval'].fillna(0).astype(float)
            st.table(df__[['time','activity','interval']])

    def build_variant_activity(connection=None):

        container_elem = st.container()
        with container_elem:    
            c_col1, c_col2 = st.columns([1,2])
            with c_col1:
                global act_vari_selector
                act_vari_selector = st.radio(label = "Seelct", label_visibility ="hidden",options = ["Variant","Activity"],horizontal =True)

            if act_vari_selector == "Variant":
                with c_col2:
                    global variant_Selector, df_1
                    script = """SELECT "Variant Label" FROM public.variants_info"""
                    df_1 = pd.read_sql(con= connection,sql= script)
                    variant_Selector = st.selectbox(label = "select Variant",label_visibility ="hidden",options = df_1['Variant Label'].to_list())

                w_col1, w_col2 = st.columns([1,2])
                with w_col1:
                    random_vars = []
                    for i in np.arange(5):
                        random_vars.append(f"Variant {random.randrange(len(df_1))}")
                    
                    script__1 =  f"""
                    SELECT
                        "Variant Label",
                        AVG(EXTRACT(EPOCH FROM max-min) /60) as "minutes"
                    FROM
                        (
                            SELECT
                                t1."Variant Label",
                                t1."ID_y" as case,
                                min(t2."time:timestamp") as "min",
                                max(t2."time:timestamp") as "max"
                            FROM public.variants_info_percase t1
                            LEFT JOIN  public.eventlog_df t2
                            ON t1."ID_y" = t2."case:concept:name"
                            WHERE t1. "Variant Label" in {tuple(random_vars + [variant_Selector])}
                            GROUP BY t1."Variant Label", t1."ID_y"
                        ) as F_TABLE
                    GROUP BY
                        "Variant Label"
                    """
                    df_variants_interval = pd.read_sql(con= connection, sql=script__1)
                    plot_variants_interval = plx.bar(orientation = "h", data_frame= df_variants_interval, y = 'Variant Label', x = "minutes")
                    st.plotly_chart(plot_variants_interval,use_container_width=True)
                    

                with w_col2:
                    script__2 = f"""
                    SELECT 
                        "concept", 
                        MIN(seconds_passed) AS MIN,
                        MAX(seconds_passed) AS MAX, 
                        AVG(seconds_passed) as AVG,
                        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY SECONDS_PASSED) as MEDIAN,  
                        PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY SECONDS_PASSED) as Q75, 
                        PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY SECONDS_PASSED) as Q25,
                        STDDEV(SECONDS_PASSED) AS STD
                    FROM
                        (
                            SELECT
                                "Case",
                                "concept", 
                                ROUND(EXTRACT(EPOCH FROM lead-time),4) as SECONDS_PASSED
                            FROM
                                (
                                    SELECT 
                                        "Case",
                                        "concept",
                                        "time",
                                        lead("time",1) over(PARTITION by "Case" ORDER BY "time")
                                    FROM
                                        (
                                            SELECT
                                                t1."Variant Label",
                                                t1."ID_y" as "Case",
                                                t2."concept:name" as "concept",
                                                t2."time:timestamp" as time
                                            FROM public.variants_info_percase t1
                                            LEFT JOIN public.eventlog_df t2
                                            ON t1."ID_y" = t2."case:concept:name"
                                            WHERE "Variant Label" = '{variant_Selector}'
                                        ) TST
                                ) TST2
                        )TST3
                    GROUP BY "concept" """
                    df_concept_summary = pd.read_sql(con = connection,sql = script__2).fillna(0)
                    space()
                    space()
                    st.table(df_concept_summary)


            else:
                w_col1_, w_col2_ = st.columns([1,2])
                with c_col2:
                    global activity_select
                    script__3 = """ SELECT DISTINCT("concept:name") FROM public.eventlog_df """
                    activity_select = st.selectbox(label = "Select Activity", label_visibility = "hidden", options = pd.read_sql(con= connection,sql = script__3)['concept:name'])
                    space()
                    space()
                with w_col1_:
                    script__4 = f"""
                        SELECT
                            "concept",
                            count("seconds_passed") as count, 
                            min("seconds_passed") as min, 
                            max("seconds_passed") as max,
                            avg("seconds_passed") as avg,
                            STDDEV("seconds_passed") as STD,
                            PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY "seconds_passed") as MEDIAN,
                            PERCENTILE_CONT(0.75) WITHIN GROUP(ORDER BY "seconds_passed") as q75,
                            PERCENTILE_CONT(0.25) WITHIN GROUP(ORDER BY "seconds_passed") as q25
                        FROM
                            (
                                SELECT
                                    "concept",
                                    ROUND(EXTRACT(EPOCH FROM lead-time),4) as SECONDS_PASSED
                                FROM
                                    (
                                        SELECT 
                                            "concept",
                                            "time",
                                            lead("time",1) OVER(PARTITION BY "Case" ORDER BY "time")
                                        FROM
                                            (
                                                SELECT
                                                    t1."ID_y" as "Case",
                                                    t2."concept:name" as "concept" ,
                                                    t2."time:timestamp" as time
                                                FROM
                                                    public.variants_info_percase t1
                                                    LEFT JOIN public.eventlog_df t2
                                                    ON t1."ID_y" = t2."case:concept:name"
                                            ) TST
                                    ) TST2
                            ) TST3
                        WHERE
                            "concept" = '{activity_select}'
                        GROUP BY "concept"  """
                    df_activity = pd.read_sql(con = connection, sql = script__4)
                    df_activity = df_activity.T
                    df_activity.columns = df_activity.iloc[0,:]
                    df_activity = df_activity.drop("concept")
                    st.table(df_activity)
                    
                with w_col2_:
                    with st.expander("Box Plot"):
                        script__5 = f"""
                            SELECT 
                                "concept", 
                                ROUND(EXTRACT(EPOCH FROM lead-time),4) as interval
                            FROM
                                (
                                    SELECT
                                        "concept",
                                        "time",
                                        lead("time",1) OVER(PARTITION BY "Case" ORDER BY "time")
                                    FROM
                                        (
                                            SELECT
                                                t1."ID_y" as "Case",
                                                t2."concept:name" as "concept" ,
                                                t2."time:timestamp" as time
                                            FROM
                                                public.variants_info_percase t1
                                                LEFT JOIN public.eventlog_df t2
                                                ON t1."ID_y" = t2."case:concept:name"
                                        ) TST
                                ) TST2
                            WHERE "concept" = '{activity_select}' """
                        df_boxplot = pd.read_sql(con= connection, sql= script__5)
                        boxplot = plx.box(data_frame = df_boxplot, x = 'interval')
                        st.plotly_chart(boxplot,use_container_width = True)
                    space()
                    with st.expander("Scatter  Plot"):
                        script__6 = f"""
                            SELECT 
                                "concept", ROUND(EXTRACT(EPOCH FROM lead-time),4) as interval,"time"
                            FROM
                                (
                                    SELECT "concept","time",lead("time",1) OVER(PARTITION BY "Case" ORDER BY "time")
                                    FROM
                                        (
                                            SELECT t1."ID_y" as "Case",t2."concept:name" as "concept" ,t2."time:timestamp" as time
                                            FROM public.variants_info_percase t1
                                            LEFT JOIN public.eventlog_df t2
                                            ON t1."ID_y" = t2."case:concept:name"
                                        ) TST
                                )TST2
                            WHERE "concept" = '{activity_select}' """
                        df_scatterplot = pd.read_sql(con= connection, sql= script__6)
                        scatterplot = plx.scatter(data_frame = df_scatterplot, x = 'interval', y = "time")
                        st.plotly_chart(scatterplot,use_container_width = True)                   
                    space()
                    with st.expander("Line Plot"):
                            script__7 = f"""  SELECT "date", count("concept")
                            FROM (
                                SELECT "concept", ROUND(EXTRACT(EPOCH FROM lead-time),4) as SECONDS_PASSED,DATE("time")
                                FROM
                                    (
                                    SELECT "concept","time",lead("time",1) OVER(PARTITION BY "Case" ORDER BY "time")
                                    FROM
                                            (
                                            SELECT t1."ID_y" as "Case",t2."concept:name" as "concept" ,t2."time:timestamp" as time
                                            FROM public.variants_info_percase t1
                                            LEFT JOIN public.eventlog_df t2
                                            ON t1."ID_y" = t2."case:concept:name"
                                            ) TST
                                    ) TST2 
                                WHERE concept = '{activity_select}'
                            ) TST3
                            group by "date" """
                            df_lineplot = pd.read_sql(con= connection,sql= script__7)
                            lineplot_ = plx.area(data_frame= df_lineplot, x = "date", y = "count")
                            st.plotly_chart(lineplot_, use_container_width= True)

    def build_gantt(connection = None):

        gantt_container = st.container()
        with gantt_container:

            sd1, sd2 = st.columns(2)

            with sd1:
                space()
                title_centered_h4('Select the Case to Analyze')

            with sd2 : 
                global select_cases
                global _df_
                select_cases = st.selectbox(
                    label = 'Select Case___s',
                    label_visibility = 'hidden',
                    options = pd.read_sql(
                        con = connection, 
                        sql = """SELECT "ID_y" FROM public.variants_info_percase """)['ID_y'].to_list()
                )
                query_df = f""" SELECT * FROM public.eventlog_df WHERE "case:concept:name" = '{select_cases}' """
                _df_ = pd.read_sql(sql= query_df, con = connection)

        gantt_chart =  get_gantt(xes_df = _df_, id_ = select_cases)
        st.plotly_chart(gantt_chart, use_container_width=True)

    def build_variant_case_identifier(connection=""):

            xc_container= st.container()
            with xc_container:
                with st.expander("Case & Variant"):
                    xc_col1, xc_col2 = st.columns(2)
                    with xc_col1:
                        title_centered_h4("Find case per Variant")
                        _script1 = """SELECT "Variant Label" FROM public.variants_info """
                        variants_df = pd.read_sql(con= connection,sql= _script1)
                        variant_Selector_ = st.selectbox(label = "select Variant _1_",label_visibility ="hidden",options = variants_df['Variant Label'].to_list(), index= 3)
                        script_2 = f"""SELECT "ID_y" FROM  public.variants_info_percase  WHERE  "Variant Label" = '{variant_Selector_}' """
                        data_f = pd.read_sql(con= connection, sql = script_2)
                        cent_text(str(data_f.iloc[0,0]))

                    with xc_col2:
                        title_centered_h4("Find Variant per Case")
                        script_3 = """SELECT "ID_y" FROM  public.variants_info_percase"""                     
                        cases_df = pd.read_sql(con= connection,sql = script_3 )
                        case_selector_ = st.selectbox(label = "select Variant _1a_",label_visibility ="hidden",options = cases_df['ID_y'].to_list(),index = 2)
                        script_4 = f""" SELECT "Variant Label" FROM  public.variants_info_percase WHERE "ID_y" =  '{case_selector_}' """                    
                        cases_data_df = pd.read_sql(con= connection,sql = script_4)
                        cent_text(str(cases_data_df.iloc[0,0]))        

    def progress_line_plot(connection = ""):
        b_container = st.container()
        with b_container:
            string_1= """SELECT DISTINCT  "case:concept:name" as Case FROM public.eventlog_df """  
            cases_list = pd.read_sql(con= connection, sql = string_1)["case"].to_list()
            b_col1,b_col2 = st.columns([1,2])
            with b_col1:
                global a_selector,b_selector,c_selector,d_selector,e_selector
                a_selector = st.selectbox(label = "Case 1",  options = cases_list, index = 1)
                b_selector = st.selectbox(label = "Case 2",  options = cases_list, index = 2)
                c_selector = st.selectbox(label = "Case 3",  options = cases_list, index = 3)
                d_selector = st.selectbox(label = "Case 4",  options = cases_list, index = 4)
                e_selector = st.selectbox(label = "Case 5",  options = cases_list, index = 5)

            str_ = f"""('{a_selector}','{b_selector}','{c_selector}', '{d_selector}','{e_selector}') """
            string_plot = f"""SELECT "concept:name" AS concept, "time:timestamp" as time, "case:concept:name" as case  FROM public.eventlog_df  WHERE  "case:concept:name" IN {str_} """ 
            df_plot = pd.read_sql(con=connection,sql= string_plot)

            dfs_ = []

            with b_col2:
                st.plotly_chart(plx.line(df_plot,x = 'concept', y = "time", markers= True, color= "case"),use_container_width = True)
            
        return b_container
                    




class data:

    def data_page(connection= None ):

        title_centered_h1("Data")
        cent_text("Please reveiw a subset of the Data")

        xc_container = st.container()
        with xc_container:
            script1 = """SELECT * FROM  public.eventlog_df  WHERE  "case:concept:name" IN (SELECT DISTINCT("case:concept:name") FROM public.eventlog_df  limit 1 ) """
            st.table(pd.read_sql(con= connection, sql = script1))
            line()

            sd_col1, sd_col2 = st.columns(2)

            with sd_col1:
                script2 = """SELECT * FROM public.variants_info_percase LIMIT 10 """
                st.table(pd.read_sql(con= connection, sql = script2))

            with sd_col2:
                space()
                space()
                st.info('Developed By Alejandro Velez for Accelerate INC. ')
        return xc_container
        



