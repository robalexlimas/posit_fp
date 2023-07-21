from typing import _GenericAlias


from sfpy.posit import Posit16, Posit32, Quire32
from sfpy.float import Float16, Float32


def get_custom_format(format):
    if format == 'posit16':
        CustomData: _GenericAlias = Posit16
    elif format == 'posit32':
        CustomData: _GenericAlias = Posit32
    elif format == 'float16':
        CustomData: _GenericAlias = Float16
    elif format == 'float32':
        CustomData: _GenericAlias = Float32
    else:
        CustomData: _GenericAlias = Quire32
    return CustomData
