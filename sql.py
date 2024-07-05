from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# from models import db, Customer, Seller, Products, Cart, Wishlist
# from models import init_db
# from sqlalchemy.sql.expression import func,desc
db = SQLAlchemy()

class Seller(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50),unique = True, nullable=False)
    password_hash = db.Column(db.String(100),nullable = False)
    products = db.relationship('Products', backref = 'seller',lazy = True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    cart = db.relationship('Cart',backref = 'customer',lazy = True)
    cart = db.relationship('Wishlist',backref = 'customer',lazy = True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Products(db.Model):
    product_id = db.Column(db.Integer,  primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'),nullable = False)
    product_name = db.Column(db.String(150), nullable = False)
    product_description = db.Column(db.Text,nullable = False)
    product_price = db.Column(db.Float,nullable=False)
    product_category = db.Column(db.String(150), nullable = False)
    product_cart = db.relationship('Cart', backref = 'products', lazy =True)
    product_wish = db.relationship('Wishlist', backref = 'products', lazy =True)

    image1 = db.Column(db.String(150),nullable = False)
    image2 = db.Column(db.String(150),nullable = True)
    image3 = db.Column(db.String(150),nullable = True)
    image4 = db.Column(db.String(150),nullable = True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    added_product = db.Column( db.Integer, db.ForeignKey('products.product_id'),nullable=False)
    
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    added_product = db.Column( db.Integer, db.ForeignKey('products.product_id'),nullable=False)
    

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


@app.route('/add_to_wishlist/<string:product_id>', methods=['GET', 'POST'])
def add_to_wishlist(product_id):
    if check_customer_session():
        customer_name = session.get('username')
        customer = Customer.objects(username=customer_name).first()
        product = Products.objects(id=ObjectId(product_id)).first()

        if not customer:
            flash("Something went wrong. Please try again.")
            return redirect(url_for('login'))
        if not product:
            flash("Product doesn't exist.")
            return redirect(url_for('login'))

        if product.id in customer.wishlist:
            flash("Product already exists in the wishlist.")
            return redirect(url_for('login'))
        else:
            customer.wishlist.append(product.id)
            customer.save()
            flash("Product added to the wishlist!")
            return redirect(url_for('index'))  # Redirect to a valid page after adding to the wishlist
    else:
        return redirect(url_for('login'))


        <!-- <i class="far fa-heart heart_button" onclick='event.stopPropagation(); AddToWishlist("{{product._id}}")'></i> -->'''.venv\



            