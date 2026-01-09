from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# Association table for shared albums
album_shares = db.Table('album_shares',
    db.Column('album_id', db.Integer, db.ForeignKey('albums.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

# Association table for photo tags
photo_tags = db.Table('photo_tags',
    db.Column('photo_id', db.Integer, db.ForeignKey('photos.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tag {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(200))
    intro = db.Column(db.Text)
    role = db.Column(db.String(20), default='user') # 'user' or 'admin'
    liked_photos_privacy = db.Column(db.String(20), default='public') # public, private, shared
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    albums = db.relationship('Album', backref='author', lazy='dynamic')
    photos = db.relationship('Photo', backref='uploader', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    shared_albums = db.relationship('Album', secondary=album_shares, backref=db.backref('shared_users', lazy='dynamic'))
    liked_photos = db.relationship('Like', backref='user', lazy='dynamic')
    
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def add_notification(self, type, author, payload):
        n = Notification(user=self, author=author, type=type, payload=str(payload))
        db.session.add(n)
        return n

    def new_notifications(self):
        return self.notifications.filter_by(is_read=False).count()

    def mark_notifications_read(self):
        self.notifications.filter_by(is_read=False).update({'is_read': True})
        db.session.commit()

    def like_photo(self, photo):
        if not self.has_liked_photo(photo):
            like = Like(user_id=self.id, photo_id=photo.id)
            db.session.add(like)

    def unlike_photo(self, photo):
        if self.has_liked_photo(photo):
            Like.query.filter_by(user_id=self.id, photo_id=photo.id).delete()

    def has_liked_photo(self, photo):
        return Like.query.filter_by(user_id=self.id, photo_id=photo.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def is_mutual_following(self, user):
        return self.is_following(user) and user.is_following(self)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Album(db.Model):
    __tablename__ = 'albums'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    privacy = db.Column(db.String(20), default='public') # public, private, shared
    allow_download = db.Column(db.Boolean, default=True)
    is_banned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cover_id = db.Column(db.Integer, db.ForeignKey('photos.id', use_alter=True, name='fk_album_cover_photo'), nullable=True)
    
    # Relationships
    photos = db.relationship('Photo', backref='album', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Photo.album_id')
    cover = db.relationship('Photo', foreign_keys=[cover_id], post_update=True)

    def __repr__(self):
        return f'<Album {self.title}>'

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    filesize = db.Column(db.Integer)
    position = db.Column(db.Integer, default=0)
    is_banned = db.Column(db.Boolean, default=False)
    taken_at = db.Column(db.DateTime)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='photo', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='photo', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=photo_tags, backref=db.backref('photos', lazy='dynamic'))

    def __repr__(self):
        return f'<Photo {self.filename}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def __repr__(self):
        return f'<Comment {self.content}>'

class Like(db.Model):
    __tablename__ = 'likes'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Like User:{self.user_id} Photo:{self.photo_id}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(20)) # like, comment, follow, new_album, new_photo
    payload = db.Column(db.Text) # JSON string or simple ID
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notifications', lazy='dynamic'))
    author = db.relationship('User', foreign_keys=[author_id])

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False) # 'photo' or 'album'
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, resolved, dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reporter = db.relationship('User', backref='reports_filed')

    def __repr__(self):
        return f'<Notification {self.type}>'

# Helper to avoid forward reference issues between Album and Photo
def get_public_cover(self):
    # 1. Existing cover if valid and not banned
    if self.cover and not self.cover.is_banned:
        return self.cover
    
    # 2. Fallback to first non-banned photo
    # Check for both False and None for backward compatibility
    return self.photos.filter((Photo.is_banned == False) | (Photo.is_banned == None)).order_by(Photo.position.asc(), Photo.uploaded_at.desc()).first()

Album.public_cover = property(get_public_cover)
