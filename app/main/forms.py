from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, MultipleFileField, FileField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired

class AlbumForm(FlaskForm):
    title = StringField('相簿標題', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('描述')
    privacy = SelectField('隱私設定', choices=[('public', '公開'), ('private', '私密'), ('shared', '僅好友')])
    allow_download = BooleanField('允許訪客下載原圖', default=True)
    submit = SubmitField('建立相簿')

class ImportAlbumForm(FlaskForm):
    file = FileField('選擇備份檔 (.zip)', validators=[
        FileRequired(),
        FileAllowed(['zip'], '僅支援 ZIP 格式！')
    ])
    submit = SubmitField('開始匯入')

class PrivacyUpdateForm(FlaskForm):
    privacy = SelectField('隱私設定', choices=[('public', '公開'), ('private', '私密'), ('shared', '僅好友')])
    submit = SubmitField('更新設定')

class EditProfileForm(FlaskForm):
    username = StringField('使用者名稱', validators=[DataRequired(message='此欄位為必填')])
    about_me = TextAreaField('個人簡介', validators=[Length(min=0, max=140)])
    avatar = FileField('上傳頭像', validators=[FileAllowed(['jpg', 'png'], '僅支援圖片格式！')])
    liked_photos_privacy = SelectField('按讚內容隱私', choices=[('public', '公開'), ('shared', '僅好友'), ('private', '僅自己')])
    submit = SubmitField('更新資料')

class PhotoUploadForm(FlaskForm):
    # Support multiple files
    photos = MultipleFileField('上傳照片', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], '僅支援圖片格式！')
    ])
    submit = SubmitField('上傳')

class CommentForm(FlaskForm):
    content = TextAreaField('留言', validators=[DataRequired()])
    submit = SubmitField('送出留言')
