"""
Prism Project class

Table of Contents
- Imports
- Class definition
"""

###########
# Imports #
###########

# Prism-specific imports
from prism.mixins.sys_handler import SysHandlerMixin

# Standard library imports
from typing import Any, Dict


####################
# Class definition #
####################

class SysPathEngine(SysHandlerMixin):
    """
    Class for modifying the project's sys.path
    """

    def __init__(self,
        project,
        run_context: Dict[Any, Any]
    ):
        self.project = project
        self.run_context = run_context

        # Define base sys path and base sys modules
        temp_context: Dict[Any, Any] = {}
        exec('import sys', temp_context)
        self.base_sys_path = [p for p in temp_context['sys'].path]
        self.base_sys_modules = {
            k: v for k, v in temp_context['sys'].modules.items()
        }

    def modify_sys_path(self):
        """
        Modify the sys.path values for this project
        """
        # Configure sys.path
        self.add_paths_to_sys_path(self.project.sys_path_config, self.run_context)

        # Return run context
        return self.run_context

    def revert_to_base_sys_path(self, run_context: Dict[Any, Any]):
        """
        Remove project dir and all associated modules from sys path
        """
        run_context = self.remove_paths_from_sys_path(
            self.base_sys_path, self.project.sys_path_config, run_context
        )
        self.run_context = self.remove_project_modules(
            self.base_sys_modules, self.project.sys_path_config, run_context
        )

        # Return run context
        return self.run_context