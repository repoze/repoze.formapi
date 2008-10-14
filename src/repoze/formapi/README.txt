Documentation
=============

To set up form fields, simply subclass and set the ``fields``
attribute.

  >>> from repoze import formapi
  
  >>> class TapeForm(formapi.Form):
  ...     """A form to edit a casette tape object."""
  ...
  ...     fields = {
  ...         'artist': unicode,
  ...         'title': unicode,
  ...         'asin': str,
  ...         'year': int,
  ...         'playtime': float}

Forms often do not have default values, for instance search forms or
add forms.

  >>> form = TapeForm()

The form data is available from the ``data`` attribute. Since we
didn't pass in a request, there's no data available.

  >>> form.data['artist'] is None
  True

If a request comes in, the values are reflected in the form data. We
can also validate the request against the form fields.

There's no inherent concept of required fields, hence requests may
provide zero or more field values.
  
We pass the request to the form as keyword argument.

  >>> request = Request(
  ...    params=(('title', u'Motorcity Detroit USA Live'),))

  >>> form = TapeForm(request=request)

This request would set the title of the record on the data object;
since it's a valid unicode string, we expect no validation errors.

  >>> form.validate()
  True
  
  >>> form.data['title']
  u'Motorcity Detroit USA Live'

We'll often want to initialize the form with default values. To this
effect we pass in a dictionary object.

  >>> data = {
  ...    'artist': u'Bachman-Turner Overdrive',
  ...    'title': u'Four Wheel Drive',
  ...    'asin': 'B000001FL8',
  ...    'year': 1975,
  ...    'playtime': 33.53}

  >>> form = TapeForm(data)

The values are available in the ``data`` object.
  
  >>> form.data['title']
  u'Four Wheel Drive'

However, if we pass in the request from the former example, we'll see
that values from the request are used before the passed dictionary
object is queried.

  >>> form = TapeForm(data, request=request)

  >>> form.data['title']
  u'Motorcity Detroit USA Live'

Validation
----------

To add custom validation to your forms, add a form decorator.

  >>> class EightiesTapeForm(TapeForm):
  ...     """A form to accept 80's casette tape submissions."""
  ...
  ...     @formapi.validator('year')
  ...     def validate_year(self):
  ...         if not 1979 < self.data['year'] < 1989:
  ...            return u"Must be an 80's tape."

Let's try and violate this contraint.
  
  >>> request = Request(
  ...    params=(('year', u'1972'),))

  >>> form = EightiesTapeForm(data, request=request)

  >>> form.validate()
  False

The error message is available in the ``errors`` dictionary.

  >>> form.errors['year']
  u"Must be an 80's tape."
