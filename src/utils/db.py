import duckdb
import pandas as pd
from typing import Optional

def query_duckdb(df: pd.DataFrame, sql_query: str) -> Optional[pd.DataFrame]:
    """
    Registers DataFrame as DuckDB view 'retail_data' and executes analytical SQL query.
    Returns resulting DataFrame or None if query fails.
    """
    if df.empty:
        return None

    try:
        con = duckdb.connect(database=':memory:')
        con.register('retail_data', df)
        result_df = con.execute(sql_query).df()
        con.close()
        return result_df
    except Exception as e:
        print(f"DuckDB SQL Execution Error: {str(e)}")
        return None
