Documentation
=============

To set up simple form validation and processing, simply subclass and
define form fields.

  >>> from repoze.formapi import Form
  
  >>> class TapeForm(Form):
  ...     """A form to edit a casette tape object."""
  ...
  ...     fields = {
  ...         'artist': unicode,
  ...         'title': unicode,
  ...         'asin': str,
  ...         'year': int,
  ...         'playtime': float}

When we display the form, we can pass in a ``data`` object, which
provides values corresponding to the fields.

Forms often do not have default values, for instance search forms or
add forms.

  >>> form = TapeForm()

The form data is available from the ``data`` attribute.

  >>> form.data['artist'] is None
  True
 
If a request comes in, it can be validated against the fields. There's
no inherent concept of required fields, hence requests may provide
zero or more field values.

  >>> request = Request(
  ...    params=(('title', u'Motorcity Detroit USA Live'),))

We pass the request to the form as keyword argument.

  >>> form = TapeForm(request=request)

This request would set the title of the record on the data object;
since it's a valid unicode string, we expect no validation errors.

  >>> form.validate()
  True
  
  >>> form.data['title']
  u'Motorcity Detroit USA Live'

We can also pass in a data object when we instantiate the form.

  >>> data = {
  ...    'artist': u'Bachman-Turner Overdrive',
  ...    'title': u'Four Wheel Drive',
  ...    'asin': 'B000001FL8',
  ...    'year': 1975,
  ...    'playtime': 33.53}

  >>> form = TapeForm(data)

  >>> form.data['title']
  u'Four Wheel Drive'

If we now pass in the request, we'll see that values from the request
are used before the data object is queried.

  >>> form = TapeForm(data, request=request)

  >>> form.data['title']
  u'Motorcity Detroit USA Live'

