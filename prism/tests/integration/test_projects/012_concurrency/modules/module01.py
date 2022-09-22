"""PRIVILEGED AND CONFIDENTIAL; FOR INTERNAL USE ONLY

In this script, we... 

--------------------------------------------------------------------------------
Table of Contents:
- Imports
- Class definition
    - Run
--------------------------------------------------------------------------------
"""

#############
## Imports ##
#############
import os
import time
import pandas as pd
import prism_project
from prism.task import PrismTask       # Not necessary; prism infrastructure automatically imported on the back-end
import prism.target as PrismTarget     # Not necessary; prism infrastructure automatically imported on the back-end

######################
## Class definition ##
######################

class Module01(PrismTask):

    ## Run
    @PrismTask.target(type=PrismTarget.PandasCsv, loc=os.path.join(prism_project.OUTPUT, 'module01.csv'), index=False)
    def run(self, tasks, hooks):
        """
        Execute task.

        args:
            tasks: used to reference output of other tasks --> tasks.ref('...')
            hooks: built-in Prism hooks. These include:
                - hooks.dbt_ref --> for getting dbt models as a pandas DataFrame
                - hooks.sql     --> for executing sql query using an adapter in profile.yml
                - hooks.spark   --> for accessing SparkSession (if pyspark specified in profile.yml)
        returns:
            task output
        """
        start_time = time.time()
        time.sleep(15)
        end_time = time.time()
        time_df = pd.DataFrame({
            'start_time': [start_time],
            'end_time': [end_time]
        })
        return time_df


# EOF