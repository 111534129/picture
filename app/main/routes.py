from flask import render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import re
import zipfile
import json
import io
from flask import send_file
from app import db
from app.main import bp
from app.main.forms import AlbumForm, PhotoUploadForm, CommentForm, EditProfileForm, ImportAlbumForm
from app.models import Album, Photo, Comment, User, Notification, Report, Tag, photo_tags

@bp.route('/')
@bp.route('/index')
def index():
    tab = request.args.get('tab', 'discovery')
    items = []
    
    if tab == 'following':
        if not current_user.is_authenticated:
            flash('請先登入以查看好友動態。')
            return redirect(url_for('auth.login'))
            
        # Get followed users IDs
        followed_ids = [u.id for u in current_user.followed.all()]
        if followed_ids:
            # Query photos from followed users found in PUBLIC albums
            # (Simplification for MVP: only showing public content in feed to avoid complex privacy queries in one go)
            items = Photo.query.join(Album, Photo.album_id == Album.id).filter(
                Photo.user_id.in_(followed_ids),
                Album.privacy == 'public',
                (Photo.is_banned == False) | (Photo.is_banned == None)
            ).order_by(Photo.uploaded_at.desc()).all()
    else:
        # Default: Discovery (Public Albums)
        items = Album.query.filter_by(privacy='public').filter((Album.is_banned == False) | (Album.is_banned == None)).order_by(Album.created_at.desc()).all()
        
    return render_template('index.html', title='Home', items=items, tab=tab)

def parse_tags(text):
    if not text:
        return []
    # Find all hashtags - more robust regex for various languages
    # Matches # followed by non-whitespace and non-special-punctuation characters
    tag_names = list(set(re.findall(r'#([^\s#.,!@$%^&*()=+\[\]{};\':"\\|<>/?？，。！]+)', text)))
    tags = []
    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    return tags

@bp.app_template_filter('linkify_tags')
def linkify_tags(text):
    if not text:
        return ""
    def replace(match):
        name = match.group(1)
        return f'<a href="{url_for("main.tag", name=name)}" style="color: #007bff; text-decoration: none;">#{name}</a>'
    return re.sub(r'#([^\s#.,!@$%^&*()=+\[\]{};\':"\\|<>/?？，。！]+)', replace, text)

@bp.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        return dict(unread_notification_count=current_user.new_notifications())
    return dict(unread_notification_count=0)

@bp.route('/albums/new', methods=['GET', 'POST'])
@login_required
def new_album():
    form = AlbumForm()
    if form.validate_on_submit():
        album = Album(title=form.title.data, description=form.description.data, 
                      privacy=form.privacy.data, allow_download=form.allow_download.data, author=current_user)
        db.session.add(album)
        db.session.commit()
        
        # Notify followers
        followers = current_user.followers.all()
        for follower in followers:
            follower.add_notification('new_album', current_user, album.id)
        db.session.commit()
        
        flash('相簿建立成功！')
        return redirect(url_for('main.album', id=album.id))
    return render_template('main/new_album.html', title='New Album', form=form)

@bp.route('/album/<int:id>', methods=['GET', 'POST'])
def album(id):
    album = Album.query.get_or_404(id)
    
    # Check if banned
    if album.is_banned and current_user.role != 'admin':
        flash('此內容因違反社群規範已被移除。')
        return redirect(url_for('main.index'))
        
    # Check permission
    # Public: Allow everyone
    # Private: Allow author only
    # Shared: Allow author (and friends logic later)
    if album.privacy != 'public':
        if not current_user.is_authenticated:
             flash('請登入以檢視此相簿。')
             return redirect(url_for('auth.login'))
             
        # Allow author
        if album.author == current_user:
            pass
        # Allow mutual friends for 'shared' albums
        elif album.privacy == 'shared' and current_user.is_mutual_following(album.author):
            pass
        # Allow specifically shared users (works for private albums too)
        elif current_user in album.shared_users:
            pass
        else:
            flash('您沒有權限檢視此相簿（需互為好友或被授權）。')
            return redirect(url_for('main.index'))
        
    upload_form = PhotoUploadForm()
    if upload_form.validate_on_submit() and current_user.is_authenticated:
        if upload_form.photos.data:
            for file in upload_form.photos.data:
                if file.filename == '':
                    continue
                    
                # Generate unique filename
                ext = os.path.splitext(file.filename)[1]
                filename = str(uuid.uuid4()) + ext
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                file.save(file_path)
                
                photo = Photo(album=album, uploader=current_user, 
                              filename=filename, original_filename=file.filename,
                              filesize=os.path.getsize(file_path))
                
                # Check for tags in album description (as a fallback or default for now)
                # Ideally, we should add a field to the upload form for tags
                if album.description:
                    tags = parse_tags(album.description)
                    for tag in tags:
                        photo.tags.append(tag)
                        
                db.session.add(photo)
            
            db.session.commit()
            
            # Notify followers (only once per upload batch, pointing to the album)
            followers = current_user.followers.all()
            for follower in followers:
                follower.add_notification('new_photo', current_user, album.id)
            db.session.commit()
            
            flash('照片上傳成功！')
            return redirect(url_for('main.album', id=id))
            
    # Sort photos by position (asc) then uploaded_at (desc), filtering banned ones
    photos = album.photos.filter((Photo.is_banned == False) | (Photo.is_banned == None)).order_by(Photo.position.asc(), Photo.uploaded_at.desc()).all()

    return render_template('main/album.html', title=album.title, album=album, upload_form=upload_form, photos=photos)

