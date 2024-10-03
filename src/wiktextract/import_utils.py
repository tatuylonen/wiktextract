import importlib
import importlib.util
import types


def import_extractor_module(
    lang_code: str, module_name: str
) -> types.ModuleType | None:
    try:
        full_module_name = f"wiktextract.extractor.{lang_code}.{module_name}"
        if importlib.util.find_spec(full_module_name) is not None:
            return importlib.import_module(full_module_name)
    except ModuleNotFoundError:
        return None
    return None
