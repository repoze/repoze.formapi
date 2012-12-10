Introduction
============

This library helps you parse, validate and deserialize form input as
well as execute form actions.

The starting point is to define the data structure that describes your
data. For instance, an action string and a list of numbers (typical
for a form that allows a user to select some items and apply an
action):

>>> fields = {
...     'action': unicode,
...     'items': [int]
... }

Let's apply the following input sequence:

>>> params = [
...      ('action', 'submit'),
...      ('items', 1),
...      ('items', 2),
...      ('security-token', '...')
... ]

Note that ``'security-token'`` is an example of a parameter that is
provided, but not defined in the fields. That's not an error.

Now, to parse the parameters above into the data structure defined by
our fields definition, we use the ``parse`` function (note that in the
rest of this text, we assume that symbols have been imported).

>>> from repoze.formapi import parse
>>> data, errors = parse(params, fields)

In the logic that handles this call, you'll typically want to test if
the ``errors`` value is true (meaning there was an error) or false
(meaning there was no error).

>>> bool(errors)
False

Let's take a look at the data:

>>> data
{'action': u'submit', 'items': [1, 2]}


Types
=====

In the previous example, we used Python's built-in data types: ``int``
and ``unicode``.

However, you can use any callable as the data type. Note that if the
callable raises a ``KeyError``, then it's simply ignored.

Let's try an example:

>>> data, errors = parse((('foo', 'bar'), ('baz', 'boo'), ('baz', 'qux')), {
...     'foo': str.upper,
...     'baz': {'boo': 'yes'}.__getitem__,
... })

What can we expect in ``data``?

The ``'foo'`` parameter will be uppercased, the first ``'baz'``
resolves to ``'yes'``, while the other raises a ``KeyError`` and is
ignored.

>>> data
{'foo': 'BAR', 'baz': 'yes'}

It's useful to remember that if you want a parameter to be ignored,
simply raise a ``KeyError``.


Forms
=====

The library provides an abstraction for handling forms.

To create a form you subclass the ``Form`` class and define the form
field definitions in the ``fields`` attribute.

>>> class TapeForm(Form):
...     """Casette tape form."""
...
...     fields = {
...         'artist': unicode,
...         'title': unicode,
...         'asin': str,
...         'year': int,
...         'playtime': float
...     }

If there are no start or *default* values, the form can be
instantiated with no arguments:

>>> form = TapeForm()

The form data is available from the ``data`` attribute. Since we
didn't pass in a request, there's no data available.

>>> form.data['artist'] is None
True

That's not very interesting. Let's pass an input parameter.

>>> params = (('title', u'Motorcity Detroit USA Live'),)
>>> form = TapeForm(params=params)

This will set the ``'title'`` field.

The input is a valid unicode string and there are no validation
errors.

>>> form.validate()
True

Let's confirm that the data is available.

>>> form.data['title']
u'Motorcity Detroit USA Live'

The library also support passing in a ``request`` argument, if this is
an object that has a ``params`` attribute.

>>> request = Request(params=params)

The ``Request`` class from `WebOb <http://pypi.python.org/pypi/WebOb>`_
(a popular package that provides an object-oriented interface to the
HTTP protocol) is compatible.

>>> form = TapeForm(request=request)

We'll often want to initialize the form with default values. To this
effect we pass in a dictionary object.

>>> data = {
...    'artist': u'Bachman-Turner Overdrive',
...    'title': u'Four Wheel Drive',
...    'asin': 'B000001FL8',
...    'year': 1975,
...    'playtime': 33.53
... }
>>> form = TapeForm(data)

The values are available in the form data object.

>>> form.data['title']
u'Four Wheel Drive'

However, if we pass in the request from the former example, we'll see
that values from the request are used before the passed dictionary
object is queried.

>>> form = TapeForm(data, request=request)
>>> form.data['title']
u'Motorcity Detroit USA Live'

The provided ``data`` dictionary is unchanged at this point:

>>> data['title']
u'Four Wheel Drive'

We need to invoke the ``save`` method to commit the changes to the
provided dictionary.

>>> form.data.save()
>>> data['title']
u'Motorcity Detroit USA Live'


Additional validation
---------------------

It is possible to create validation methods for more complex
needs. These extra validators can be hooked up using the `validator`
decorator.

>>> class CDForm(Form):
...     fields = {
...         'artist': unicode,
...         'title': unicode,
...         'asin': str,
...         'year': int,
...         'genre': str,
...         'playtime': float}
...
...     @validator
...     def check_genre(self):
...         if self.data['genre'] != 'rock':
...             yield 'Genre is invalid'

A validator can look at all the data that is available. This makes it
easy to create validators that need to check multiple fields.

>>> form = CDForm()
>>> form.validate()
False

The errors attribute contains our error message.

