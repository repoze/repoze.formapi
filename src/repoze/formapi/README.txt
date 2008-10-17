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

This request would set the title of the record on the form data
object; since it's a valid unicode string, we expect no validation
errors.

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

All updates to the data object are transient.

  >>> data['title']
  u'Four Wheel Drive'

We need to invoke the ``save`` method to commit the changes.

  >>> form.data.save()
  
  >>> data['title']
  u'Motorcity Detroit USA Live'

Form submission
---------------

By default, the form is assumed to be submitted; this means that the
form data will reflect values present in the request.

To change this behavior, instantiate the form with a ``prefix``
identifying this particular form.

The form is then submitted exactly when the values of the prefix code
parameter matches this prefix; by default, this is "form_id".

  >>> TapeForm.prefix_code
  'form_id'

  >>> request = Request(params=(
  ...    ('form_id', 'tape_form'),
  ...    ('title', u'Motorcity Detroit USA Live'),))

  >>> form = TapeForm(request=request, prefix='tape_form')

  >>> form.data['title']
  u'Motorcity Detroit USA Live'  

Note that the prefix must match the request prefix code value.

  >>> form = TapeForm(request=request, prefix='other_form')
  
  >>> form.data['title'] is None
  True

  
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

If we violate this constraint, we expect validation to fail.
  
  >>> request = Request(
  ...    params=(('year', u'1972'),))

  >>> form = EightiesTapeForm(data, request=request)

  >>> form.validate()
  False

The error message is available in the ``errors`` dictionary.

  >>> form.errors['year']
  u"Must be an 80's tape."

Data proxies
------------

We can bind a context object to a data object by using a proxy
object. This technique can be used to create edit or add-forms.

To illustrate this, let's define a content object. We'll hardcode
default values for simplicity.

  >>> class Tape(object):
  ...    artist = u'Bachman-Turner Overdrive'
  ...    title = u'Four Wheel Drive'
  ...    asin = 'B000001FL8'
  ...    year = 1975
  ...    playtime = 33.53

We can now create a data proxy for an instance of this class.
  
  >>> tape = Tape()
  >>> proxy = formapi.Proxy(tape)

With no further intervention, this data object acts as a proxy to read
and write attributes on the content object.

  >>> proxy.title
  u'Four Wheel Drive'
  
  >>> proxy.title = u'Motorcity Detroit USA Live'
  
  >>> tape.title
  u'Motorcity Detroit USA Live'

If we want to have more control over this process, we can subclass and
define descriptors.

The following example defines custom behavior for the ``title``
attribute; the value is uppercased.

  >>> class TapeProxy(formapi.Proxy):
  ...     def get_title(self):
  ...         return self.title
  ...
  ...     def set_title(self, value):
  ...         self.title = value.upper()
  ...
  ...     title = property(get_title, set_title)

  >>> proxy = TapeProxy(tape)

If we read and write to the ``title`` attribute of this proxy object,
the custom getter and setter functions are used.
  
  >>> proxy.title = u'Motorcity Detroit USA Live'

As would be expected from a proxy, changes are actually made to the
underlying content object.
  
  >>> tape.title
  u'MOTORCITY DETROIT USA LIVE'

Saving form data
----------------
  
When instantiating a form, you can pass in a proxy object instead of
``data``. This binds the data object to the proxy, but it also allows
us to save the form data on the proxied object.
  
  >>> form = EightiesTapeForm(proxy, request=request)

  >>> form.data['title'] = u'Four Wheel Drive'

Assignment behaves logically.
  
  >>> form.data['title']
  u'Four Wheel Drive'
  
However, if we invoke the ``save`` action, changes take effect on the
proxied object.
  
  >>> form.data.save()
  
  >>> tape.title
  u'FOUR WHEEL DRIVE'

  
