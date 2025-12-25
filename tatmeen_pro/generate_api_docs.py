import os
import sys
import inspect
import django
from django.urls import URLPattern, URLResolver

# -------- INITIAL SETUP --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# IMPORTANT: Update this to your project's settings module:
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tatmeen_pro.settings")

django.setup()
# --------------------------------


OUTPUT_FILE = "API_DOCUMENTATION.md"


def extract_urls(urlpatterns, parent=""):
    docs = []

    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            path = parent + str(pattern.pattern)
            view = pattern.callback

            doc = inspect.getdoc(view) or "No description available."
            methods = getattr(view, "allowed_methods", ["GET"])

            docs.append({
                "path": path,
                "methods": methods,
                "description": doc
            })

        elif isinstance(pattern, URLResolver):
            nested = parent + str(pattern.pattern)
            docs.extend(extract_urls(pattern.url_patterns, nested))

    return docs


def generate_api_documentation():
    from tatmeen_pro.urls import urlpatterns   # Update if needed

    docs = extract_urls(urlpatterns)

    md = "# 📘 API Documentation (Auto-generated)\n\n"

    for d in docs:
        md += f"## `{d['path']}`\n"
        md += f"**Methods:** {', '.join(d['methods'])}\n\n"
        md += f"**Description:**\n{d['description']}\n\n"
        md += "---\n\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"API documentation generated → {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_api_documentation()
