from app import app, db, Shop, Product  # Add Product import

with app.app_context():
    db.create_all()
    print("Database created with Shop and Product tables!")
