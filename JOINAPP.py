import pm4py
import __CALCULATION_FUNCTIONS
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import tkinter as tk

from tkinter import filedialog


def validate_login(user_val,password_val,ip_val,port_val):
    engine = create_engine(f"postgresql://{user_val}:{password_val}@{ip_val}:{port_val}/root")
    try:
        engine.connect()
        pop_success = tk.Toplevel(root)
        pop_success.geometry("500x500")
        pop_success.title('Message Success')
        tk.Label(pop_success, text= 'Connection Ok').place(x=150,y=80)
        return engine, 'ok'

    except:
        pop_Failed = tk.Toplevel(root)
        pop_Failed.geometry("500x500")
        pop_Failed.title('Message Failed')
        tk.Label(pop_Failed, text= 'Connection Failed , Review databse Login Credentials').place(x=150,y=80)

def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",title = "Select a File", filetypes = (
        ("Text files","*.txt*"),("all files","*.*")))
    return filename

def read_data(path):
    xes_data_ = pm4py.read_xes(path)
    print('data read')
    xes_data_df = pm4py.convert_to_dataframe(xes_data_)
    xes_data_df['time:timestamp'] = pd.to_datetime(xes_data_df['time:timestamp'], utc=True)
    print('data converted to table, date converted ')
    return xes_data_ , xes_data_df

def load_eventlog_df(xes_data_df, engine = None):
    xes_data_df.to_sql(con=engine,schema='public',index =False,if_exists='replace',name='eventlog_df',chunksize=6000)
    print('eventlog_df: loaded ')

def filtered_data_load(engine = None, xes_data_df = None, xes_data_= None):
    overview_data_filter_header_info = __CALCULATION_FUNCTIONS.utils_utils.get_df_overview_summary_header(eventlog_dataframe = xes_data_df,evntlog = xes_data_)
    overview_data_filter_header_info.to_sql(con=engine, if_exists ='replace',index = False,name='overview_header',schema ='public')
    print('Overveiw Header: Loaded')

def load_variants(engine = None, xes_data_ = None):
    varinats_info_Data_0,varinats_info_Data_1 = __CALCULATION_FUNCTIONS.transformation_utils.GET_TRANSFORMED_DATA_BIG(xes_data_)
    varinats_info_Data_1.to_sql(con=engine,schema ='public',if_exists='replace',index=False,name ='variants_info')
    varinats_info_Data_0.to_sql(con=engine,schema ='public',if_exists='replace',index=False,name ='variants_info_percase')
    print('Data Variants: Loaded')

def nets_sankeys(engine = None,xes_data_=None ):
    __CALCULATION_FUNCTIONS.build_progress.get_visuals(xes_eventlog = xes_data_,con=engine,schema ='public', x_height = "800px",s_height = 500, s_width = 1400  )
    print('Nets & Sankeys Created -')

def BPMNs_ (engine = None, xes_data_ = None):
    __CALCULATION_FUNCTIONS.build_progress.get_BPMNs(xes_eventlog = xes_data_, con = engine)
    print('BPMNs Created')

def additional_maps_(engine= None, xes_data_=None):
    __CALCULATION_FUNCTIONS.build_progress.get_additional_maps(xes_eventlog = xes_data_, con= engine )
    print('Additional Maps Created')

def dfg_vis_data(engine=None, xes_data_ = None):
    __CALCULATION_FUNCTIONS.build_progress.get_visuals_DFG(xes_eventlog = xes_data_,aggregation_ ='mean',x_height = "800px",con= engine,x_width="100%")
    print('DFG_CREATED')

def gantt__(engine = None, xes_data_df= None, xes_data_= None):
    __CALCULATION_FUNCTIONS.build_progress.buid_dataset_4_gantt(con= engine,dataframe= xes_data_df,xes_eventlog = xes_data_)
    print('data_4_gantt_loaded')


def Do_job():
    login = validate_login(user_val = user.get(), password_val=password.get(),ip_val=ip.get(),port_val=port.get())
    if login[1] == 'ok':
        path = browseFiles()
        xes_data_ , xes_data_df = read_data(path = path)
        load_eventlog_df(xes_data_df = xes_data_df, engine = login[0])
        filtered_data_load(engine=login[0],xes_data_ = xes_data_, xes_data_df= xes_data_df)
        load_variants(engine= login[0],xes_data_= xes_data_)
        nets_sankeys(engine = login[0],xes_data_=xes_data_)
        BPMNs_(engine=login[0],xes_data_ = xes_data_)
        dfg_vis_data(engine=login[0],xes_data_=xes_data_)
        gantt__(engine= login[0], xes_data_ = xes_data_, xes_data_df = xes_data_df)





root = tk.Tk()
root.title("Enter Values for Database Connection")
root.geometry("500x500")


user = tk.Entry(root)
password = tk.Entry(root)
ip = tk.Entry(root)
port = tk.Entry(root)
Label_user = tk.Label(root,text ='Enter User')
Label_pass_word = tk.Label(root,text ='Enter data')
Label_ip = tk.Label(root,text ='Enter ip')
Label_port =  tk.Label(root,text ='Enter Root')


Label_user.pack()
user.pack()
Label_pass_word.pack()
password.pack()
Label_ip.pack()
ip.pack()
Label_port.pack()
port.pack()


button = tk.Button(root, text="Run Script", command=Do_job).pack()
root.mainloop()