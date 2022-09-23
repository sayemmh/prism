#############
## Imports ##
#############

# Prism infrastructure imports
import prism.task
import prism.target
import prism.decorators

# Prism project imports
import prism_project


######################
## Class definition ##
######################

class Module02(prism.task.PrismTask):
    
    ## Run
    @prism.decorators.target(type=prism.target.Txt, loc=prism_project.OUTPUT / 'module02.txt')
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
        with open(tasks.ref('extract/module01.py'), 'r') as f:
            lines = f.read()
        f.close()
        return lines + "\n" + "Hello from module 2!"


# EOF