"""
Mixin classes for each task

Table of Contents
- Imports
- Class definition
"""


###########
# Imports #
###########

# Standard library imports
import argparse
from typing import Any, Dict
from pathlib import Path

# Prism-specific imports
from prism.infra import project as prism_project
from prism.infra import pipeline as prism_pipeline
from prism.infra import executor as prism_executor


####################
# Class definition #
####################

class RunMixin():
    """
    Mixin for connect task
    """

    def parse_functions(self):
        return None

    def get_profile_path(self,
        args: argparse.Namespace,
        project_dir: Path
    ) -> Path:
        """
        Get profile.yml path from args

        args:
            args: user arguments
            project_dir: project directory
        returns:
            profiles_path: path to profile.yml
        """
        if args.profiles_dir is not None:
            profile_dir = Path(args.profiles_dir)
        else:
            profile_dir = project_dir
        profiles_path = profile_dir / 'profile.yml'
        return profiles_path

    def create_project(self,
        project_dir: Path,
        profiles_path: Path,
        env: str,
        which: str
    ) -> prism_project.PrismProject:
        """
        Wrapper for creation of PrismPipeline object. Needed in order to be compatible
        with event manager.

        args:
            code: str or code object to run
            globals_dict: globals dictionary
        returns:
            PrismPipeline object
        """
        project = prism_project.PrismProject(project_dir, profiles_path, env, which)
        project.setup()
        return project

    def create_pipeline(self,
        project: prism_project.PrismProject,
        dag_executor: prism_executor.DagExecutor,
        pipeline_globals: Dict[Any, Any]
    ) -> prism_pipeline.PrismPipeline:
        """
        Wrapper for creation of PrismPipeline object. Needed in order to be compatible
        with event manager.

        args:
            code: str or code object to run
            globals_dict: globals dictionary
        returns:
            PrismPipeline object
        """
        pipeline = prism_pipeline.PrismPipeline(
            project, dag_executor, pipeline_globals
        )
        return pipeline