>>> form.errors[0]
'Genre is invalid'

Errors can also be assigned to a specific field. To do this a
validator can register itself for a specific field.

>>> class CDForm(Form):
...
...     fields = {
...         'artist': unicode,
...         'title': unicode,
...         'asin': str,
...         'year': int,
...         'genre': str,
...         'playtime': float}
...
...     @validator('genre')
...     def check_genre(self):
...         if self.data['genre'] != 'rock':
...             yield 'Genre is invalid'

When this form is validated it will have the error available for the
specific field.

>>> form = CDForm()
>>> form.validate()
False
>>> 'genre' in form.errors
True
>>> form.errors['genre'][0]
'Genre is invalid'

Form context
------------

We can set the context of a form to some object.

>>> class Tape:
...    title = u'Motorcity Detroit USA Live'
...    asin = 'B000001FL8'
...    year = 1975

>>> tape = Tape()

The form data will draw defaults from the context.

>>> form = TapeForm(context=tape)
>>> form.data['title']
u'Motorcity Detroit USA Live'

Request parameters take priority over the context. In the following
example, we submit the form with trivial input.

>>> request = Request(params=(('asin', u''), ('year', u'')))
>>> form = TapeForm(context=tape, request=request)

This form input is valid; although ``year`` is an integer field, the
trivial input is valid and will be assigned a value of ``None``.

>>> form.validate()
True

The ``asin`` input is coerced to a string (from unicode).

>>> form.data['asin']
''

The ``year`` input is trivial. It's not a required field, so the value
is ``None`` (treated as a non-input).

>>> form.data['year'] is None
True

Required fields
---------------

We use the ``required`` method to mark fields required.

Let's continue the example from above. If we make the fields required,
the input no longer validates.

>>> TapeForm.fields['year'] = required(int, u"Required field" )
>>> TapeForm.fields['asin'] = required(str)

The form input is no longer valid.

>>> form = TapeForm(context=tape, request=request)
>>> form.validate()
False
>>> form.data['year'] is None
True

The error message is available as well:

>>> form.errors['year'][0]
'Required field'

Now let's try a valid input:

>>> request = Request(params=(('asin', u'B000001FL8'), ('year', u'1978')))
>>> form = TapeForm(context=tape, request=request)

We can expect both required fields to be
converted and correctly typed.

>>> form.validate()
True

>>> form.data['asin']
'B000001FL8'

>>> form.data['year']
1978

Form submission
---------------

If a form prefix has not been set, the request is applied by
default. However, most applications will want to set a form prefix and
require explicit form submission.

A form submits a "default action" if the prefix is submitted as a
parameter.

>>> request = Request(params=(
...    ('tape_form', ''),
...    ('title', u'Motorcity Detroit USA Live')))
>>> form = TapeForm(request=request, prefix='tape_form')
>>> form.data['title']
u'Motorcity Detroit USA Live'

As expected, if we submit a form with a different prefix, the request
is not applied.

>>> form = TapeForm(request=request, prefix='other_form')
>>> form.data['title'] is None
True

We can also define form actions on the form class itself.

>>> class TapeAddForm(TapeForm):
...     """An add-form for a casette tape."""
...
...     @action
...     def handle_add(self, data):
...         print "add"
...
...     @action("add_and_edit")
...     def handle_add_and_edit(self, data):
...         print "add_and_edit"

The first action is a "default action"; if we submit the request we
set up before, this action will be read to be submitted.

>>> form = TapeAddForm(request=request, prefix='tape_form')
>>> form.actions
[<Action name="" submitted="True">,
 <Action name="add_and_edit" submitted="False">]

The submitted action is available in the ``action`` parameter.

>>> form.action
<Action name="" submitted="True">

To call the form handler of the submitted action, we invoke the form's
call method.

>>> form()
add

To call the named form action, there must be a parameter in the
request which is a concatenation of the prefix and the form action
name. Accepted separation characters are '.' (dot), '_' (underscore)
and '-' (dash).

>>> request = Request(params=(
...    ('tape_form-add_and_edit', ''),
...    ('title', u'Motorcity Detroit USA Live'),))
>>> form = TapeAddForm(request=request, prefix='tape_form')
>>> form.actions
[<Action name="" submitted="False">,
 <Action name="add_and_edit" submitted="True">]
>>> form()
add_and_edit

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
>>> proxy = Proxy(tape)

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

>>> class TapeProxy(Proxy):
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

>>> form = TapeForm(proxy, request=request)
>>> form.data['title'] = u'Four Wheel Drive'

Assignment behaves logically.

>>> form.data['title']
u'Four Wheel Drive'

However, if we invoke the ``save`` action, changes take effect on the
proxied object.

>>> form.data.save()
>>> tape.title
u'FOUR WHEEL DRIVE'

