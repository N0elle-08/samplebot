'''
This function is responsible for handling user actions as per the given defined intents
'''
import requests
from hdbcli import dbapi
from hana_ml.dataframe import ConnectionContext
from hana_ml import dataframe as df
from settings.base import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_SCHEMA, setup_logger

logger = setup_logger()
class Actions:
    def __init__(self):
        pass

    def db_connection(self):
    # Connect to the SAP HANA database
        # Define your SAP HANA credentials
        
        cc = ConnectionContext(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)

        return cc
    
    def get_details(self, tab_name):
        """
        Fetch employee details from the connected database.
        """
        cc = self.db_connection()
        schema = DB_SCHEMA
        query = f"SELECT * FROM {schema}.{tab_name}"
        emp_df = df.DataFrame(cc, query)
        # Collect the result as a Pandas DataFrame
        emp_pandas_df = emp_df.collect()

         # Convert the Pandas DataFrame to a list of dictionaries
        result_dict = emp_pandas_df.to_dict(orient='records')

        logger.info(f"Retrieved data from {tab_name}")
        logger.info(result_dict)  # Log the result as a dictionary

        return result_dict 

        # table_format = emp_pandas_df.to_string(index=False)
        
        # logger.info(f"retrieved data from {tab_name}")
        # logger.info(table_format)
        # return table_format


