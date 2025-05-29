from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shops.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

'''

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    image = db.Column(db.String(100))

    def __repr__(self):
        return f'<Shop {self.name}>'

'''

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    image = db.Column(db.String(100))
    # Relationship to products
    products = db.relationship('Product', backref='shop', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Shop {self.name}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    nr_in_stock = db.Column(db.Integer, nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'




@app.route('/')
def index():
    shops = Shop.query.all()
    return render_template('index.html', shops=shops)

@app.route('/shop/<int:shop_id>')
def shop_detail(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    return render_template('shop_detail.html', shop=shop)


# ... existing routes ...

@app.route('/admin/shop/<int:shop_id>/add_product', methods=['GET', 'POST'])
def add_product(shop_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    shop = Shop.query.get_or_404(shop_id)
    
    if request.method == 'POST':
        new_product = Product(
            name=request.form['name'],
            sell_price=float(request.form['sell_price']),
            buy_price=float(request.form['buy_price']),
            nr_in_stock=int(request.form['nr_in_stock']),
            shop_id=shop_id
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('shop_detail', shop_id=shop_id))
    
    return render_template('add_product.html', shop=shop)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(product_id)
    shop = product.shop
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.sell_price = float(request.form['sell_price'])
        product.buy_price = float(request.form['buy_price'])
        product.nr_in_stock = int(request.form['nr_in_stock'])
        db.session.commit()
        return redirect(url_for('shop_detail', shop_id=shop.id))
    
    return render_template('edit_product.html', product=product)



@app.route('/admin/product/delete/<int:product_id>')
def delete_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(product_id)
    shop_id = product.shop.id
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('shop_detail', shop_id=shop_id))





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == os.getenv('ADMIN_USER') and password == os.getenv('ADMIN_PASS'):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    shops = Shop.query.all()
    return render_template('admin.html', shops=shops)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_shop():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_shop = Shop(
            name=request.form['name'],
            description=request.form['description'],
            location=request.form['location'],
            image=request.form['image']
        )
        db.session.add(new_shop)
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('add_shop.html')

@app.route('/admin/edit/<int:shop_id>', methods=['GET', 'POST'])
def edit_shop(shop_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    shop = Shop.query.get_or_404(shop_id)
    
    if request.method == 'POST':
        shop.name = request.form['name']
        shop.description = request.form['description']
        shop.location = request.form['location']
        shop.image = request.form['image']
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('edit_shop.html', shop=shop)

@app.route('/admin/delete/<int:shop_id>')
def delete_shop(shop_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
