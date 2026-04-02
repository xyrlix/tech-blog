"""Markdown 渲染服务"""
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.tables import TableExtension
from slugify import slugify as _slugify


_MD_EXTENSIONS = [
    FencedCodeExtension(),
    CodeHiliteExtension(linenums=False, css_class="highlight"),
    TocExtension(permalink=True),
    TableExtension(),
    "nl2br",
    "sane_lists",
]


def render_markdown(text: str) -> str:
    """Markdown -> HTML"""
    return markdown.markdown(text, extensions=_MD_EXTENSIONS)


def make_slug(title: str) -> str:
    """标题 -> URL slug"""
    return _slugify(title, allow_unicode=True)
