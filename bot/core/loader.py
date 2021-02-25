import importlib
import inspect
import pkgutil
import types
import typing as t

from loguru import logger

from bot import cogs, databases


def get_module_name(name: str) -> str:
    return name.split(".")[-1]


def is_a_cog(module: types.ModuleType) -> bool:
    imported = importlib.import_module(module.name)
    return inspect.isfunction(getattr(imported, "setup", None))


def get_modules_list(
    package: types.ModuleType, check: t.Optional[types.FunctionType] = None
) -> t.List[str]:
    modules = []

    for submodule in pkgutil.walk_packages(package.__path__, f"{package.__name__}."):
        if get_module_name(submodule.name).startswith("_"):
            continue

        if check and not check(submodule):
            continue

        modules.append(submodule.name)

    return modules


COGS = get_modules_list(cogs, check=is_a_cog)
DATABASES = get_modules_list(databases)