@bp.route('/album/<int:id>/reorder', methods=['POST'])
@login_required
def reorder_photos(id):
    album = Album.query.get_or_404(id)
    if album.author != current_user:
        return {'status': 'error', 'message': 'Permission denied'}, 403
        
    data = request.get_json()
    if not data or 'photo_ids' not in data:
        return {'status': 'error', 'message': 'Invalid data'}, 400
        
    photo_ids = data['photo_ids']
    
    # Update positions
    # Verify all photos belong to this album to prevent unauthorized modification
    # A more efficient way is to query all photos in this album and update
    
    photos_map = {p.id: p for p in album.photos}
    
    for index, photo_id in enumerate(photo_ids):
        photo_id = int(photo_id)
        if photo_id in photos_map:
            photos_map[photo_id].position = index
            
    db.session.commit()
    return {'status': 'success'}

@bp.route('/photo/<int:id>', methods=['GET', 'POST'])
def photo(id):
    photo = Photo.query.get_or_404(id)
    
    # Check if banned (photo or album)
    if (photo.is_banned or photo.album.is_banned) and current_user.role != 'admin':
        flash('此內容因違反社群規範已被移除。')
        return redirect(url_for('main.index'))
        
    # Permission check
    if photo.album.privacy != 'public':
        if not current_user.is_authenticated:
            flash('請登入以檢視此照片。')
            return redirect(url_for('auth.login'))
            
        if photo.album.author == current_user:
            pass
        elif photo.album.privacy == 'shared' and current_user.is_mutual_following(photo.album.author):
            pass
        elif current_user in photo.album.shared_users:
            pass
        else:
            flash('權限不足（需互為好友或被授權）。')
            return redirect(url_for('main.index'))
    
    form = CommentForm()
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        parent_id = request.args.get('parent_id')
        comment = Comment(content=form.content.data, author=current_user, photo=photo)
        if parent_id:
            parent = Comment.query.get(parent_id)
            if parent:
                comment.parent = parent
        
        db.session.add(comment)
        db.session.commit()
        
        # Notify photo uploader
        if photo.uploader != current_user:
            photo.uploader.add_notification('comment', current_user, photo.id)
            
        # Notify parent comment author if it's a reply
        if parent_id:
            parent = Comment.query.get(parent_id)
            if parent and parent.author != current_user and parent.author != photo.uploader:
                parent.author.add_notification('comment_reply', current_user, photo.id)

        # Notify Mentioned Users
        mentions = re.findall(r'@(\w+)', form.content.data)
        for username in set(mentions):
            user = User.query.filter_by(username=username).first()
            if user and user != current_user:
                 user.add_notification('mention', current_user, photo.id)
                
        db.session.commit()
        
        flash('留言已新增。')
        return redirect(url_for('main.photo', id=id))
        
    return render_template('main/photo.html', title=photo.filename, photo=photo, form=form)

