from google.adk.tools.bigquery.bigquery_toolset import BigQueryToolset

from .credentials import credentials_config

bigquery_toolset = BigQueryToolset(credentials_config=credentials_config, tool_filter=[
    'list_dataset_ids',
    'get_dataset_info',
    'list_table_ids',
    'get_table_info',
    'execute_sql',
])
