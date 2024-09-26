'''
This function is responsible for handling user actions as per the given defined intents
'''
import requests
from hdbcli import dbapi
from hana_ml.dataframe import ConnectionContext
from hana_ml import dataframe as df
from settings.base import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_SCHEMA

class Actions:
    def __init__(self):
        pass

    def db_connection(self):
    # Connect to the SAP HANA database
        # Define your SAP HANA credentials
        
        cc = ConnectionContext(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)

        return cc
    
    def get_employee_details(self):
        """
        Fetch employee details from the connected database.
        """
        cc = self.db_connection()
        schema = DB_SCHEMA
        query = f"SELECT * FROM {schema}.COS_EMPINFO"
        emp_df = df.DataFrame(cc, query)
        # Collect the result as a Pandas DataFrame
        emp_pandas_df = emp_df.collect()

        table_format = emp_pandas_df.to_string(index=False)

        return table_format


