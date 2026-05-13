from django import template

register = template.Library()


@register.filter
def ru_plural(value, variants):
    variants = variants.split(",")
    value = abs(int(value))
    if value % 10 == 1 and value % 100 != 11:
        return f"{value} {variants[0]}"
    elif (
        value % 10 >= 2 and value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20)
    ):
        return f"{value} {variants[1]}"
    else:
        return f"{value} {variants[2]}"
