from jinja2 import Environment, FileSystemLoader
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def generate_report(data: dict, fmt: str = "html") -> tuple[str, str, str]:
    if fmt == "html":
        return _generate_html(data)
    else:
        return _generate_html(data)  # fallback to html


def _generate_html(data: dict) -> tuple[str, str, str]:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("report.html")
    html = template.render(review=data)
    return html, "text/html", f"review-{data['id']}.html"
