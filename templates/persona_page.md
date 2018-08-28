# {{ obj.title }}

**ID: {{ obj.ident }}** [(permalink)](...)

## Description:

{{ obj.content }}

User narratives for this persona:
{% for narrative in obj.narratives %}
* {{ narrative.ident }}: {{ make_title_link(narrative) }} - {{ narrative.blurb }}
{% endfor %}