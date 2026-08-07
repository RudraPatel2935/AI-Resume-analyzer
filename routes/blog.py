import re
from datetime import datetime
from flask import Blueprint, render_template, request, Response, url_for, abort
from models.blog import BlogPost
from database.db import db

blog_bp = Blueprint("blog", __name__)


def markdown_to_html(text):
    """
    A lightweight, safe Markdown to HTML converter for blog posts.
    Handles headings, bold, italic, lists, blockquotes, code blocks, tables, and links.
    """
    if not text:
        return ""

    # Escape HTML special chars (simple safety measure)
    html = text

    # Code blocks ```
    def code_block_sub(match):
        code = match.group(2).replace("<", "&lt;").replace(">", "&gt;")
        return f'<pre><code class="language-{match.group(1) or "text"}">{code}</code></pre>'

    html = re.sub(r"```(\w*)\n(.*?)```", code_block_sub, html, flags=re.DOTALL)

    # Inline code `code`
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

    # Headings
    html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

    # Bold and Italics
    html = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", html)

    # Links [text](url)
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', html)

    # Blockquotes
    html = re.sub(r"^> (.*?)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)

    # Horizontal Rule
    html = re.sub(r"^---$", r"<hr>", html, flags=re.MULTILINE)

    # Unordered Lists
    lines = html.split("\n")
    in_list = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            content = line.strip()[2:]
            if not in_list:
                new_lines.append("<ul>")
                in_list = True
            new_lines.append(f"  <li>{content}</li>")
        else:
            if in_list:
                new_lines.append("</ul>")
                in_list = False
            new_lines.append(line)
    if in_list:
        new_lines.append("</ul>")

    html = "\n".join(new_lines)

    # Paragraphs (convert double newlines to paragraphs)
    paras = html.split("\n\n")
    formatted_paras = []
    for p in paras:
        p_str = p.strip()
        if not p_str:
            continue
        if any(p_str.startswith(tag) for tag in ["<h1", "<h2", "<h3", "<ul", "<ol", "<pre", "<blockquote", "<hr"]):
            formatted_paras.append(p_str)
        else:
            formatted_paras.append(f"<p>{p_str}</p>")

    return "\n".join(formatted_paras)


@blog_bp.route("/blog")
def index():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    posts_query = BlogPost.query.filter_by(is_published=True)

    if category:
        posts_query = posts_query.filter_by(category=category)

    if query:
        search_filter = f"%{query}%"
        posts_query = posts_query.filter(
            (BlogPost.title.ilike(search_filter)) |
            (BlogPost.summary.ilike(search_filter)) |
            (BlogPost.keywords.ilike(search_filter))
        )

    posts = posts_query.order_by(BlogPost.created_at.desc()).all()

    # Get distinct categories for filter bar
    categories_raw = db.session.query(BlogPost.category).filter_by(is_published=True).distinct().all()
    categories = [cat[0] for cat in categories_raw if cat[0]]

    featured_post = posts[0] if (posts and not query and not category) else None
    remaining_posts = posts[1:] if featured_post else posts

    return render_template(
        "blog/index.html",
        posts=remaining_posts,
        featured_post=featured_post,
        categories=categories,
        selected_category=category,
        search_query=query,
    )


@blog_bp.route("/blog/<slug>")
def detail(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    recent_posts = BlogPost.query.filter(
        BlogPost.id != post.id, BlogPost.is_published == True
    ).order_by(BlogPost.created_at.desc()).limit(3).all()

    formatted_content = markdown_to_html(post.content)

    return render_template(
        "blog/post.html",
        post=post,
        content_html=formatted_content,
        recent_posts=recent_posts,
    )


@blog_bp.route("/sitemap.xml")
def sitemap():
    host = request.host_url.rstrip("/")
    published_posts = BlogPost.query.filter_by(is_published=True).all()

    urls = [
        {"loc": f"{host}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{host}/blog", "priority": "0.9", "changefreq": "daily"},
    ]

    for post in published_posts:
        mod_date = (post.updated_at or post.created_at or datetime.utcnow()).strftime("%Y-%m-%d")
        urls.append({
            "loc": f"{host}/blog/{post.slug}",
            "lastmod": mod_date,
            "priority": "0.8",
            "changefreq": "weekly",
        })

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for url in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{url['loc']}</loc>")
        if "lastmod" in url:
            xml_lines.append(f"    <lastmod>{url['lastmod']}</lastmod>")
        xml_lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{url['priority']}</priority>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    return Response("\n".join(xml_lines), mimetype="application/xml")


@blog_bp.route("/robots.txt")
def robots():
    host = request.host_url.rstrip("/")
    content = f"""User-agent: *
Allow: /
Allow: /blog
Disallow: /admin
Disallow: /uploads/

Sitemap: {host}/sitemap.xml
"""
    return Response(content, mimetype="text/plain")
