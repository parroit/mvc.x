import re
from datetime import time
from org.vertx.java.core.json import JsonObject
from mvc_x import form

def attr_get(obj, attr, value=None):
    if hasattr(obj, 'has_key') and obj.has_key(attr): return obj[attr]
    if hasattr(obj, attr): return getattr(obj, attr)
    return value

__author__ = 'parroit'

class Bindable():
    def clone(self):
        return Bindable(self.name,validators=self.validators,action=self.action  ,*self.fields)
    def get_widget(self,x):
        if x.type=="text" or x.type=="number" or x.type=="datetime":
            return form.Textbox(x.name,id=x.name,description=x.description,value=x.get_value(),valid=x.is_valid(),note=x.note,**x.attrs)
        elif x.type=="password":
            return form.Password(x.name,id=x.name,description=x.description,value=x.get_value(),valid=x.is_valid(),note=x.note,**x.attrs)
        elif x.type=="checkbox":
            return form.Checkbox(x.name,id=x.name,description=x.description,value=x.get_value(),valid=x.is_valid(),note=x.note,**x.attrs)
        elif x.type=="submit":
            return form.Submit(x.name,id=x.name,description=x.description,value=x.get_value(),valid=x.is_valid(),note=x.note,**x.attrs)
        elif x.type=="select":
            print(x.attrs)
            return form.Dropdown(x.name,x.attrs["items"],id=x.name,description=x.description,value=x.get_value(),valid=x.is_valid(),note=x.note,**x.attrs)

    def to_json(self):
        obj=JsonObject()
        #print("to_json")
        for x in self.fields:
            #print(x.name)
            obj.putString(x.name,str(x.get_value()))
            #print("to_json end ")
        return obj

    def to_form(self,form_action=None):

        inputs=[self.get_widget(x) for x in self.fields ]

        action=form_action or self.action
        return form.Form(id=self.name,action=action,name=self.name,valid=self.is_valid(),note=self.note, *inputs).render()

    def fill_from_values(self,values):
        clone=self.clone()
        vals=dict(values)
        clone.source=values
        print(values)
        for column in clone.fields:
            value=None
            if hasattr(values, column.name):
                value = getattr(values, column.name)
            elif vals.has_key(column.name):
                value=vals[column.name]

            if not value is None:
                if isinstance(value ,list) and len(value)==1:
                    column.set_value(value[0])
                else:
                    column.set_value(value)
            else:
                if column.type=="checkbox":
                    column.set_value("0")
                else:
                    column.set_value("")
        return clone



    def __init__(self,name, *fields, **kw):
        self.name=name
        self.fields = fields
        self.valid = True
        self.note = None
        self.source=None
        self.action = kw.pop('action', "")
        self.validators = kw.pop('validators', [])

    def is_valid(self):
        return self.valid

    def validate(self):

        _valid = True
        for fld in self.fields:
            _valid = fld.validate() and _valid
        if not _valid:
            self.note="Some fields contains invalid data."
        _valid = _valid and self._validate()

        self.valid = _valid
        return _valid

    def _validate(self):

        for v in self.validators:
            if not v.valid(self):
                self.note = v.msg
                return False
        return True

    def fill(self, source=None, **kw):
        return self.validates(source, _validate=False, **kw)

    def __getitem__(self, i):
        for x in self.fields:
            if x.name == i: return x
        raise KeyError, i

    def __getattr__(self, name):
        # don't interfere with deepcopy
        inputs = self.__dict__.get('fields') or []
        for x in inputs:
            if x.name == name: return x
        raise AttributeError, name

    def get(self, i, default=None):
        try:
            return self[i]
        except KeyError:
            return default

class Field(object):
    def __init__(self, name, *validators, **attrs):
        self.name = name
        self.validators = validators
        self.attrs = attrs
        self.value=None
        self.valid=True
        self.note=attrs.pop('note', "")

        self.description = attrs.pop('description', name)
        self.type = attrs.pop('type', type)

    def clone(self):
        return Field(self.name,*self.validators,**self.attrs )

    def get_type(self):
        return self.type

    def validate(self):
        self.valid=True
        for v in self.validators:
            if not v.valid(self.value):
                self.note = v.msg
                self.valid=False

        return self.valid
    def is_valid(self):
        return self.valid

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value



class Validator:

    def __init__(self, msg, test):
        self.msg=msg
        self.test=test

    def valid(self, value):
        try: return self.test(value)
        except Exception: return False

notnull = Validator("Required", bool)

class regexp(Validator):
    def __init__(self, rexp, msg):
        Validator.__init__(self, msg,None)
        self.rexp = re.compile(rexp)
        self.msg = msg

    def valid(self, value):
        return bool(self.rexp.match(value))

if __name__ == "__main__":
    import doctest
    doctest.testmod()


class Required(Validator):
    def __init__(self, msg="This field is required."):
        self.msg = msg

    def valid(self, value):

        result = not value is None and value <> "" and value <> 0    and value <> 0.0
        print str(value)+" valid: "+str(result)
        return result

class TextRe(Validator):
    def __init__(self, rexp, msg):
        self.rexp = re.compile(rexp,re.DOTALL)
        self.msg = msg

    def valid(self, value):
        return bool(self.rexp.match(value))

def freetext(min, max):
    return TextRe(u".{" + str(min) + "," + str(max) + "}$",
        "Deve essere un testo di lunghezza compresa fra " + str(min) + " e " + str(max) + " caratteri.")


def numeric():
    return form.regexp(u"[0-9]*$", "Deve essere un valore numerico.")


class DateValidator(Validator):
    def __init__(self, msg):
        self.msg = msg

    def valid(self, value):
        try:

            return value!=u"01/01/1900" and time.strptime(value, '%d/%m/%Y')
        except ValueError:
            return False


def valid_date():
    return DateValidator("Deve essere una data valida.")



codice_fiscale_valido = regexp(r"[A-Za-z]{6}[0-9LMNPQRSTUV]{2}[A-Za-z]{1}[0-9LMNPQRSTUV]{2}[A-Za-z]{1}[0-9LMNPQRSTUV]{3}[A-Za-z]{1}$", 'Deve essere un codice fiscale valido.')
nominativo = regexp(r"[0-9A-Za-z ',\-\.\(\)]{1,100}$", 'Deve essere compreso fra 1 e 100 caratteri alfanumerici <o \',-.()>')
sponsor_valido = regexp(r"[0-9A-Za-z ',\-\.\(\)]{0,100}$", 'Deve essere compreso fra 0 e 100 caratteri alfanumerici <o \',-.()>')
alfanum = regexp(r"[a-zA-Z0-9]*$", 'Deve essere costituito da caratteri alfanumerici')
text = regexp(r"[a-zA-Z0-9 ]*$", 'Deve essere costituito da caratteri alfanumerici e spazi')

email=regexp(r"^[_.0-9a-z-]+@([0-9a-z][0-9a-z-]+.)+[a-z]{2,4}$", 'Deve essere un indirizzo email')