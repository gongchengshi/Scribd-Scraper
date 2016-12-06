import sys
import logging
import os
import urllib2
import xmlparse
import re
import codecs

class Resource(object):
    """Base class for remote objects that the Scribd API allows
    to interact with.
    
    This class is never instantiated, only subclassed.
    
    Every object features a set of resource attributes that are
    stored and managed by the Scribd platform. They are accessed
    and used like any other Python object attributes but are
    stored in a separate container.
    """

    def __init__(self, xml=None):
        # Instantiates an object of the class.
        #
        # If "xml" is not None, it is a xmlparse.Element object whose
        # subelements are to be converted to this object's resource
        # attributes.

        self._attributes = {} # Attributes as loaded from the XML.
        self._set_attributes = {} # Attributes set externally.

        # Create a list of instance variables. All variables used by
        # the object during its lifetime have to be setup at this point.
        # This is used to distinguish between instance variables and
        # the resource attributes.
        self._instance_vars_names = self.__dict__.keys()

        if xml is not None:
            self._load_attributes(xml)
            
    def get_attributes(self):
        """Returns a dictionary with the resource attributes."""
        attrs = self._attributes.copy()
        attrs.update(self._set_attributes)
        return attrs
        
    def _load_attributes(self, xml):
        """Adds resource attributes to this object based on XML
        response from the HOST.
        """
        for element in xml:
            text = element.text
            if text is not None:
                try:
                    type = element.attrs.get('type', None)
                    if type == 'integer':
                        text = int(text)
                    elif type == 'float':
                        text = float(text)
                    else:
                        text = str(text)
                except (UnicodeError, ValueError):
                    pass
            self._attributes[element.name] = text
            self._set_attributes.pop(element.name, None)
            
    def __getattr__(self, name):
        # The attribute is treated as a resource attribute if
        # self._instance_vars_names is defined and it doesn't
        # contain the attribute name.
        if name not in self.__dict__.get('_instance_vars_names', (name,)):
            if name == 'id':
                return self._get_id()
            try:
                return self._set_attributes[name]
            except KeyError:
                pass
            try:
                return self._attributes[name]
            except KeyError:
                pass
        raise AttributeError('%s object has no attribute %s' % \
                             (repr(self.__class__.__name__), repr(name)))
            
    def __setattr__(self, name, value):
        # The attribute is treated as a resource attribute if
        # self._instance_vars_names is defined and it doesn't
        # contain the attribute name.
        if name in self.__dict__.get('_instance_vars_names', (name,)):
            object.__setattr__(self, name, value)         
        else:
            self._set_attributes[name] = value

    def __repr__(self):
        return '<%s.%s %s at 0x%x>' % (self.__class__.__module__,
            self.__class__.__name__, repr(self.id), id(self))

    def __eq__(self, other):
        if isinstance(other, Resource):
            return (self.id == other.id)
        return object.__eq__(self, other)
        
    def __hash__(self):
        return hash(self.id)

    def _get_id(self):
        # Overridden in subclasses.
        return ''

class Document(Resource):
    def __init__(self, xml):
        Resource.__init__(self, xml)
            
    def _get_id(self):
        return self.doc_id