{{ name | escape | underline}}

..
   old hacky method
   {% set parent = fullname.split(".")[:-1] | join('.') %}

   .. line-block:: 
      :mod:`{{parent}}`
      ↪{{name}}

.. ↪ :mod:`{{module}}`

.. autodata:: {{ fullname }}
   :no-value:
   

