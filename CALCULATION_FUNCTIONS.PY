import pandas as pd
import pm4py
import networkx as nx
from pyvis.network import Network
import pyvis
import numpy as np
import warnings
from typing import Union
import ast
import plotly.express as plx
import plotly.graph_objects as go
from collections import OrderedDict
import datetime
import os
from PIL import Image
from io import BytesIO

warnings.simplefilter(action='ignore')


class utils_utils: # --------------------------------------- Misc. Functions

    def scale_range(input,min,max):
        input += -(np.min(input))
        input /= np.max(input) / (max - min)
        input += min
        return input

    def get_df_overview_summary_header(eventlog_dataframe, evntlog):
        dataframe = []
        years = pd.to_datetime(eventlog_dataframe['time:timestamp']).dt.year.unique()
        for year in years:
            df_year = eventlog_dataframe[eventlog_dataframe['time:timestamp'].dt.year == year]
            no_cases = len(df_year['case:concept:name'].unique())
            no_events = len(df_year)
            no_activities = len(df_year['concept:name'].unique())
            try:
                log = pm4py.filter_time_range(evntlog, dt1=datetime.datetime(day=1,month=1,year=year), dt2=datetime.datetime(day=31,month=12,year=year))
                print('Done - Attempt : 1')
            except:
                try:
                    log = pm4py.filter_time_range(evntlog, dt1=datetime.datetime(day=1,month=1,year=year), dt2=datetime.datetime(day=31,month=12,year=year))
                    print('Done - Attempt : 2')
                except:
                    pass
            no_variants =len(transformation_utils.GET_TRANSFORMED_DATA_BIG(event_log=log)[1])
            #no_variants =len(GET_TRANSFORMED_DATA_BIG(event_log=evntlog)[1])
            dataframe_overview_header = pd.DataFrame({'cases':[no_cases],'events':[no_events],'activities':[no_activities],'variants':[no_variants],'year':[year]})
            dataframe.append(dataframe_overview_header)
        dataframe_overview_header = pd.concat(dataframe)
        return dataframe_overview_header

    def human_time_duration(seconds):
        TIME_DURATION_UNITS = (
            ('year',60 * 60 * 24 * 365),
            ('month',60 * 60 * 24 * 30.41),
            ('week', 60*60*24*7),
            ('day', 60*60*24),
            ('hour', 60*60),
            ('min', 60),
            ('sec', 1))
        if seconds == 0:
            return 'inf'
        parts = []
        for unit, div in TIME_DURATION_UNITS:
            amount, seconds = divmod(int(seconds), div)
            if amount > 0:
                parts.append('{} {}{}'.format(amount, unit, "" if amount == 1 else "s"))
        return ', '.join(parts)

    def get_size_format(b, factor=1024, suffix="B"):
        """
        Scale bytes to its proper byte format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if b < factor:
                return f"{b:.2f}{unit}{suffix}"
            b /= factor
        return f"{b:.2f}Y{suffix}"

    def compress_img(image_name, new_size_ratio=0.9, quality=90, width=None, height=None, to_jpg=True):
        # load the image to memory
        img = Image.open(image_name)
        # print the original image shape
        #print("[*] Image shape:", img.size)
        # get the original image size in bytes
        image_size = os.path.getsize(image_name)
        # print the size before compression/resizing
        #print("[*] Size before compression:", utils_utils.get_size_format(image_size))
        if new_size_ratio < 1.0:
            # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
            img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
            # print new image shape
            #print("[+] New Image shape:", img.size)
        elif width and height:
            # if width and height are set, resize with them instead
            img = img.resize((width, height), Image.ANTIALIAS)
            # print new image shape
            #print("[+] New Image shape:", img.size)
        # split the filename and extension
        filename, ext = os.path.splitext(image_name)
        # make new filename appending _compressed to the original file name
        if to_jpg:
            # change the extension to JPEG
            new_filename = f"{filename}_compressed.jpg"
        else:
            # retain the same extension of the original image
            new_filename = f"{filename}_compressed{ext}"
        try:
            # save the image with the corresponding quality and optimize set to True
            img.save(new_filename, quality=quality, optimize=True)
        except OSError:
            # convert the image to RGB mode first
            img = img.convert("RGB")
            # save the image with the corresponding quality and optimize set to True
            img.save(new_filename, quality=quality, optimize=True)
        #print("[+] New file saved:", new_filename)
        # get the new image size in bytes
        new_image_size = os.path.getsize(new_filename)
        # print the new size in a good format
        #print("[+] Size after compression:", utils_utils.get_size_format(new_image_size))
        # calculate the saving bytes
        saving_diff = new_image_size - image_size
        # print the saving percentage
        #print(f"[+] Image size change: {saving_diff/image_size*100:.2f}% of the original image size.")


class transformation_utils: # --------------------------------------- Functions to Transform the Data

    def GET_TRANSFORMED_DATA(EVENTLOG_DATA_FRAME : pd.DataFrame ):
        """
        Takes an eventlog Dataframe and returns twop dataframes with processed data
        """
        TRACES = []
        ID = []

        for case_con_name in EVENTLOG_DATA_FRAME['case:concept:name'].unique():
            df_con_name = EVENTLOG_DATA_FRAME[EVENTLOG_DATA_FRAME['case:concept:name'] == case_con_name]
            TRACES.append(df_con_name['concept:name'].to_list())
            ID.append(case_con_name)
        DATAFRAME_0 = pd.DataFrame({'TRACE':TRACES,'ID':ID})
        # ----------------DataFrame With the Variant Label, ID  and Tarce  ------------- 
        DATAFRAME_0['TRACE'] = DATAFRAME_0['TRACE'].astype(str)
        DATAFRAME_1 = DATAFRAME_0.groupby('TRACE').count().reset_index()
        DATAFRAME_1['Variant Label'] = ['Variant ' + str(i) for i in range(len(DATAFRAME_1))]
        DATAFRAME_1 = DATAFRAME_1.merge(DATAFRAME_0,on='TRACE',how= 'left')

        # ---------------DataFrame with Sumamry Data -------------
        DATAFRAME_2 = DATAFRAME_0.groupby('TRACE').count().reset_index()
        DATAFRAME_2['PERCENTAGE'] = (DATAFRAME_2['ID'] / DATAFRAME_2['ID'].sum() ) *100
        DATAFRAME_2 = DATAFRAME_2.sort_values('PERCENTAGE',ascending=False)
        DATAFRAME_2['CUMSUM'] = np.cumsum(DATAFRAME_2["PERCENTAGE"])
        DATAFRAME_2 = DATAFRAME_2.merge(DATAFRAME_1.drop_duplicates(subset='Variant Label'), on='TRACE',how='left')
        DATAFRAME_2 = DATAFRAME_2.drop(['ID','ID_x','ID_y'],axis=1)
        DATAFRAME_2['COMPLEX_PERC'] =  utils_utils.scale_range(  input = [float(d) for d in range(len(DATAFRAME_2))],  min=0,  max=100 )

        return DATAFRAME_1, DATAFRAME_2

    def GET_FILTERED_EVENTLOG(DATAFRAME_arg: pd.DataFrame , LEVEL: Union[int , float], eventlog_to_filter : pm4py.objects.log.obj.EventLog):
        """
        Takes as arguments a dataframe with a column named 'TRACE' containing 
        tuples with traces and another column with the name 'CUMSUM' used to filter.
        This function returns an enventlog object.

        """
        traces_to_work = DATAFRAME_arg[DATAFRAME_arg['COMPLEX_PERC']<= LEVEL]['TRACE'].apply(
            lambda x: tuple(ast.literal_eval(x))).to_list()
        if len(traces_to_work) <= 0:
            traces_to_work = DATAFRAME_arg[DATAFRAME_arg['CUMSUM']<= DATAFRAME_arg['COMPLEX_PERC'].min() ]['TRACE'].apply(
                lambda x: tuple(ast.literal_eval(x))).to_list()
        try:
            eventlog_filtered = pm4py.filter_variants(
                log = eventlog_to_filter,
                retain=True,
                variants=traces_to_work)
        except:
            try:
                eventlog_filtered = pm4py.filter_variants(
                    log = eventlog_to_filter,
                    retain=True,
                    variants=traces_to_work)
            except:
                pass
        return eventlog_filtered, traces_to_work

    def GET_TRANSFORMED_DATA_BIG(event_log : pm4py.objects.log.obj.EventLog):
        """
        Takes an eventlog  and returns two dataframes with processed data
        """
        s = pm4py.get_variants_as_tuples(event_log)
        keys = list(s.keys())
        values = list(s.values())
        dfs = []
        for trace, data in zip(keys,values):
            dataframes =  []
            for trace_ in data:
                trace_list_details = str(list(trace))
                case_concept_name = trace_._attributes['concept:name']
                df = pd.DataFrame({
                    'TRACE': [trace_list_details],
                    'ID_y': [case_concept_name]})
                dataframes.append(df)
            df_final = pd.concat(dataframes)
            df_final['ID_x'] = len(data)
            dfs.append(df_final)
        DF_FINAL_TRACES_0 = pd.concat(dfs)
        DF_FINAL_TRACES_1 = DF_FINAL_TRACES_0.groupby('TRACE')['ID_y'].count().to_frame().reset_index()
        DF_FINAL_TRACES_1['Variant Label'] =  ['Variant ' + str(i)for i in range(len(DF_FINAL_TRACES_1))]
        # --------------------------------
        DF_FINAL_TRACES_2 = DF_FINAL_TRACES_0.merge(DF_FINAL_TRACES_1[['TRACE','Variant Label']], how = 'left', on = 'TRACE')
        DF_FINAL_TRACES_2 = DF_FINAL_TRACES_2[['TRACE','ID_x','Variant Label','ID_y']]
        # --------------------------------
        DF_FINAL_TRACES_1['PERCENTAGE'] = (DF_FINAL_TRACES_1['ID_y'] /  DF_FINAL_TRACES_1['ID_y'].sum()) * 100
        DF_FINAL_TRACES_1 = DF_FINAL_TRACES_1.sort_values('PERCENTAGE', ascending = False)
        DF_FINAL_TRACES_1['CUMSUM'] = np.cumsum(DF_FINAL_TRACES_1["PERCENTAGE"])
        DF_FINAL_TRACES_1 = DF_FINAL_TRACES_1[['TRACE','PERCENTAGE','CUMSUM','Variant Label']]
        DF_FINAL_TRACES_1['COMPLEX_PERC'] =  utils_utils.scale_range(  input = [float(d) for d in range(len(DF_FINAL_TRACES_1))],  min=0,  max=100 )

        return DF_FINAL_TRACES_2,DF_FINAL_TRACES_1 


class sankey_utils: # --------------------------------------- Functions to build the Sankey Diagrams

    def get_sankey(name:str , nodes_base: pd.DataFrame, _colors_ = True,height = 800, width = 800):
        """
        This Function Takes Three Arguments
        name : String with the name of the final output given to the sankey diagram Created
        nodes_base : Dataframe with the source and target nodes with their respective arc Value
        _colors_: boolean with the instruction to apply colors to the Sankey Diagram or have grey links with blue nodes
        """

        if  not os.path.isdir('Sankey_Code'):
            os.makedirs("Sankey_Code")
        _label = pd.concat([nodes_base['Source'], nodes_base['Target']]).drop_duplicates().to_list()
        _source = []
        _target = []
        _values = []
        for a, b, c in zip(nodes_base['Source'], nodes_base['Target'],nodes_base['arc_value'] ): 
            _source.append(_label.index(a))
            _target.append(_label.index(b))
            _values.append(c)

        if _colors_ == True:
            r = 14
            g = 14
            b = 225 
            color_node_ = []
            color_line_ = []
            for i in range(len(_source)):
                if r <= 10 or g <=10 or b<=10 or r > 255 or g > 255 or b > 255 :
                    r = 14
                    g = 14
                    b = 225 
                color_node_.append(f'rgb({r},{g},{b})')
                color_line_.append(f'rgba({r},{g},{b},0.2)')
                r += 30
                g += 12
                b += -18
            color_node = color_node_
            color_line = color_line_
        else:
            color_node = 'Blue'
            color_line = None

        fig = go.Figure(
            data = [
                go.Sankey(node = dict(pad= 50,thickness= 10,line =dict(color = 'black',width=0.9),color = color_node , label = _label,),link = dict(source = _source,target = _target,value= _values,color=color_line))])
        fig.update_layout(title_text="Sankey Diagram", font_size=10,autosize=False,height = height, width= width)
        fig.write_html(f"Sankey_Code/{name}.html")


class Gantt_utils: # --------------------------------------- Functions to build the Gantt Chart

    def GET_ids_4_GANTT(XES_DF : pd.DataFrame , transformed_data: pd.DataFrame):

        subset_full_xes_df = XES_DF[['time:timestamp','concept:name','case:concept:name']]
        subset_full_xes_df['time:timestamp'] = pd.to_datetime(subset_full_xes_df['time:timestamp'],utc = True)
        subset_full_xes_df_grouped = subset_full_xes_df.groupby('case:concept:name')['time:timestamp'].agg(['min','max']).reset_index()
        subset_full_xes_df_grouped['time_elapsed'] = ( subset_full_xes_df_grouped['max'] - subset_full_xes_df_grouped['min']) / np.timedelta64(1,'s')
        subset_full_xes_df_grouped_merged = transformed_data[['ID_y','TRACE']].merge(subset_full_xes_df_grouped, how ='left', left_on='ID_y',right_on='case:concept:name').drop('case:concept:name',axis=1)
        subset_full_xes_df_grouped_merged_final = subset_full_xes_df_grouped_merged.groupby('TRACE')['time_elapsed'].agg(['min','mean','max']).reset_index()

        gantt_data = []

        for trace in subset_full_xes_df_grouped_merged_final['TRACE']:
            DF  = subset_full_xes_df_grouped_merged_final[subset_full_xes_df_grouped_merged_final['TRACE'] == trace]
            min_ = DF['min'].to_list()[0]
            mean_ = DF['mean'].to_list()[0]
            max_ = DF['max'].to_list()[0]
            
            DF_2 = subset_full_xes_df_grouped_merged[subset_full_xes_df_grouped_merged['TRACE'] == trace]
            min_id = DF_2.iloc[(DF_2['time_elapsed'] - min_).abs().argsort()[:1]]['ID_y'].to_list()[0]
            max_id = DF_2.iloc[(DF_2['time_elapsed'] - max_).abs().argsort()[:1]]['ID_y'].to_list()[0]
            mean_id = DF_2.iloc[(DF_2['time_elapsed'] - mean_).abs().argsort()[:1]]['ID_y'].to_list()[0]
            
            DF_3 = pd.DataFrame({'TRACE':[trace],'id_MIN':[min_id],'id_MAX':[max_id],'id_MEAN':[mean_id]})
            gantt_data.append(DF_3)

        gantt_data = pd.concat(gantt_data)
        return gantt_data

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
        


class nets:

    def get_base_node_df (xes_data : pm4py.objects.log.obj.EventLog):
        """
        The input is a heuristic net and returns 
        a dataframe with the source and destiny connections as well as 
        the label value , for this version is 
        the number of elements passig from one node to another.
        """
        
        heuristic_net = pm4py.discover_heuristics_net(xes_data)

        dataframes_ = []
        names_ = []
        node_occurances_ = []

        for node_name in heuristic_net.nodes:
            node = heuristic_net.nodes[node_name]
            name_ = (heuristic_net.nodes[node_name].node_name)
            node_occurance = heuristic_net.nodes[node_name].node_occ
            is_start_act = heuristic_net.nodes[node_name].is_start_activity
            #nodes_dict = heuristic_net.nodes[node_name].node_dictionary
            output_con = heuristic_net.nodes[node_name].output_connections
            names_.append(
                name_
            )
            node_occurances_.append(
                node_occurance
            )

            for other_node in output_con:
                source = []
                target = []
                arc_value = []
                depend_value = []

                for edge in node.output_connections[other_node]:
                    final_node_start_internal = edge.start_node.node_name
                    final_node_end_internal = edge.end_node.node_name
                    repr_value_ = edge.repr_value
                    _dependency_value = edge.dependency_value

                    source.append(final_node_start_internal)
                    target.append(final_node_end_internal)
                    arc_value.append(repr_value_)
                    depend_value.append(_dependency_value)
                
                df_internal = pd.DataFrame(
                    {
                        'Source':source,
                        'Target':target,
                        'arc_value':arc_value,
                        'depend_value':depend_value})
                df_internal['name_orig'] = name_
                dataframes_.append(df_internal)

        s_a = pm4py.get_start_activities(xes_data)
        e_a = pm4py.get_end_activities(xes_data)


        start_act_df = pd.DataFrame({
            'Source': ['Start'] * len(s_a),
            'Target': s_a.keys(),
            'arc_value': s_a.values(),
            'depend_value': [0.5] * len(s_a.keys()),
            'name_orig': ['Start'] * len(s_a.keys())  })
        
        end_act_df = pd.DataFrame({
            'Source': e_a.keys(),
            'Target': ['End'] *  len(e_a.keys()),
            'arc_value': e_a.values(),
            'depend_value': [0.5] * len(e_a.keys()),
            'name_orig': ['End'] * len(e_a.keys())  })

        final_df = pd.concat(dataframes_)
        final_df = pd.concat([start_act_df,final_df,end_act_df])
        final_df = final_df.reset_index(drop= True)

        return final_df

    def get_node_level_(node_info_df):
        """
        This function takes a pandas dataframe as argument conatining the node edges information
        Usually the output from the function get_base_node_df and returns a dataframe with the node and the level
        they need to placed in the Graphical element

        """

        node_info_df['NODE LEVEL'] = range(len(node_info_df))

        for source, num in zip(node_info_df['Source'].unique(),range(len(node_info_df['Source'].unique()))):
            dependents = node_info_df[node_info_df['Source'] == source]['Target'].to_list()
            dict_f = {source:dependents}
            for key, values in dict_f.items():
                for value in values:
                    node_info_df.loc[(node_info_df['Source'] == key) & (node_info_df['Target'] == value) , 'NODE LEVEL'] = num


        df_grouped = node_info_df.groupby(['Target'])['NODE LEVEL'].max().to_frame().reset_index()
        df_grouped_2 = node_info_df['Target'].drop_duplicates().to_frame().reset_index(drop=True)
        df_grouped_2['NEW LEVEL'] = range(1,len(df_grouped_2)+1)
        
        
        x_df_grouped = node_info_df.groupby(['Source'])['NODE LEVEL'].max().to_frame().reset_index()
        x_df_grouped_2 = node_info_df['Source'].drop_duplicates().to_frame().reset_index(drop=True)
        x_df_grouped_2['NEW LEVEL'] = range(1,len(x_df_grouped_2)+1)

        all = pd.concat([node_info_df['Source'],node_info_df['Target']]).to_frame().drop_duplicates().reset_index(drop=True)
        all.columns = ['Node']
        full = all.merge(df_grouped,how='left',left_on='Node',right_on='Target').merge(x_df_grouped,how = 'left', left_on= 'Node', right_on='Source')
        full = full.drop(full[full['Node'] =='Start'].index) 


        c = [] 
        for a,b in zip(full['NODE LEVEL_x'].fillna(0), full['NODE LEVEL_y'].fillna(0)):
            if a > b:
                c.append(a)
            else:
                c.append(b)
        full['c'] = c
        df_grouped = full[['Node','c']]
        df_grouped.columns=['Target', 'NODE LEVEL']    
            
        
        dfs = []
        for value in df_grouped['NODE LEVEL'].unique():
            _df_ = df_grouped[df_grouped['NODE LEVEL'] == value]
            _df_ = _df_.merge(
                df_grouped_2,
                how ='left',
                on = 'Target')
            _df_.loc[:,'NODE LEVEL'] = _df_['NEW LEVEL'].min()
            dfs.append(_df_)
        final_df = pd.concat(dfs).drop('NEW LEVEL',axis =1)
        final_df.columns = ['node_name','order']
        final_df = pd.concat([pd.DataFrame({'node_name':['Start'], 'order':[0]}),final_df])
        final_df = final_df.fillna(np.round(final_df['order'].mean(),0) +1)

        if final_df[final_df['node_name'] =='End']['order'].to_list()[0] != final_df['order'].max():
            final_df.loc[(final_df['node_name'] == 'End'),'order'] = final_df['order'].max() + 1


        return final_df

    def build_net( df_nodes,df_node_levels, name = 't', buttons = False, layout = True,height='600px', width ='100%'):
        
        if  not os.path.isdir('Network_Code'):
            os.makedirs("Network_Code")
        
        nt = Network(directed = True, layout= layout,height=height, width=width)
        for node,level in zip(df_node_levels['node_name'],df_node_levels['order']):
            nt.add_node(node, shape='box',label=node,level= level)
        for start,end,arc_value in zip(df_nodes['Source'],df_nodes['Target'],df_nodes['arc_value']):
            nt.add_edge(start,end,label=str(arc_value))    
        
        if buttons == True:
            nt.show_buttons(filter_=['physics'])

        nt.hrepulsion(
            node_distance=150,
            spring_strength =0)
        nt.prep_notebook()
        nt.show(f'Network_Code/{name}.html')

    def get_node_time_df(eventlog_filtered:pm4py.objects.log.obj.EventLog,aggregation ='mean'): 

        """
        Function to get the daataframe with the Source and atrget nodes with the time between Node
        ---------------------------------
        aggregation can be :
            - 'mean' : default which reflects the average amount of time from node to node
            - 'min'
            - 'max'
            - 'stdev'
            - 'sum'
        """
        D_F_G, START_ACTIVITIES, END_ACTIVITIES = pm4py.discover_performance_dfg(eventlog_filtered)
        #Body Data - - - - 
        frames_a1 = []
        for a,b in zip(D_F_G.keys(),D_F_G.values()):
            start = [a[0]]
            end = [a[1]]
            arc = utils_utils.human_time_duration(b[aggregation]).replace(' ','')
            if arc == '' or arc =='inf' :
                arc ='0sec'
            arc = [arc]
            frame = pd.DataFrame({'Source':start,'Target':end,'arc_value':arc})
            frames_a1.append(frame)
        #Start Data - - - -
        frames_a2 = []
        for a in START_ACTIVITIES.keys():
            start = ['Start']
            end = [a]
            arc = ['-']
            frame = pd.DataFrame({'Source':start,'Target':end,'arc_value':arc})
            frames_a2.append(frame)
        #End Data - - - - - 
        frames_a3 = []
        for a in END_ACTIVITIES.keys():
            start = [a]
            end = ['End']
            arc = ['-']
            frame = pd.DataFrame({'Source':start,'Target':end,'arc_value':arc})
            frames_a3.append(frame)

        final_df = pd.concat(
            [
                pd.concat(frames_a2),
                pd.concat(frames_a1),
                pd.concat(frames_a3)
                ]).reset_index(drop=True)

        final_df['depend_value'] = range(len(final_df))
        final_df['name_orig'] = final_df['Source']

        return final_df

    def build_performance_net(df_nodes,df_node_levels, name = 't', buttons = False, layout = False, height = '620px', width = '50%' ):

        if  not os.path.isdir('DFG_Code'):
            os.makedirs("DFG_Code")    
        nt = Network(directed = True, layout= layout, height=height, width=width)
        for node,level in zip(df_node_levels['node_name'],df_node_levels['order']):
            if node == 'Start' or node == 'End':
                nt.add_node(
                    node,
                    shape='diamond',
                    label=node,
                    level= level,
                    color='green', 
                    size=120)
            else:    
                nt.add_node(node, shape='box',label=node,level= level,color ='orange')
        for start,end,arc_value in zip(df_nodes['Source'],df_nodes['Target'],df_nodes['arc_value']):
            nt.add_edge(start,end,label=str(arc_value),color='orange')    
        
        if buttons == True:
            nt.show_buttons(filter_=['physics'])

        nt.force_atlas_2based(
            overlap=1,
            central_gravity=0,
            gravity=-68,
            spring_length=200,
            spring_strength=0.03,
            damping=1)

        nt.prep_notebook()
        nt.show(f"DFG_Code/{name}.html")


class build_progress:

    def get_visuals(xes_eventlog,x_width = '100%' ,x_height ='600px' , con = '', schema = '', name_sql_start = 'start_activities', name_sql_end = 'end_activities', s_height =800, s_width= 800 ):

        transformed_Data_0, transformed_Data_1 = transformation_utils.GET_TRANSFORMED_DATA_BIG(
            event_log=xes_eventlog)

        
        dfs_start = []
        dfs_end = []
        
        for complexity in range(0,101,1):

            FILTERED =  transformation_utils.GET_FILTERED_EVENTLOG(
                transformed_Data_1,
                complexity,
                xes_eventlog)
            
            NODE_BASE = nets.get_base_node_df(FILTERED[0])
            NODE_LEVELS = nets.get_node_level_(NODE_BASE)

            try:
                start_act = pm4py.get_start_activities(log = FILTERED[0])
                end_act = pm4py.get_end_activities(log=FILTERED[0])
            except:
                try:
                    start_act = pm4py.get_start_activities(log = FILTERED[0])
                    end_act = pm4py.get_end_activities(log=FILTERED[0])
                except:
                    print('Error Getting Start Activities ')
            keys_start = []
            values_start = []
            for keys, values in start_act.items():
                keys_start.append(keys)
                values_start.append(values)
            
            keys_end  = []
            values_end = []
            for keys, values in end_act.items():
                keys_end.append(keys)
                values_end.append(values)

            
            df_start_act = pd.DataFrame({'Activity':keys_start,'Number of Cases': values_start, 'complexity': [complexity] *len(keys_start)})
            df_end_act   = pd.DataFrame({'Activity':keys_end,'Number of Cases': values_end,'complexity': [complexity] * len(keys_end) })

            dfs_start.append(df_start_act)
            dfs_end.append(df_end_act)


            nets.build_net(
                df_nodes = NODE_BASE,
                df_node_levels= NODE_LEVELS,
                name = str(complexity),
                height= x_height,
                width=x_width
            )

            sankey_utils.get_sankey(name= str(complexity),nodes_base= NODE_BASE,height=s_height, width=s_width)

        
        dfs_start_final = pd.concat(dfs_start)
        dfs_end_final = pd.concat(dfs_end)
        try:
            dfs_start_final.to_sql(con = con,schema = schema,index =False,if_exists='replace',name = name_sql_start)
        except:
            try:
                dfs_start_final.to_sql(con = con,schema = schema,index =False,if_exists='replace',name = name_sql_start)
            except:
                pass
        try:
            dfs_end_final.to_sql(con=con,schema=schema,index =False,if_exists='replace',name = name_sql_end)
        except:
            try:
                dfs_end_final.to_sql(con=con,schema=schema,index =False,if_exists='replace',name = name_sql_end)
            except:
                pass
    
    def get_BPMNs(xes_eventlog, con = ''):

        transformed_Data_0, transformed_Data_1 = transformation_utils.GET_TRANSFORMED_DATA_BIG(event_log=xes_eventlog)
        if  not os.path.isdir('BPMNs'):
            os.makedirs("BPMNs")

        
        for complexity in range(0,101,1):
            #complexity_.append(complexity)
            FILTERED =  transformation_utils.GET_FILTERED_EVENTLOG(transformed_Data_1, complexity,  xes_eventlog)
            BPMN = pm4py.discover_bpmn_inductive(FILTERED[0])
            pm4py.save_vis_bpmn(bpmn_graph=BPMN, file_path = f'BPMNs/{complexity}.png')
            
            
            utils_utils.compress_img(image_name= f'BPMNs/{complexity}.png',new_size_ratio=1,quality=5,to_jpg=False)
            
            
            
            image = Image.open(f'BPMNs/{complexity}_compressed.png')
            buff = BytesIO()
            image.save(buff,format='png')
            bytes_image = buff.getvalue()

            df_bpmn = pd.DataFrame({'image': [bytes_image], 'complexity': [complexity]})

            if complexity == range(0,101,1)[0]:
                df_bpmn.to_sql(con= con, index = False, if_exists='replace',name="process_bpmn_images")
            else:
                df_bpmn.to_sql(con= con, index = False, if_exists='append',name="process_bpmn_images")
            os.remove(f'BPMNs/{complexity}.png')
            os.remove(f'BPMNs/{complexity}_compressed.png')


        os.removedirs('BPMNs')

    def get_additional_maps(xes_eventlog, con = ''):
           
        transformed_Data_0, transformed_Data_1 = transformation_utils.GET_TRANSFORMED_DATA_BIG(event_log=xes_eventlog)
        if  not os.path.isdir('Petri_Net_Inductive'):
            os.makedirs("Petri_Net_Inductive")
        if  not os.path.isdir('alpha_miner'):
            os.makedirs("alpha_miner")
        if  not os.path.isdir('alpha_plus_miner'):
            os.makedirs("alpha_plus_miner")
        
        bytes_images_alpha_plus = []
        bytes_images_alpha = []
        bytes_images_inductive = []
        complexity_level = []


        for complexity in range(0,101,1):
            complexity_level.append(complexity)
            
            FILTERED =  transformation_utils.GET_FILTERED_EVENTLOG(transformed_Data_1, complexity,  xes_eventlog)
            
            p_net_ind , ini, end = pm4py.discover_petri_net_inductive(FILTERED[0])
            pm4py.save_vis_petri_net(petri_net = p_net_ind, initial_marking=ini,final_marking=end,file_path=f"Petri_Net_Inductive/{complexity}.png")
            image_p_net_ind = Image.open(f"Petri_Net_Inductive/{complexity}.png")
            buff_p_net_ind = BytesIO()
            image_p_net_ind.save(buff_p_net_ind, format = "png")
            image_p_net_ind_bytes = buff_p_net_ind.getvalue()
            bytes_images_inductive.append(image_p_net_ind_bytes)
            os.remove(f"Petri_Net_Inductive/{complexity}.png")

            pnalpha, inialpha, finaalpha  = pm4py.discover_petri_net_alpha(FILTERED[0])
            pm4py.save_vis_petri_net(petri_net=pnalpha,initial_marking=inialpha,final_marking=finaalpha, file_path= f"alpha_miner/{complexity}.png")
            image_alpha = Image.open(f"alpha_miner/{complexity}.png")
            buff_alpha = BytesIO()
            image_alpha.save(buff_alpha,format= 'png')
            image_alpha_bytes = buff_alpha.getvalue()
            bytes_images_alpha.append(image_alpha_bytes)
            os.remove(f"alpha_miner/{complexity}.png")

            pnalphaplus, inialphaplus, finaalphaplus  = pm4py.discover_petri_net_alpha_plus(FILTERED[0])
            pm4py.save_vis_petri_net(petri_net=pnalphaplus,initial_marking=inialphaplus,final_marking=finaalphaplus, file_path= f"alpha_plus_miner/{complexity}.png")
            image_alpha_plus = Image.open(f"alpha_plus_miner/{complexity}.png")
            buff_alpha_plus = BytesIO()
            image_alpha_plus.save(buff_alpha_plus,format= 'png')
            image_alphaplus_bytes = buff_alpha_plus.getvalue()
            bytes_images_alpha_plus.append(image_alphaplus_bytes)
            os.remove(f"alpha_plus_miner/{complexity}.png")
        
        df_other_maps = pd.DataFrame(
            {
                'complexity' : complexity_level,
                'Petri_Net_Inductive': bytes_images_inductive,
                'Petri_Net_Alpha': bytes_images_alpha,
                'Petri_Net_Alpha_plus':bytes_images_alpha_plus  })
        
        df_other_maps.to_sql(con= con, schema= 'public', name ='additional_maps', if_exists='replace', index = False, chunksize=5)
        os.removedirs('Petri_Net_Inductive')
        os.removedirs('alpha_miner')
        os.removedirs('alpha_plus_miner')
        
    def get_visuals_DFG(xes_eventlog = None, x_height ='600px',aggregation_= 'mean', con= None,x_width="100%"):

        transformed_Data_0, transformed_Data_1 = transformation_utils.GET_TRANSFORMED_DATA_BIG(
            event_log=xes_eventlog)
        
        
        complexities = []
        dfs_with_time_peractivity_pair =  []
        dfs_time = []
        
        for complexity in range(0,101,1):
            #complexities.append(complexity)
            FILTERED =  transformation_utils.GET_FILTERED_EVENTLOG(
                transformed_Data_1,
                complexity,
                xes_eventlog)

            nodes_time_df = nets.get_node_time_df(eventlog_filtered=FILTERED[0],aggregation=aggregation_)
            nodes_levels_time_df = nets.get_node_level_(nodes_time_df)
            #dfs_with_time_peractivity_pair.append(pd.DataFrame(dict(pm4py.discover_performance_dfg(FILTERED[0])[0 ])).to_json())

            filtered_df = pm4py.convert_to_dataframe(FILTERED[0])
            try:
                filtered_df['time:timestamp'] =  pd.to_datetime(filtered_df['time:timestamp'],utc=True)
            except:
                pass

            days = (filtered_df['time:timestamp'].max()-filtered_df['time:timestamp'].min()).days
            _seconds = (filtered_df['time:timestamp'].max()-filtered_df['time:timestamp'].min()).seconds
            hours =  int(_seconds/3600)
            _minutes = (_seconds/3600) - hours
            minutes = int(_minutes * 60)
            time_head_ = pd.DataFrame({'min_time':[filtered_df['time:timestamp'].min()],'max_time':[filtered_df['time:timestamp'].max()],'days':[days],'hours':[hours],'minutes':[minutes]})
            time_head_ = time_head_.to_json() 
            #dfs_time.append(time_head_)

            df_final_timing = pd.DataFrame({
                'complexity': [complexity],
                'dfs_time': [time_head_],
                'dfs_time_pairs': [pd.DataFrame(dict(pm4py.discover_performance_dfg(FILTERED[0])[0 ])).to_json()]

            })

            if complexity == range(0,101,1)[0]:
                df_final_timing.to_sql(con = con, if_exists='replace',index=False,name= 'timing_visual', schema= 'public')
            else:
                df_final_timing.to_sql(con = con, if_exists='append',index=False,name= 'timing_visual', schema= 'public')
            
            
            
            nets.build_performance_net(
                df_nodes = nodes_time_df,
                df_node_levels = nodes_levels_time_df,
                name = str(complexity),
                height= x_height,
                width= x_width)
            

        
        #df_final_timing = pd.DataFrame(
        #    {
        #        'complexity' : complexities,
        #        'dfs_time' : dfs_time,
        #        'dfs_time_pairs' : dfs_with_time_peractivity_pair
        #        }
        #        )
        
        #df_final_timing.to_sql(con = con, if_exists='replace',index=False,name= 'timing_visual', schema= 'public')

    def buid_dataset_4_gantt(con= None, dataframe  =None, xes_eventlog =None):
            transformed_Data_0, transformed_Data_1 = transformation_utils.GET_TRANSFORMED_DATA_BIG(event_log=xes_eventlog)
            DATA_4_GANTT = Gantt_utils.GET_ids_4_GANTT(XES_DF=dataframe,transformed_data=transformed_Data_0)
            DATA_4_GANTT.to_sql(con=con,name = 'data_4_gantt',if_exists='replace',index =False,schema='public' )

        
    