@bp.route('/album/<int:id>/privacy', methods=['POST'])
@login_required
def update_album_privacy(id):
    album = Album.query.get_or_404(id)
    if album.author != current_user:
        flash('權限不足。')
        return redirect(url_for('main.index'))
    
    # Simple form processing without a full template
    privacy = request.form.get('privacy')
    if privacy in ['public', 'private', 'shared']:
        album.privacy = privacy
        
    # Checkbox for allow_download
    # If checked, value is 'y' or 'on'. If unchecked, it's missing.
    allow_download_val = request.form.get('allow_download')
    album.allow_download = (allow_download_val is not None)
    
    db.session.commit()
    flash('相簿設定已更新。')
    
    # Redirect back to where the user came from (likely the photo page)
    return redirect(request.referrer or url_for('main.album', id=id))

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # Pagination could be added here
    return render_template('main/user.html', user=user)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.intro = form.about_me.data
        current_user.liked_photos_privacy = form.liked_photos_privacy.data
        
        if form.avatar.data:
            file = form.avatar.data
            ext = os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + ext
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            current_user.avatar = filename
            
        db.session.commit()
        flash('您的個人資料已更新。')
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.intro
        form.liked_photos_privacy.data = current_user.liked_photos_privacy
    return render_template('main/edit_profile.html', title='編輯個人資料', form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'使用者 {username} 不存在。')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('您不能追蹤自己！')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    user.add_notification('follow', current_user, "")
    db.session.commit()
    flash(f'您已成功追蹤 {username}！')
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'使用者 {username} 不存在。')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('您不能取消追蹤自己！')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'您已停止追蹤 {username}。')
    return redirect(url_for('main.user', username=username))

@bp.route('/user/<username>/followers')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    users = user.followers.all()
    title = f'{username} 的追蹤者'
    return render_template('main/users_list.html', title=title, users=users)

@bp.route('/user/<username>/following')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    users = user.followed.all()
    title = f'{username} 正在追蹤'
    return render_template('main/users_list.html', title=title, users=users)

@bp.route('/album/<int:id>/delete', methods=['POST'])
@login_required
def delete_album(id):
    album = Album.query.get_or_404(id)
    if album.author != current_user and current_user.role != 'admin':
        flash('您沒有權限刪除此相簿。')
        return redirect(url_for('main.index'))
    
    # Delete physical files
    for photo in album.photos:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
    db.session.delete(album)
    db.session.commit()
    flash('相簿已刪除。')
    # If admin deleted someone else's album, go to index, otherwise profile
    if current_user.role == 'admin' and album.author != current_user:
        return redirect(url_for('main.index'))
    return redirect(url_for('main.user', username=current_user.username))

@bp.route('/photo/<int:id>/delete', methods=['POST'])
@login_required
def delete_photo(id):
    photo = Photo.query.get_or_404(id)
    album_id = photo.album.id
    if photo.uploader != current_user and current_user.role != 'admin':
        flash('您沒有權限刪除此照片。')
        return redirect(url_for('main.album', id=album_id))
    
    # Delete physical file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    db.session.delete(photo)
    db.session.commit()
    flash('照片已刪除。')
    return redirect(url_for('main.album', id=album_id))

@bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('您沒有權限進入管理員後台。')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    albums = Album.query.all()
    photos = Photo.query.all()
    pending_reports_count = Report.query.filter_by(status='pending').count()
    return render_template('main/admin_dashboard.html', users=users, albums=albums, photos=photos, pending_reports_count=pending_reports_count)

