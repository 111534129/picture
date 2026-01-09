from app import create_app, db
from app.models import User
import sys

app = create_app()

def promote_to_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.role = 'admin'
            db.session.commit()
            print(f"成功將使用者 {username} 設為管理員 (admin)！")
        else:
            print(f"找不到使用者: {username}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方式: python promote_admin.py <username>")
    else:
        promote_to_admin(sys.argv[1])
