"""
Prism Module class

Table of Contents
- Imports
- Class definition
"""

#############
## Imports ##
#############

# Standard library imports
import argparse
from typing import Any, Dict

# Prism-specific imports
from prism.infra import project as prism_project
from prism.infra import executor as prism_executor
from prism.infra import psm
import prism.constants
import prism.exceptions
import prism.logging
from prism.mixins import sys_handler


######################
## Class definition ##
######################


class PrismPipeline(sys_handler.SysHandlerMixin):
    """
    Class for managing prism project components and scope
    """

    def __init__(self,
        project: prism_project.PrismProject,
        executor: prism_executor.DagExecutor,
        pipeline_globals: Dict[Any, Any]
    ):
        self.project = project
        self.dag_executor = executor
        self.pipeline_globals = pipeline_globals

        # Execute project
        self.project.exec(self.pipeline_globals)

        # The pipeline is being run using spark-submit, then the adapters must contain a pyspark adapter
        if self.project.which=='spark-submit':
            if 'pyspark' not in list(self.project.adapters_object_dict.keys()):
                raise prism.exceptions.RuntimeException(message='`spark-submit` command requires a `pyspark` adapter')
            
        # If the profile.yml contains a pyspark adapter, then the user should use the spark-submit command
        if 'pyspark' in list(self.project.adapters_object_dict.keys()):
            if self.project.which=='run':
                raise prism.exceptions.RuntimeException(message='`pyspark` adapter found in profile.yml, use `spark-submit` command')

        # Create PSM object
        psm_obj = psm.PrismFunctions(self.project, upstream={})
        
        # If PySpark adapter is specified in the profile, then explicitly add SparkSession to psm object
        if 'pyspark' in list(self.project.adapters_object_dict.keys()):
            pyspark_adapter = self.project.adapters_object_dict['pyspark']
            pyspark_alias = pyspark_adapter.get_alias()
            pyspark_spark_session = pyspark_adapter.engine
            setattr(psm_obj, pyspark_alias, pyspark_spark_session)

        self.pipeline_globals['psm'] = psm_obj
        
        # Create sys handler
        self.pipeline_globals = self.add_sys_path(self.project.project_dir, self.pipeline_globals)

        # Set the globals for the executor
        self.dag_executor.set_executor_globals(self.pipeline_globals)


    def exec(self, args: argparse.Namespace):
        executor_output = self.dag_executor.exec(args)
        
        # Close SQL adapter connections
        if "snowflake" in list(self.project.adapters_object_dict.keys()):
            self.project.adapters_object_dict["snowflake"].engine.close()
        if "redshift" in list(self.project.adapters_object_dict.keys()):
            self.project.adapters_object_dict["redshift"].engine.close()
        if "bigquery" in list(self.project.adapters_object_dict.keys()):
            self.project.adapters_object_dict["bigquery"].engine.close()
        
        # Remove project dir and all associated modules from sys path
        self.pipeline_globals = self.remove_sys_path(self.project.project_dir, self.pipeline_globals)
        self.pipeline_globals = self.remove_project_modules(self.project.project_dir, self.pipeline_globals)
        return executor_output



# EOF