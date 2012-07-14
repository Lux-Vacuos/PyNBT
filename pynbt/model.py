# -*- coding: utf8 -*-
import inspect
import pprint

from pynbt import nbt


class ModelError(Exception):
    pass


class NBTField(object):
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self.value = kwargs.get('default')

    def _copy(self):
        return self.__class__(**self._kwargs)

    def __str__(self):
        return str(self.value)

    @property
    def name(self):
        return self._kwargs.get('name', None)

    @name.setter
    def name(self, value):
        self._kwargs['name'] = value

    @property
    def optional(self):
        return self._kwargs.get('optional', False)

    @optional.setter
    def optional(self, value):
        self._kwargs['optional'] = value

    @property
    def value(self):
        return self._kwargs.get('value', None)

    @value.setter
    def value(self, value):
        self._kwargs['value'] = value


class ByteField(NBTField):
    _TAG = nbt.TAG_Byte


class ShortField(NBTField):
    _TAG = nbt.TAG_Short


class IntegerField(NBTField):
    _TAG = nbt.TAG_Int


class FloatField(NBTField):
    _TAG = nbt.TAG_Float


class LongField(NBTField):
    _TAG = nbt.TAG_Long


class DoubleField(NBTField):
    _TAG = nbt.TAG_Double


class StringField(NBTField):
    _TAG = nbt.TAG_String


class NBTModel(object):
    def __init__(self, compound=None):
        """
        A thin "schema" layer above PyNBT.
        """
        # Find every NBTField sublcass on our model definition.
        members = inspect.getmembers(self.__class__)
        fields = dict((k, v) for k, v in members if isinstance(v, NBTField))

        for field_name, field in fields.items():
            local_field = field._copy()
            setattr(self, field_name, local_field)

            # If there was no explicit name, use our assignment name.
            if local_field.name is None:
                local_field.name = field_name

            if compound is not None:
                # Load the field from the compound.
                field_value = compound.get(local_field.name, None)

                # Fields are required by default.
                if field_value is None and not local_field.optional:
                    raise ModelError('{0} is not optional'.format(
                        local_field.name))

                # We can discard the TAG object since we contain the type
                # information anyways.
                local_field.value = field_value.value

    def save(self, compound):
        members = inspect.getmembers(self)
        fields = dict((k, v) for k, v in members if isinstance(v, NBTField))

        for field_name, field in fields.items():
            compound[field.name] = field._TAG(field.value)
