workers = 3
bind = "unix:/tmp/gunicorn.sock"
module = "app:app"