@bp.route('/admin/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        flash('權限不足。')
        return redirect(url_for('main.index'))
        
    user = User.query.get_or_404(id)
    if user == current_user:
        flash('您不能刪除自己的帳號。')
        return redirect(url_for('main.admin_dashboard'))
    
    for album in user.albums:
        for photo in album.photos:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                
    db.session.delete(user)
    db.session.commit()
    flash(f'使用者 {user.username} 已刪除。')
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/album/<int:id>/share', methods=['POST'])
@login_required
def share_album(id):
    album = Album.query.get_or_404(id)
    if album.author != current_user:
        flash('您沒有權限設定此相簿的共享。')
        return redirect(url_for('main.album', id=id))
        
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash(f'找不到使用者：{username}')
    elif user == current_user:
        flash('不需要將相簿分享給自己。')
    elif user in album.shared_users:
        flash(f'相簿已經分享給 {username} 了。')
    else:
        album.shared_users.append(user)
        db.session.commit()
        flash(f'已將相簿分享給 {username}。')
        
    return redirect(url_for('main.album', id=id))

@bp.route('/album/<int:id>/unshare', methods=['POST'])
@login_required
def unshare_album(id):
    album = Album.query.get_or_404(id)
    if album.author != current_user:
        flash('您沒有權限設定此相簿的共享。')
        return redirect(url_for('main.album', id=id))
        
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    
    if user and user in album.shared_users:
        album.shared_users.remove(user)
        db.session.commit()
        flash(f'已取消對 {user.username} 的分享。')
    else:
        flash('操作失敗。')
        
    return redirect(url_for('main.album', id=id))

@bp.route('/photo/<int:id>/like', methods=['POST'])
@login_required
def like_photo(id):
    photo = Photo.query.get_or_404(id)
    # Check permission (same as view)
    if photo.album.privacy != 'public':
        if photo.album.author != current_user and \
           not (photo.album.privacy == 'shared' and current_user.is_mutual_following(photo.album.author)) and \
           current_user not in photo.album.shared_users:
             # If user can't view, they can't like. Technically permission check is done in view but double check here.
             flash('您沒有權限。')
             return redirect(url_for('main.index'))

    current_user.like_photo(photo)
    if photo.uploader != current_user:
        photo.uploader.add_notification('like', current_user, photo.id)
    db.session.commit()
    # flash('按讚成功！') # Optional, maybe too noisy
    return redirect(url_for('main.photo', id=id))

@bp.route('/photo/<int:id>/unlike', methods=['POST'])
@login_required
def unlike_photo(id):
    photo = Photo.query.get_or_404(id)
    current_user.unlike_photo(photo)
    db.session.commit()
    return redirect(url_for('main.photo', id=id))

@bp.route('/notifications')
@login_required
def notifications():
    # Show all notifications, ordered by timestamp desc
    notifications = current_user.notifications.order_by(Notification.timestamp.desc()).all()
    # Mark all as read when visiting the page (optional, or can use a separate button)
    current_user.mark_notifications_read()
    return render_template('main/notifications.html', notifications=notifications)

@bp.route('/notifications/read/<int:id>')
@login_required
def mark_read(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id != current_user.id:
        return redirect(url_for('main.index'))
    notification.is_read = True
    db.session.commit()
    # Redirect logic based on type
    if notification.type in ['like', 'comment', 'comment_reply', 'mention']:
        return redirect(url_for('main.photo', id=int(notification.payload)))
    elif notification.type == 'follow':
        return redirect(url_for('main.user', username=notification.author.username))
    elif notification.type in ['new_album', 'new_photo']:
        return redirect(url_for('main.album', id=int(notification.payload)))
    
    return redirect(url_for('main.notifications'))

@bp.route('/search')
def search():
    q = request.args.get('q')
    if not q:
        return redirect(url_for('main.index'))
    
    # Search Albums (Public)
    albums = Album.query.filter(
        (Album.title.contains(q) | Album.description.contains(q)),
        Album.privacy == 'public',
        (Album.is_banned == False) | (Album.is_banned == None)
    ).all()
    
    # Search Users
    users = User.query.filter(User.username.contains(q)).all()
    
    # Search Photos (In Public Albums)
    photos = Photo.query.join(Album, Photo.album_id == Album.id).filter(
        Photo.original_filename.contains(q),
        Album.privacy == 'public',
        (Photo.is_banned == False) | (Photo.is_banned == None)
    ).all()
    
    return render_template('main/search_results.html', q=q, albums=albums, users=users, photos=photos)

@bp.route('/album/<int:id>/set_cover/<int:photo_id>', methods=['POST'])
@login_required
def set_album_cover(id, photo_id):
    album = Album.query.get_or_404(id)
    photo = Photo.query.get_or_404(photo_id)
    
    if album.author != current_user:
        flash('您沒有權限修改此相簿。')
        return redirect(url_for('main.index'))
        
    if photo.album_id != album.id:
        flash('該照片不屬於此相簿。')
        return redirect(url_for('main.album', id=id))
        
    album.cover_id = photo.id
    db.session.commit()
    flash('已將照片設為相簿封面。')
    
    return redirect(url_for('main.photo', id=photo_id))

@bp.route('/photo/<int:id>/edit_tags', methods=['POST'])
@login_required
def edit_photo_tags(id):
    photo = Photo.query.get_or_404(id)
    if photo.uploader != current_user and current_user.role != 'admin':
        flash('權限不足。')
        return redirect(url_for('main.photo', id=id))
    
    tags_str = request.form.get('tags', '')
    # If the user didn't include #, we should still handle it. 
    # But parse_tags expects #. Let's fix parse_tags or ensure the input has #.
    # Actually, we can pre-process tags_str to ensure words have # if they don't.
    
    # Or better: modify parse_tags to handle space/comma separated list if no # is found.
    # For now, let's keep it consistent: users enter tags with # or we add them.
    
    new_tags = parse_tags(tags_str)
    photo.tags = new_tags
    db.session.commit()
    flash('標籤已更新。')
    return redirect(url_for('main.photo', id=id))

@bp.route('/photo/<int:id>/download')
@login_required
def download_photo(id):
    photo = Photo.query.get_or_404(id)
    album = photo.album
    
    # 1. Access Check (Same as View Logic)
    has_access = False
    if album.privacy == 'public':
        has_access = True
    elif album.author == current_user:
        has_access = True
    elif album.privacy == 'shared' and current_user.is_mutual_following(album.author):
        has_access = True
    elif current_user in album.shared_users:
        has_access = True
        
    if not has_access:
        flash('您沒有權限下載此照片。')
        return redirect(url_for('main.index'))
        
    # 2. Download Permission Check
    can_download = False
    if album.author == current_user:
        can_download = True
    elif album.allow_download:
        can_download = True
        
    if not can_download:
        flash('此相簿不允許下載原圖。')
        return redirect(url_for('main.photo', id=id))

    # Serve file
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], photo.filename, as_attachment=True, download_name=photo.original_filename)

