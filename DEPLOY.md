# Deployment Guide

## Prerequisites
- Python 3.10+
- A server (VPS, cloud instance, etc.)
- A domain name pointed to your server
- PostgreSQL (recommended for production)

## Setup

### 1. Clone and install
```bash
git clone https://github.com/JamesMoore2090/beach-app-.git
cd beach-app-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary  # production extras
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your real values
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Initialize database
```bash
export FLASK_CONFIG=prod
source .env
python create_db.py
```

### 4. Run with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

### 5. Nginx reverse proxy (recommended)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/beach-app-/app/static;
    }

    client_max_body_size 16M;
}
```

### 6. HTTPS with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 7. Birthday email cron job
```bash
crontab -e
# Add this line to check birthdays daily at 8am:
0 8 * * * cd /path/to/beach-app- && source venv/bin/activate && source .env && flask check-birthdays
```

## Updating
```bash
cd /path/to/beach-app-
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart beach-app  # if using systemd
```
