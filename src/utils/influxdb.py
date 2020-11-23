"""
This module contains functions related to interactions with InfluxDB.
"""

import datetime as dt
from influxdb import DataFrameClient, InfluxDBClient
import logging
import pandas as pd


class InfluxDB:

    def __init__(self, host, port, user, password, dbname, ssl):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.ssl = True if ssl else False

        # Define DB and DataFrame clients
        self.database_client = InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname, self.ssl)
        self.dataframe_client = DataFrameClient(self.host, self.port, self.user, self.password, self.dbname, self.ssl)

    def create_database(self):
        try:
            if not any(self.dbname in item.get('name') for item in self.database_client.get_list_database()):
                self.database_client.create_database(self.dbname)
        except Exception as e:
            logging.error(f"Something happen when creating database. Reason {e}")

    def drop_database(self):
        try:
            self.database_client.drop_database(self.dbname)
        except Exception as e:
            logging.error(f"Something happen when dropping database. Reason {e}")

    def measurement_exists(self, measurement):

        result = self.read_query('show measurements')
        if result:
            measurements = [m[0] for m in result.raw['series'][0]['values']]
        else:
            return False

        return True if measurement in measurements else False

    def get_last_time_measurement(self, measurement):
        """
        Given a measurement name, get maximum time available

        Parameters
        ----------
        measurement: str
            Measurement name to check

        Returns
        -------
        str
            Datetime in string format meaning the last time available in the DB
        """

        query = f"SELECT * FROM {measurement} ORDER BY DESC LIMIT 1"
        raw = self.read_query(query)
        last_time = [p for p in raw.get_points()][0]['time']
        return dt.datetime.strptime(last_time, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')

    def get_min_time(self, measurement_name, group_by_col=None):
        """
        Check minimum available time from a specific measurement.
        If group_by_col is not None, the minimum time is checked for each group

        Parameters
        ----------
        measurement_name: str
            Name of the measurement
        group_by_col: str
            Column name for which to group by. Default, None

        Returns
        -------
        pd.DataFrame
            DataFrame with minimum time. If grouped, a row for each group is returned
        """

        query = f"select time, first(value) from {measurement_name}"
        if group_by_col is not None:
            query = f"{query} group by {group_by_col}"

        result = self.dataframe_client.query(query)

        if group_by_col is not None:
            vars_id = []
            min_times = []
            for x, df in result.items():
                try:
                    var_id = x[1][0][1]
                    timestamp = df.index.values[0]
                    vars_id = vars_id + [var_id]
                    min_times = min_times + [timestamp]
                except:  # TODO: Refine exception
                    continue
            result_df = pd.DataFrame({'variable_id': pd.to_numeric(vars_id), 'min_timestamp': min_times})
        else:
            min_time = result[measurement_name].index.values[0]
            result_df = pd.DataFrame({'min_timestamp': [min_time]})
        return result_df

    def load_dataframe(self, df, measurement, tags='', tag_columns=None, protocol='line'):
        """
        Write points to InfluxDB measurement with the corresponding tags from a DataFrame

        Parameters
        ----------
        df: pd.DataFrame
            Pandas DataFrame to load
        measurement: str
            Name of the measurement to load data in
        tags:
            Tags dictionary with the corresponding keys and values
        tag_columns:
            List of columns to use as tags
        protocol: str
            Whether 'json' or 'line'. Default, 'line'
        """

        client = self.dataframe_client

        # TODO: Add exception in case of failure
        client.write_points(df, measurement=measurement, protocol=protocol, tags=tags, tag_columns=tag_columns)
        n_rows = df.shape[0]
        logging.debug(f"DataFrame successfully loaded into InfluxDB. Number of rows loaded: {n_rows}")

    def load_json(self, json):
        """
        Write points to InfluxDB measurement with the corresponding tags from a DataFrame

        Parameters
        ----------
        json: pd.DataFrame
            JSON to load
        """

        client = self.database_client

        client.write_points(json)

        logging.debug("Json successfully loaded into InfluxDB")

    def read_measurement(self, measurement, limit=None):

        query = f'select * from "{measurement}"'

        if limit is not None:
            query = f"{query} limit {limit}"

        result = self.dataframe_client.query(query)

        return result[measurement]

    def read_measurement_between_dates(self, measurement, from_date, to_date, columns=None):

        columns_str = '*' if columns is None else ', '.join(columns)

        query = f"select {columns_str} from \"{measurement}\" where time >= '{from_date}' and time <= '{to_date}'"

        result = self.dataframe_client.query(query)

        return result[measurement]

    def read_query(self, query, client_str='database'):

        if client_str == 'database':
            return self.database_client.query(query)

        measurement = query.split(' ')[query.split(' ').index('from') + 1]

        return self.dataframe_client.query(query)[measurement]


def transform_dataframe_influx(df, cols, index_col=None):
    """
    Transform Pandas DataFrame accordingly to InfluxDB requirements

    Parameters
    ----------
    df: pd.DataFrame
        Pandas DataFrame to load
    cols: list of str
        List with the column names wanted to save into DB
    index_col: str
        Column name (mainly, a timestamp column) to be used as the time index column

    Returns
    -------
    pd.DataFrame
        DataFrame containing only wanted columns and indexed by one particular column
    """

    if index_col is None:
        index_col = cols[0]

    df_trans = df[cols]
    df_trans = df_trans.set_index(pd.DatetimeIndex(df_trans[index_col]))
    df_trans = df_trans.drop([index_col], axis=1)
    return df_trans
