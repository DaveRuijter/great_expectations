import json
from string import Template as pTemplate

from jinja2 import (
    Template, Environment, BaseLoader, PackageLoader, select_autoescape
)


def render_styling_from_template(template):
    if "styling" in template:

        class_list = template["styling"].get("classes", None)
        if class_list == None:
            class_str = ""
        else:
            class_str = 'class="'+' '.join(class_list)+'" '

        attribute_dict = template["styling"].get("attributes", None)
        if attribute_dict == None:
            attribute_str = ""
        else:
            attribute_str = ""
            for k, v in attribute_dict.items():
                attribute_str += k+'="'+v+'" '

        # TODO: Implement something for `style` here...
        styling_str = ""

        string = pTemplate('$classes$attributes$style').substitute({
            "classes": class_str,
            "attributes": attribute_str,
            "style": styling_str,
        })

        return string

    else:
        return ""


def render_template(template):
    if "styling" in template:
        # print("aaaa")
        params = template["params"]
        for parameter, parameter_styling in template["styling"]["params"].items():

            class_list = parameter_styling.get("classes", None)
            if class_list == None:
                class_str = ""
            else:
                class_str = 'class="'+' '.join(class_list)+'" '

            attribute_dict = parameter_styling.get("attributes", None)
            if attribute_dict == None:
                attribute_str = ""
            else:
                attribute_str = ""
                for k, v in attribute_dict.items():
                    attribute_str += k+'="'+v+'" '

            params[parameter] = pTemplate('<span $classes$attributes$style>$content</span>').substitute({
                "classes": class_str,
                "attributes": attribute_str,
                "style": parameter_styling.get("style", ""),
                "content": params[parameter],
            })
        string = pTemplate(template["template"]).substitute(params)
        # print(string)
        return string

    else:
        return pTemplate(template["template"]).substitute(template["params"])


class NoOpTemplate(object):
    @classmethod
    def render(cls, document):
        return document


class PrettyPrintTemplate(object):
    @classmethod
    def render(cls, document, indent=2):
        print(json.dumps(document, indent=indent))


# Abe 2019/06/26: This View should probably actually be called JinjaView or something similar.
# Down the road, I expect to wind up with class hierarchy along the lines of:
#   View > JinjaView > GEContentBlockJinjaView
class View(object):
    """Defines a method for converting a document to human-consumable form"""

    _template = NoOpTemplate

    @classmethod
    def render(cls, document, template=None):
        if template is None:
            template = cls._template

        t = cls._get_template(template)
        return t.render(document)

    @classmethod
    def _get_template(cls, template):
        if template is None:
            return NoOpTemplate

        env = Environment(
            loader=PackageLoader(
                'great_expectations',
                'render/view/templates'
            ),
            autoescape=select_autoescape(['html', 'xml'])
        )
        env.filters['render_template'] = render_template
        env.filters['render_styling'] = render_styling_from_template
        return env.get_template(template)


class ColumnHeaderView(View):
    _template = "header.j2"


class ValueListView(View):
    _template = "value_list.j2"


class ColumnSectionView(View):
    _template = "sections.j2"


class PageView(View):
    _template = "page.j2"