@bp.app_template_filter('linkify_mentions')
def linkify_mentions(text):
    def replace(match):
        username = match.group(1)
        user = User.query.filter_by(username=username).first()
        if user:
            return f'<a href="{url_for("main.user", username=username)}">@{username}</a>'
        return match.group(0)
    return re.sub(r'@(\w+)', replace, text)

@bp.route('/album/<int:id>/export')
@login_required
def export_album(id):
    album = Album.query.get_or_404(id)
    if album.author != current_user and current_user.role != 'admin':
        flash('您沒有權限匯出此相簿。')
        return redirect(url_for('main.album', id=id))
        
    # Create ZIP in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Prepare Metadata
        metadata = {
            'title': album.title,
            'description': album.description,
            'photos': []
        }
        
        # 2. Add Photos
        for photo in album.photos:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
            if os.path.exists(file_path):
                # Add file to ZIP (using original filename if possible, but keeping unique internally)
                # Structure: photos/<id>_<original_name>
                # Using photo.filename (UUID) for storage in ZIP is safer to avoid collisions, 
                # but user wants to backup. Let's store as unique name in zip and map in metadata.
                zip_path = f"photos/{photo.filename}"
                zf.write(file_path, zip_path)
                
                metadata['photos'].append({
                    'filename': photo.filename, # Internal name in ZIP
                    'original_filename': photo.original_filename,
                    'description': '' # Future proofing
                })
        
        # 3. Add Metadata file
        zf.writestr('metadata.json', json.dumps(metadata, ensure_ascii=False, indent=2))
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        download_name=f"album_export_{id}.zip",
        as_attachment=True
    )

@bp.route('/albums/import', methods=['GET', 'POST'])
@login_required
def import_album():
    form = ImportAlbumForm()
    if form.validate_on_submit():
        file = form.file.data
        try:
            with zipfile.ZipFile(file) as zf:
                # 1. Read Metadata
                if 'metadata.json' not in zf.namelist():
                    flash('無效的備份檔：找不到 metadata.json')
                    return redirect(url_for('main.import_album'))
                
                metadata = json.loads(zf.read('metadata.json').decode('utf-8'))
                
                # 2. Create Album
                album = Album(
                    title=f"{metadata.get('title', 'Imported Album')} (匯入)",
                    description=metadata.get('description', ''),
                    privacy='private', # Default to private for safety
                    author=current_user
                )
                db.session.add(album)
                db.session.flush() # Get ID
                
                # 3. Process Photos
                count = 0
                for photo_meta in metadata.get('photos', []):
                    zip_path = f"photos/{photo_meta['filename']}"
                    if zip_path in zf.namelist():
                        # Extract and restore
                        original_filename = photo_meta.get('original_filename', 'unknown.jpg')
                        # Generate new UUID filename to avoid collision
                        ext = os.path.splitext(original_filename)[1]
                        if not ext: ext = '.jpg'
                        new_filename = str(uuid.uuid4()) + ext
                        
                        target_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                        
                        # Write file
                        with open(target_path, 'wb') as f:
                            f.write(zf.read(zip_path))
                            
                        # Create DB record
                        photo = Photo(
                            filename=new_filename,
                            original_filename=original_filename,
                            album_id=album.id,
                            user_id=current_user.id
                        )
                        db.session.add(photo)
                        count += 1
                
                db.session.commit()
                flash(f'相簿匯入成功！共復原 {count} 張照片。')
                return redirect(url_for('main.album', id=album.id))
                
        except zipfile.BadZipFile:
            flash('無效的 ZIP 檔案。')
        except Exception as e:
            flash(f'匯入失敗：{str(e)}')
            
    return render_template('main/import_album.html', form=form)

