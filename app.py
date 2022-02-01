# This is app.py, this is the main file called.

from project import app 
from project.functions import create_master_df
import pandas as pd

if __name__ == '__main__':
    global master_df
    global master_df_flag
    master_df_flag = False
    master_df = create_master_df()
    app.run(debug=True)
