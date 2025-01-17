Here’s a summarized version of the README:

---

## Chrysalis: Recipe and Mental Health Platform

Chrysalis is a website combining recipes and mental health resources. It provides user-friendly functionality and a secure admin dashboard for managing content.

### Features

- **User Features**: Explore recipes, interact with comments/likes/reviews, access mental health resources, and contact admins.
- **Admin Features**: Manage users, recipes, reviews, comments, and contact messages via a dashboard.

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up a PostgreSQL database:
   ```
   Host: localhost
   Database: Chrysalis
   User: postgres
   Password: butterfly
   ```
4. Run the app:
   ```bash
   python app.py
   ```

### Usage

- Visit `http://localhost:5000` to access the app.
- Use admin routes (e.g., `/admin`) for platform management.

### Project Structure

```
├── app.py          # Main application
├── templates/      # HTML templates
├── static/         # Static assets
├── requirements.txt# Dependencies
└── README.md       # Documentation
```

### Security Notes

- Update `app.secret_key` with a secure value.
- Use hashed passwords for authentication.



---