@bp.route('/report', methods=['POST'])
@login_required
def report_content():
    target_type = request.form.get('type')
    target_id = request.form.get('id')
    reason = request.form.get('reason')
    
    if not all([target_type, target_id, reason]):
        flash('請填寫所有欄位。')
        return redirect(request.referrer)
        
    if reason == '其他':
        other_reason = request.form.get('other_reason')
        if not other_reason:
            flash('請填寫詳細檢舉原因。')
            return redirect(request.referrer)
        reason = f"其他：{other_reason}"
        
    report = Report(
        reporter=current_user,
        target_type=target_type,
        target_id=target_id,
        reason=reason
    )
    db.session.add(report)
    db.session.commit()
    flash('檢舉已送出，我們將盡快審核。')
    return redirect(request.referrer)

@bp.route('/admin/reports')
@login_required
def admin_reports():
    # Simple admin check (in real app use decorators)
    if current_user.role != 'admin':
        flash('權限不足。')
        return redirect(url_for('main.index'))
        
    reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).all()
    
    # Pre-fetch report targets for display
    report_items = []
    for r in reports:
        target = None
        if r.target_type == 'album':
            target = Album.query.get(r.target_id)
        elif r.target_type == 'photo':
            target = Photo.query.get(r.target_id)
        
        report_items.append({
            'report': r,
            'target': target
        })
        
    return render_template('main/admin_reports.html', report_items=report_items)

@bp.route('/admin/report/<int:id>/resolve', methods=['POST'])
@login_required
def resolve_report(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    report = Report.query.get_or_404(id)
    action = request.form.get('action') # 'ban' or 'dismiss'
    
    if action == 'ban':
        report.status = 'resolved'
        
        target_author = None
        target_name = ""
        
        # 1. Ban Content
        if report.target_type == 'album':
            album = Album.query.get(report.target_id)
            if album:
                album.is_banned = True
                target_author = album.author
                target_name = f"相簿「{album.title}」"
        elif report.target_type == 'photo':
            photo = Photo.query.get(report.target_id)
            if photo:
                photo.is_banned = True
                target_author = photo.uploader
                target_name = f"照片「{photo.original_filename}」"
                
                # Check if this photo is the album cover
                if photo.album.cover_id == photo.id:
                    # Find next not banned photo
                    next_cover = Photo.query.filter(
                        Photo.album_id == photo.album_id,
                        (Photo.is_banned == False) | (Photo.is_banned == None),
                        Photo.id != photo.id
                    ).order_by(Photo.position.asc(), Photo.uploaded_at.desc()).first()
                    
                    if next_cover:
                        photo.album.cover_id = next_cover.id
                    else:
                        photo.album.cover_id = None

        # 2. Notify Author
        if target_author:
            msg = f"您的{target_name}因違反社群規範（理由：{report.reason}）已被下架。"
            notification = Notification(
                user=target_author,
                author=current_user, # Admin
                type='system',
                payload=msg
            )
            db.session.add(notification)
            
        flash('內容已下架並通知作者。')
        
    elif action == 'dismiss':
        report.status = 'dismissed'
        flash('檢舉已駁回。')
        
    db.session.commit()
    return redirect(url_for('main.admin_reports'))

@bp.route('/tag/<name>')
def tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    
    # Query all photos with this tag
    # Filter public albums only and not banned photos
    photos = Photo.query.join(photo_tags).join(Album, Photo.album_id == Album.id).filter(
        photo_tags.c.tag_id == tag.id,
        Album.privacy == 'public',
        (Photo.is_banned == False) | (Photo.is_banned == None)
    ).order_by(Photo.uploaded_at.desc()).all()
    
    return render_template('main/tag_results.html', title=f'#{tag.name}', tag=tag, photos=photos)
            
