
import sys
import os
import shutil
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import User, Album, Photo, Like, Comment, Notification

def verify_fix():
    app = create_app()
    
    # Use a temporary database or test environment if possible, 
    # but since this is a manual run on dev env, we will be careful.
    # We will create a specific user for testing and delete them.
    
    TEST_USERNAME = 'test_deletion_user'
    TEST_EMAIL = 'test_deletion@example.com'
    TEST_FILENAME = 'test_delete_photo.txt'
    
    with app.app_context():
        # Clean up previous runs
        user = User.query.filter_by(username=TEST_USERNAME).first()
        if user:
            print(f"Cleaning up existing user {TEST_USERNAME}")
            try:
                # We can't use route logic here easily without mocking request,
                # but we can test the model cascade directly.
                db.session.delete(user)
                db.session.commit()
            except Exception as e:
                print(f"Cleanup failed (might be expected if cascade broken): {e}")
                db.session.rollback()
                # Try to manually clean unrelated items if needed, but let's proceed.

        # 1. Create User
        print(f"Creating user {TEST_USERNAME}...")
        user = User(username=TEST_USERNAME, email=TEST_EMAIL)
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # 2. Create Album & Photo (simulate file)
        print("Creating album and photo with file...")
        album = Album(title='Test Album', author=user)
        db.session.add(album)
        db.session.commit()
        
        # Create dummy file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], TEST_FILENAME)
        with open(file_path, 'w') as f:
            f.write('dummy content')
            
        photo = Photo(album=album, uploader=user, filename=TEST_FILENAME, original_filename='test.jpg')
        db.session.add(photo)
        db.session.commit()
        photo_id = photo.id
        
        # 3. Create dependent data (Like, Comment)
        # Verify self-like or like by others. 
        # If we delete USER, their likes on OTHER photos should disappear.
        # If we delete USER, their own photos (and likes on them) should disappear.
        
        print("Creating likes and comments...")
        # Like their own photo
        user.like_photo(photo)
        
        # Comment on their own photo
        comment = Comment(content='Test comment', author=user, photo=photo)
        db.session.add(comment)
        db.session.commit()
        
        # 4. Verify data exists
        assert User.query.get(user_id) is not None
        assert Photo.query.get(photo_id) is not None
        assert Like.query.filter_by(user_id=user_id, photo_id=photo_id).count() == 1
        assert Comment.query.filter_by(user_id=user_id).count() == 1
        assert os.path.exists(file_path)
        print("Data creation verified.")
        
        # 5. Test Deletion (Model Cascade)
        # We are testing the MODEL cascade here first. 
        # If this fails, the route will verify fail too.
        print("Deleting user via DB session...")
        try:
            db.session.delete(user)
            db.session.commit()
            print("DB Deletion successful!")
        except Exception as e:
            print(f"DB Deletion FAILED: {e}")
            return

        # 6. Verify Cascade Results
        assert User.query.get(user_id) is None, "User should be gone"
        assert Album.query.filter_by(author_id=user_id).count() == 0, "User's albums should be gone"
        assert Photo.query.get(photo_id) is None, "User's photos should be gone"
        assert Like.query.filter_by(user_id=user_id).count() == 0, "User's likes should be gone"
        assert Comment.query.filter_by(user_id=user_id).count() == 0, "User's comments should be gone"
        
        print("Cascade verification passed.")
        
        # 7. Note on file deletion
        # This script only tests DB cascade. The File deletion logic is in the route.
        # Since we ran DB delete directly, the file should STILL EXIST (because route logic wasn't run).
        # This confirms that if DB transaction works, we still need the route logic to clean files.
        if os.path.exists(file_path):
            print("File still exists as expected (since we bypassed route). Cleaning up manually.")
            os.remove(file_path)
        else:
            print("WARNING: File is gone? It shouldn't be if we only did DB delete.")
            
        print("Verification complete.")

if __name__ == '__main__':
    verify_fix()
