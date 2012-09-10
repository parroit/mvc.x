"""
HTML forms
(part of web.py)
"""
import re



class Form(object):
    r"""
    HTML form.
    
        >>> f = Form(Textbox("x"))
        >>> f.render()
        '<table>\n    <tr><th><label for="x">x</label></th><td><input type="text" id="x" name="x"/></td></tr>\n</table>'
    """
    def __init__(self, *inputs, **kw):
        self.inputs = inputs
        self.valid = kw.pop('valid',True)
        self.note = kw.pop('note',None)
        self.validators = kw.pop('validators', [])
        self.id=kw.pop('id',None)
        self.name=kw.pop('name',None)
        self.status=kw.pop('status',None)
        self.action=kw.pop('action',None)




    def render(self):

        out = "<div id=\"form-container\"><form id=\""+ self.id +"\" name=\""+ self.name +"\" action=\""+ self.action +"""" class="well form-horizontal" method="POST">
        <fieldset>"""
        for i in self.inputs:


            out +="<div class=\"control-group %s\">" % ("error" if not i.is_valid() else "")
            if i.has_label():
                out +="     <label class='control-label' for='%s'>%s</label>"% (i.id, i.description)
            out +="     <div class=\"controls\">"
            out +=          i.pre + i.render()  + i.post + self.rendernote(i.note)
            out +="     </div>"
            out +="</div>"

        out += """</fieldset>
        </form>
            """
        if self.note:
            out += """
            <div class="alert %s" id="info-box" >
                <h5 class="alert-heading"><span id='info-title'>%s</span></h5>
                <img id='info-icon' src='/img/%s.png' class='img-rounded'/>
                <span id='info-text'>%s</span>
            </div>

        """ % (
               "alert-info" if self.valid else "alert-error",
               "Info" if self.valid else "Error",
               "saved" if self.valid else "error",
               ('<p class="help-inline">%s</p>' % self.note) if self.note else ""
        )
        out+="</div>"
        return out


    def rendernote(self, note):
        if note: return '<span class="help-inline">%s</span>' % note
        else: return ""



class Input(object):
    def __init__(self, name, **attrs):
        self.name = name

        self.attrs = attrs = AttributeList(attrs)
        
        self.description = attrs.pop('description', name)
        self.value = attrs.pop('value', None)
        self.pre = attrs.pop('pre', "")
        self.post = attrs.pop('post', "")
        self.valid = attrs.pop('valid',None)
        self.note = attrs.pop('note',None)
        
        self.id = attrs.setdefault('id', self.get_default_id())
        
        if 'class_' in attrs:
            attrs['class'] = attrs['class_']
            del attrs['class_']

    def has_label(self):
        return True
    def is_hidden(self):
        return False
    def is_valid(self):
        return self.valid


    def get_default_id(self):
        return self.name



    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def render(self):
        attrs = self.attrs.copy()
        attrs['type'] = self.get_type()
        if self.value is not None:
            attrs['value'] = self.value
        attrs['name'] = self.name
        return '<input %s/>' % attrs

    def rendernote(self, note):
        if note: return '<strong class="wrong">%s</strong>' % note
        else: return ""
        
    def addatts(self):
        # add leading space for backward-compatibility
        return " " + str(self.attrs)

class AttributeList(dict):
    """List of atributes of input.
    
    >>> a = AttributeList(type='text', name='x', value=20)
    >>> a
    <attrs: 'type="text" name="x" value="20"'>
    """
    def copy(self):
        return AttributeList(self)
        
    def __str__(self):
        return " ".join(['%s="%s"' % (k, v) for k, v in self.items()])


class Textbox(Input):
    """Textbox input.
    
        >>> Textbox(name='foo', value='bar').render()
        '<input type="text" id="foo" value="bar" name="foo"/>'
        >>> Textbox(name='foo', value=0).render()
        '<input type="text" id="foo" value="0" name="foo"/>'
    """        
    def get_type(self):
        return 'text'

