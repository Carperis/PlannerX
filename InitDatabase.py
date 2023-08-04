    from web import app, db
    app.app_context().push()
    db.create_all()