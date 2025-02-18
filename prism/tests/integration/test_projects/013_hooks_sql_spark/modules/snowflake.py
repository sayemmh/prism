###########
# Imports #
###########

# Prism infrastructure imports
import prism.task
import prism.target
import prism.decorators

# Prism project imports
import prism_project

# Other imports
import time
import pandas as pd


######################
## Class definition ##
######################

class SnowflakeTask(prism.task.PrismTask):

    ## Run
    @prism.decorators.target(type=prism.target.PandasCsv, loc=prism_project.OUTPUT / 'machinery_sample.csv', index=False)
    @prism.decorators.target(type=prism.target.PandasCsv, loc=prism_project.OUTPUT / 'household_sample.csv', index=False)
    def run(self, tasks, hooks):
        """
        Execute task.

        args:
            tasks: used to reference output of other tasks --> tasks.ref('...')
            hooks: built-in Prism hooks. These include:
                - hooks.dbt_ref --> for getting dbt models as a pandas DataFrame
                - hooks.sql     --> for executing sql query using an adapter in profile YML
                - hooks.spark   --> for accessing SparkSession (if pyspark specified in profile YML)
        returns:
            task output
        """
        machinery_sql = f"""
        SELECT
            *
        FROM "SNOWFLAKE_SAMPLE_DATA"."TPCH_SF1"."CUSTOMER"
        WHERE
            c_mktsegment = 'MACHINERY'
        ORDER BY
            c_custkey
        LIMIT 50
        """
        machinery_df = hooks.sql(adapter_name="snowflake_base", query=machinery_sql)

        household_sql = f"""
        SELECT
            *
        FROM "SNOWFLAKE_SAMPLE_DATA"."TPCH_SF1"."CUSTOMER"
        WHERE
            c_mktsegment = 'HOUSEHOLD'
        ORDER BY
            c_custkey
        LIMIT 50
        """
        household_df = hooks.sql(adapter_name="snowflake_base", query=household_sql)

        return machinery_df, household_df


# EOF