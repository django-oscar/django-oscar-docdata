import traceback
import sys
from django.core.exceptions import ImproperlyConfigured


def import_class(import_path, setting_name=None):
    """
    Import a class by name.
    """
    mod_name, class_name = import_path.rsplit('.', 1)

    # import module
    mod = _import_module(mod_name, classnames=(class_name,))
    if mod is not None:
        # Loaded module, get attribute
        try:
            return getattr(mod, class_name)
        except AttributeError:
            pass

    # For ImportError and AttributeError, raise the same exception.
    if setting_name:
        raise ImproperlyConfigured("{0} does not point to an existing class: {1}".format(setting_name, import_path))
    else:
        raise ImproperlyConfigured("Class not found: {0}".format(import_path))


# Based on code from django-oscar:
def _import_module(module_label, classnames=()):
    """
    Imports the module with the given name.
    Returns None if the module doesn't exist, but propagates any import errors.
    """
    try:
        return __import__(module_label, fromlist=classnames)
    except ImportError:
        # There are 2 reasons why there could be an ImportError:
        #
        #  1. Module does not exist. In that case, we ignore the import and return None
        #  2. Module exists but another ImportError occurred when trying to import the module.
        #     In that case, it is important to propagate the error.
        #
        # ImportError does not provide easy way to distinguish those two cases.
        # Fortunately, the traceback of the ImportError starts at __import__
        # statement. If the traceback has more than one frame, it means that
        # application was found and ImportError originates within the local app
        __, __, exc_traceback = sys.exc_info()
        frames = traceback.extract_tb(exc_traceback)
        if len(frames) > 1:
            raise
    return None
