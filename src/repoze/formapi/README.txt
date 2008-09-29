Documentation
=============

  >>> from repoze.formapi import model
  >>> from zope import schema
  
  >>> class Model(model.Model):
  ...     language = schema.TextLine(title=u"Programming language")
  ...
  ...     @model.validator(language)
  ...     def validate_language(self):
  ...         if not self.language == 'Python':
  ...              return "Bad language: %s." % self.language
  
  >>> from repoze.formapi.form import Form
  >>> form = Form(Model)

Validate form.

  >>> form.validate(testing.Request(params={'language': u"Python"}))
  ()
  
Let's try sneaking in a suboptimal language:
  
  >>> form.validate(testing.Request(params={'language': u"Ruby"}))
  (<ValidationError field="language" u'Bad language: Ruby.'>,)
