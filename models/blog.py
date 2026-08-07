from datetime import datetime
from database.db import db


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    summary = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), default="AI Resume Team")
    category = db.Column(db.String(50), default="Career & Resume Tips", index=True)
    read_time = db.Column(db.String(20), default="5 min read")
    meta_title = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    keywords = db.Column(db.String(255), nullable=True)
    is_published = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "summary": self.summary,
            "author": self.author,
            "category": self.category,
            "read_time": self.read_time,
            "created_at": self.created_at.strftime("%B %d, %Y") if self.created_at else "",
        }