class Password(Input):
    """Password input.

        >>> Password(name='password', value='secret').render()
        '<input type="password" id="password" value="secret" name="password"/>'
    """
    
    def get_type(self):
        return 'password'

class Textarea(Input):
    """Textarea input.
    
        >>> Textarea(name='foo', value='bar').render()
        '<textarea id="foo" name="foo">bar</textarea>'
    """
    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        value = self.value or ''
        return '<textarea %s>%s</textarea>' % (attrs, value)

class Dropdown(Input):
    r"""Dropdown/select input.
    
        >>> Dropdown(name='foo', args=['a', 'b', 'c'], value='b').render()
        '<select id="foo" name="foo">\n  <option value="a">a</option>\n  <option selected="selected" value="b">b</option>\n  <option value="c">c</option>\n</select>\n'
        >>> Dropdown(name='foo', args=[('a', 'aa'), ('b', 'bb'), ('c', 'cc')], value='b').render()
        '<select id="foo" name="foo">\n  <option value="a">aa</option>\n  <option selected="selected" value="b">bb</option>\n  <option value="c">cc</option>\n</select>\n'
    """
    def __init__(self, name, args, *validators, **attrs):
        self.args = args
        super(Dropdown, self).__init__(name, *validators, **attrs)

    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        
        x = '<select %s>\n' % attrs
        
        for arg in self.args:
            if isinstance(arg, (tuple, list)):
                value, desc= arg
            else:
                value, desc = arg, arg 

            if self.value == value or (isinstance(self.value, list) and value in self.value):
                select_p = ' selected="selected"'
            else: select_p = ''
            x += '  <option%s value="%s">%s</option>\n' % (select_p, value,desc)
            
        x += '</select>\n'
        return x

class Radio(Input):
    def __init__(self, name, args, *validators, **attrs):
        self.args = args
        super(Radio, self).__init__(name, *validators, **attrs)

    def render(self):
        x = '<span>'
        for arg in self.args:
            if isinstance(arg, (tuple, list)):
                value, desc= arg
            else:
                value, desc = arg, arg 
            attrs = self.attrs.copy()
            attrs['name'] = self.name
            attrs['type'] = 'radio'
            attrs['value'] = value
            if self.value == value:
                attrs['checked'] = 'checked'
            x += '<input %s/> %s' % (attrs, desc)
        x += '</span>'
        return x

class Checkbox(Input):
    def get_type(self):
        return 'checkbox'

    def render(self):


        if self.get_value()=="1" or self.get_value()=="True":
            self.attrs['checked'] = 'checked'

        self.set_value("1")
        return Input.render(self)



class Submit(Input):
    def get_type(self):
        return 'submit'
    def has_label(self):
        return False
    def render(self):
        self.attrs['value'] = self.attrs['content']
        self.attrs['class'] = "btn btn-large btn-success"
        return Input.render(self)
class Button(Input):
    """HTML Button.

    >>> Button("save").render()
    '<button id="save" name="save">save</button>'
    >>> Button("action", value="save", html="<b>Save Changes</b>").render()
    '<button id="action" value="save" name="action"><b>Save Changes</b></button>'
    """
    def __init__(self, name, *validators, **attrs):
        super(Button, self).__init__(name, *validators, **attrs)
        self.description = ""

    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        if self.value is not None:
            attrs['value'] = self.value
        html = attrs.pop('html', None) or self.name
        return '<button %s>%s</button>' % (attrs, html)

class Hidden(Input):
    """Hidden Input.
    
        >>> Hidden(name='foo', value='bar').render()
        '<input type="hidden" id="foo" value="bar" name="foo"/>'
    """
    def is_hidden(self):
        return True
        
    def get_type(self):
        return 'hidden'

class File(Input):
    """File input.
    
        >>> File(name='f').render()
        '<input type="file" id="f" name="f"/>'
    """
    def get_type(self):
        return 'file'
