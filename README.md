# Photo Sharing Platform - Setup Guide

## Prerequisites
- Python 3.8+
- MySQL Server (Ensure it is running and you have a database named `photo_platform`)

## Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Database Configuration**:
    - Open `config.py` in the root directory.
    - Check the `SQLALCHEMY_DATABASE_URI`. It defaults to: `mysql+mysqlconnector://root:password@localhost/photo_platform`
    - **IMPORTANT**: Update the `root:password` with your actual MySQL username and password.

3.  **資料庫初始化**:
    在終端機執行以下指令來建立資料庫資料表：
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```
    *(注意：如果找不到 `flask` 指令，請確保您在虛擬環境中，或使用 `python -m flask ...`)*

4.  **Run the Application**:
    ```bash
    python run.py
    ```

5.  **Access the System**:
    - Open your browser and go to: `http://127.0.0.1:5000`

## Features Implemented
- **User System**: Register, Login, Logout.
- **Album Management**: Create public/private albums.
- **Photo Upload**: Multi-file upload to albums.
- **Gallery**: Public timeline on homepage.
- **Interactions**: Comments on photos.
