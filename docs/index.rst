.. _index:

==============
repoze.formapi
==============

:mod:`repoze.formapi` is a standalone forms framework for
Python. The philosophy is integration rather than abstraction, meaning
that you write your own HTML forms while the library handles field
marshalling, validation and form actions.

The library was written to fill the gap between ad-hoc homegrown code
and frameworks like :mod:`zope.formlib` and :mod:`ToscaWidgets` which
relies on form schemas and widgets to define, process and render
forms. While these libraries certainly have their place, they often
get in your away and provide little support when you try and have it
your way.

Introduction
============

Enter :mod:`repoze.formapi`. Write your form, preferably in a template
language that lets you present validation errors, and define form
fields using Python. Here's an example of a form fields definition for
a shopping cart:

  >>> fields = {
  ...   'items': {str: int},
  ...   'shipping_method': str,
  ...   'gift_wrapping': bool,
  ...   }

The `items` field represents items added to the shopping cart for
which we need to register the number of orders; `shipping_method` is a
string identifying the shipping method and finally we record whether
gift-wrapping is desired.

In terms of HTML, we could write the form as follows (to keep the
example brief we include only the actual input elements--labels, error
feedback and field descriptions have been left out)::

  <input type="text" name="items.bicycle" value="3" />
  <input type="text" name="items.wagon" value="1" />

  <select name="shipping_method">
    <option value="fedex">FedEx</option>
    <option value="usps" selected="selected">Regular mail</option>
  </select>

  <input type="checkbox" name="gift_wrapping" value="1" checked="checked" />

The `params` sequence of key/value request parameters (as available
from the request-object of the :mod:`WebOb` library) corresponding
to this form is:

  >>> params = (
  ...    ('items.bicycle', '3'),
  ...    ('items.wagon', '1'),
  ...    ('shipping_method', 'usps'),
  ...    ('gift_wrapping', '1'))

By marshalling the parameters, the parameters are put on the form of
the form field definitions:

  >>> data, errors = marshall(params, fields)
  >>> data['items']
  {'bicycle': 3, 'wagon': 1}
  >>> data['shipping_method']
  'usps'
  >>> data['gift_wrapping']
  True
  
Notice that the values follow the types defined in `fields`.

In addition to field marshalling, the :mod:`repoze.formapi` library
provides a minimalistic framework around which you can create forms,
validation routines and action handling. Details on this and much more
is available in the :ref:`usage` section.

Narrative documentation
-----------------------

Narrative documentation explaining how to use :mod:`repoze.formapi`.

.. toctree::
   :maxdepth: 2

   usage
   glossary
   changes

Authors
-------

.. literalinclude:: ../AUTHOR.txt

API documentation
-----------------

API documentation for :mod:`repoze.formapi`.

.. toctree::
   :maxdepth: 2

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`

