"""
Class for parsing Python ASTs.

Table of Contents:
- Imports
- Class definition
"""


###########
# Imports #
###########

# Standard library imports
import re
import ast
import astor
from pathlib import Path
from typing import List, Optional, Tuple, Union

# Prism imports
import prism.constants
import prism.exceptions
from prism.infra.manifest import ModuleManifest


####################
# Class definition #
####################

# Constant
prism_task_manager_alias = 'tasks'
prism_hooks_alias = 'hooks'


class AstParser:
    """
    Class for converting module into AST and parsing the resulting tree
    """

    def __init__(self,
        module_relative_path: Path,
        parent_path: Path
    ):
        self.module_relative_path = module_relative_path
        self.parent_path = parent_path

        # Create a module manifest
        self.module_manifest = ModuleManifest()

        # Extract module as a string and parse
        self.module_path = Path(self.parent_path / self.module_relative_path)
        with open(self.module_path, 'r') as f:
            self.module_str = f.read()
        f.close()
        self.ast_module = ast.parse(self.module_str)

        # Add module source code to manifest
        self.module_manifest.add_module(self.module_relative_path)

        # Check existence of if-name-main
        bool_if_name_main = self.check_if_name_main(self.ast_module)
        if bool_if_name_main:
            msg = f'found `if __name__ == "__main__"` in `{str(self.module_relative_path)}`; all task-specific code should be placed in `run` method'  # noqa: E501
            raise prism.exceptions.ParserException(message=msg)

        # Get classes and bases
        self.classes, self.bases = self.get_classes_bases(self.ast_module)

    def get_classes_bases(self,
        module: ast.Module
    ) -> Tuple[List[ast.ClassDef], List[List[ast.expr]]]:
        """
        Get the classes ans associated bases

        args:
            module: module represented as an AST node
        returns:
            list of classes and associated bases
        """
        classes = [n for n in module.body if isinstance(n, ast.ClassDef)]
        class_bases = [class_.bases for class_ in classes]
        return classes, class_bases

    def get_num_prism_tasks(self,
        bases: List[List[ast.expr]]
    ) -> int:
        """
        Get number of PrismTasks from `bases`

        args:
            bases: list of bases associated with classes in module
        returns:
            number of PrismTasks
        """
        prism_tasks = 0
        for base_ in bases:
            for obj in base_:
                if isinstance(obj, ast.Name):
                    if obj.id == "PrismTask":
                        prism_tasks += 1
                elif isinstance(obj, ast.Attribute):
                    if obj.attr == "PrismTask":
                        prism_tasks += 1
        return prism_tasks

    def get_prism_task_node(self,
        classes: List[ast.ClassDef],
        bases: List[List[ast.expr]]
    ) -> Optional[ast.ClassDef]:
        """
        Get the node associated with the prism task from `module`

        args:
            module: module represented as an AST node
        returns:
            node associated with prism task
        """
        # If there are no bases, then there are no class definitions. Throw an error
        if len(bases) == 0:
            return None
        for class_, base_ in zip(classes, bases):
            for obj in base_:
                if isinstance(obj, ast.Name):
                    if obj.id == "PrismTask":
                        return class_
                elif isinstance(obj, ast.Attribute):
                    if obj.attr == "PrismTask":
                        return class_
        return None

    def get_all_funcs(self, prism_task: ast.ClassDef) -> List[ast.FunctionDef]:
        """
        Get all functions from PrismTask class

        args:
            prism_task: PrismTask class as an AST class
        returns:
            run function as an ast.FunctionDef
        """
        return [f for f in prism_task.body if isinstance(f, ast.FunctionDef)]

    def get_run_func(self, prism_task: ast.ClassDef) -> Optional[ast.FunctionDef]:
        """
        Get `run` function from PrismTask class

        args:
            prism_task: PrismTask class as an AST class
        returns:
            run function as an ast.FunctionDef
        """
        functions = [f for f in prism_task.body if isinstance(f, ast.FunctionDef)]
        for func in functions:
            if func.name == "run":
                return func
        return None

    def get_func_args(self, func: ast.FunctionDef) -> List[str]:
        """
        Get arguments of `func` as a list of strings

        args:
            func: function for which to retrieve arguments
        returns:
            arguments of `func` as a list of strings
        """
        results = []
        args_list = func.args.args
        for a in args_list:
            results.append(a.arg)
        return results

    def get_prism_mod_calls(self, func: ast.FunctionDef) -> List[Path]:
        """
        Get calls to `tasks.ref` from `func`

        args:
            func: run function represented as an ast.FunctionDef object
        returns:
            calls to prism.mod contained within function
        """
        mod_calls = []

        # Get all function calls
        call_objs = []
        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                call_objs.append(node)

        # Iterate through function calls
        for c in call_objs:
            if not isinstance(c.func, ast.Attribute):
                continue
            else:
                try:
                    if c.func.value.id == prism_task_manager_alias and c.func.attr == 'ref':  # type: ignore # noqa: E501
                        args = c.args
                        if len(args) > 1:
                            raise prism.exceptions.ParserException(
                                'too many arguments in `tasks.ref()` call'
                            )
                        if Path(args[0].s) not in mod_calls:                 # type: ignore # noqa: E501
                            if args[0].s == str(self.module_relative_path):  # type: ignore # noqa: E501
                                raise prism.exceptions.ParserException(
                                    message=f'self-references found in `{str(self.module_relative_path)}`'  # noqa: E501
                                )
                            mod_calls.append(Path(args[0].s))  # type: ignore

                # If we encounter an Attribute error, then the call object producing the
                # error is not of interest to us. Skip.
                except AttributeError:
                    pass

        return mod_calls

    def check_if_name_main(self,
        ast_module: ast.Module
    ) -> bool:
        """
        Check if `ast_module` has an if __name__ == "__main__" block.

        args:
            ast_module: module represented as an AST
        returns:
            boolean indicating if `ast_module` has an if __name__ == "__main__" block
        """
        # TODO: optimize function by removing duplicate DFS searches via ast.walk

        # If-name-main block needs to appear in main body
        if_name_main_blocks = [c for c in ast_module.body if isinstance(c, ast.If)]
        for node in if_name_main_blocks:
            compares = []
            for nested_node in ast.walk(node):
                if isinstance(nested_node, ast.Compare):
                    compares.append(nested_node)

            # For each compare object, iterate through all sub-nodes and examine if
            # there is a Name object with id __name__ and a string object with s
            # "__main__".
            for comp in compares:
                has_name = 0
                has_main = 0
                for comp_subnode in ast.walk(comp):
                    if isinstance(comp_subnode, ast.Name) \
                            and comp_subnode.id == "__name__":
                        has_name = 1
                    if isinstance(comp_subnode, ast.Str) \
                            and comp_subnode.s == "__main__":
                        has_main = 1

                if max(has_name, has_main) == 1:
                    return True
        return False

    def get_targets(self, run_func: ast.FunctionDef) -> Union[str, List[str]]:
        """
        Get targets as strings

        args:
            run_function: run function as an ast FunctionDef object
        returns:
            targets as strings (or a list of strings)
        """

        # Targets will always be decorators
        decs = run_func.decorator_list
        target_decs = []
        for call in decs:
            if not isinstance(call, ast.Call):
                raise prism.exceptions.CompileException(
                    message="invalid target declaration"
                )
            if isinstance(call.func, ast.Attribute):
                if call.func.attr in ["target", "target_iterator"]:
                    target_decs.append(call)
            elif isinstance(call.func, ast.Name):
                if call.func.id in ["target", "target_iterator"]:
                    target_decs.append(call)

        # Iterate through target decorators and pull out the loc keyword
        locs: List[str] = []
        for targ_call in target_decs:
            kws = targ_call.keywords
            for kw in kws:
                if kw.arg == "loc":

                    # Python introduced ast.unparse in version 3.9, which reverses
                    # ast.parse and converts a node back into string. mypy thinks ast
                    #  doesn't have an unparse method, but this is fine.
                    python_greater_than_39 = prism.constants.PYTHON_VERSION.major == 3 and prism.constants.PYTHON_VERSION.minor >= 9  # noqa: E501
                    if prism.constants.PYTHON_VERSION.major > 3 \
                            or python_greater_than_39:
                        locs.append(ast.unparse(kw.value))  # type: ignore

                    # Otherwise, use the astor library. This is compatible with Python
                    # >=3.5
                    else:
                        locs.append(re.sub('\n$', '', astor.to_source(kw.value)))

        if len(locs) == 1:
            return locs[0]
        else:
            return locs

    def parse(self) -> Union[List[Path], Path]:
        """
        Parse module and return mod references
        """
        # This will throw an error if the number of PrismTasks!=1
        num_prism_task_classes = self.get_num_prism_tasks(self.bases)
        if num_prism_task_classes == 0:
            raise prism.exceptions.ParserException(
                message=f"no PrismTask in `{str(self.module_relative_path)}`"
            )
        elif num_prism_task_classes > 1:
            raise prism.exceptions.ParserException(
                message=f"too many PrismTasks in `{str(self.module_relative_path)}`"
            )

        # Get PrismTask, run function, and mod calls
        prism_task_class_node = self.get_prism_task_node(self.classes, self.bases)
        if prism_task_class_node is None:
            raise prism.exceptions.ParserException(
                message=f"no PrismTask in `{str(self.module_relative_path)}`"
            )

        # Confirm run function is properly structured
        run_func = self.get_run_func(prism_task_class_node)
        if run_func is None:
            raise prism.exceptions.ParserException(
                message=f"no `run` function in PrismTask in `{str(self.module_relative_path)}`"  # noqa: E501
            )
        run_args = self.get_func_args(run_func)
        if sorted(run_args) != sorted([prism_task_manager_alias, prism_hooks_alias, 'self']):  # noqa: E501
            msg = f'invalid arguments in `run` function in PrismTask in {str(self.module_relative_path)}; should only be "self", "{prism_task_manager_alias}", and "{prism_hooks_alias}"'  # noqa: E501
            raise prism.exceptions.ParserException(message=msg)

        # Parse targets
        target_locs = self.get_targets(run_func)
        self.module_manifest.add_target(self.module_relative_path, target_locs)

        # Iterate through all functions and get prism task.ref calls
        all_funcs = self.get_all_funcs(prism_task_class_node)
        all_task_refs: List[Path] = []
        for func in all_funcs:
            all_task_refs += self.get_prism_mod_calls(func)
        if len(all_task_refs) == 1:
            self.module_manifest.add_ref(
                target=self.module_relative_path, source=all_task_refs[0]
            )
            return all_task_refs[0]
        else:
            for mr in all_task_refs:
                self.module_manifest.add_ref(
                    target=self.module_relative_path, source=mr
                )
            return all_task_refs

    def get_variable_assignments(self, node, var_name: str):
        """
        Get `var_name` assignment from the Prism task. This can be used to assess the
        number of retries and the retry delay seconds.

        args:
            node: parent node
            var_name: variable name
        returns:
            assigned value of variable
        """
        # If the inputted node is an ast.Assign object, then the function is executing
        # one of its recursive calls. In this case, walk through the assign object and
        # find the names / constants.
        if isinstance(node, ast.Assign):

            # We eventually want to find names and constants. The order of the names
            # should exactly match the order of the constants. E.g., if the user says
            # VAR1, VAR2 = 30, 60, then the first name object will be VAR1 and the first
            # constant object will be 30.
            names = []
            constants = []
            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.Name):
                    names.append(sub_node.id)
                if isinstance(sub_node, ast.Constant):
                    constants.append(sub_node.value)

            # Get the var name
            for n, c in zip(names, constants):
                if n == var_name:
                    return c

            # If nothing has been returned, return None

        # Assume that the var name is an ast.Assign object. If it isn't, then it isn't a
        # variable assignment, it's something else.
        else:
            assigns = []
            for node in ast.walk(node):
                if isinstance(node, ast.Assign):
                    assigns.append(node)

            # Iterate through assign objects
            val = None
            for ast_assign in assigns:
                new_val = self.get_variable_assignments(ast_assign, var_name)
                if new_val is not None:
                    val = new_val

            # Return val. This will return None if the var name is found, and it will
            # return the last value for var name if it is defined multiple times.
            return val
