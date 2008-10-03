Documentation
=============

Forms
-----

To define a form, subclass the ``Form`` class and define attributes
and validators.

Note that the ``validator`` decorator accepts multiple fields.
  
  >>> from repoze.formapi import Form, validator
  >>> from zope import schema

  >>> class LanguageForm(Form):
  ...     language = schema.TextLine(
  ...         title=u"Programming language",
  ...         description=u"Which language will be used for this project.")
  ...
  ...     @validator(language)
  ...     def validate_language(self):
  ...         if not self.language == 'Python':
  ...              return "Bad language: %s." % self.language

To validate the form, instantiate it with a request and call the
``validate`` method. It returns a dictionary that maps form field
names to validation errors.
  
  >>> request = testing.Request(params={'language': u"Python"})
  >>> LanguageForm(request).errors
  {}
  
If we pass in a request that does not validate, we'll see a validation
error in the returned dictionary.

  >>> request = testing.Request(params={'language': u"Ruby"})
  >>> LanguageForm(request).errors
  {'language': [<ValidationError field="language" u'Bad language: Ruby.'>]}

Upon form instantiation, we can provide a ``context`` instance from
which we'll draw default values.

  >>> class Model:
  ...     def __init__(self):
  ...         self.language = u"Python"

The default value is only used if the field is not set in the request.
  
  >>> LanguageForm(request, context=Model()).errors
  {'language': [<ValidationError field="language" u'Bad language: Ruby.'>]}

  >>> request = testing.Request()
  >>> LanguageForm(request, context=Model()).errors
  {}

  >>> language_form = LanguageForm(request, prefix="prefix", action="action")
  >>> language_form.action
  'action'

  >>> language_form.submit
  'prefix.submit'
  
Form fields
-----------

A form fields class is available to access bound form field; these
extend the form field with value and error status.

  >>> request = testing.Request(params={'prefix.language': u"Ruby"})
  >>> language_form = LanguageForm(request, prefix='prefix')
  >>> from repoze.formapi import Fields
  >>> fields = language_form.fields

Individual fields are accessed using attribute lookup.
  
  >>> field = fields.language

The bound form field is a copy of the original field.

  >>> field
  <zope.schema._bootstrapfields.TextLine object at ...>

The field object provides the properties needed to create a form field
HTML.
  
  >>> field.name, field.value, field.label, field.help
  ('prefix.language',
   u'Ruby',
   u'Programming language',
   u'Which language will be used for this project.')
  
Error messages are concatenated and made available in the ``error``
attribute.

  >>> field.error
  u'Bad language: Ruby.'

If we passed in a request that validates, the error message is ``None``.

  >>> request = testing.Request(params={'language': u"Python"})
  >>> language_form = LanguageForm(request)
  >>> fields = Fields(language_form)

  >>> fields.language.error is None
  True

Field widgets
-------------

We can register components that register form field widgets.

  >>> from repoze.formapi.interfaces import IWidget

  >>> @interface.implementer(IWidget)
  ... @component.adapter(Form, schema.TextLine)
  ... def string_widget(form, field):
  ...     return u'<input type="text" name="%(name)s" value="%(value)s" />' % \
  ...         field.__dict__

  >>> component.provideAdapter(string_widget)

  >>> print field.render()
  <input type="text" name="prefix.language" value="Ruby" />
