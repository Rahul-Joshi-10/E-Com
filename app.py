import os,random,string,uuid,random  # UUID (Universally Unique Identifier)
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_pymongo import PyMongo
from mongoengine import connect
from bson import ObjectId
from werkzeug.utils import secure_filename
from models import Products,Seller,Customer

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/E_comm"
connect('E_comm', host='localhost', port=27017)
mongo = PyMongo(app)
app.config['uploaded_images'] = '.venv/website/static/img/uploaded_images'
app.secret_key = 'TheRJ@123'

if not os.path.exists(app.config['uploaded_images']):
    os.makedirs(app.config['uploaded_images'])


def check_customer_session():
    if not session.get('username') or session.get('is_seller') or not session.get('customer_id'):
        flash('Please login again session has Expired','error')
        return redirect(url_for('login'))
    else:
        return True

def check_seller_session():
    if not session.get('username') or not session.get('is_seller') or not session.get('seller_id'):
        flash('Please login again session has Expired','error')
        return redirect(url_for('login'))
    else:
        return True

@app.route('/')
def index():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    products = Products.objects.aggregate([{"$sample": {"size": 5}}])
    products = list(products)
    wishlist=[]
    cart=[]
    if check_customer_session:
        print("ajinkya is here")
        customer_name = session.get('username')
        customer = Customer.objects(username=customer_name).first()
        if not customer:
            flash("something went wrong please try again...")           
        else:
            if customer.wishlist:
                for item in customer.wishlist:
                    wishlist.append(item.id)
            if customer.cart_products:
                for item in customer.cart_products:
                    cart.append(item.id)

    return render_template('index.html', products = products, random_string = random_string, customer_wishlist = wishlist , customer_cart = cart)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        customer = Customer.objects(username=username).first()
        seller = Seller.objects(username=username).first()
        
        if customer and customer.check_password(password):
                session['username'] = username
                session['is_seller']= False
                session['customer_id'] = str(customer.id)
                flash('Successfully logged in..........','success')
                return redirect(url_for('index'))
        elif seller and seller.check_password(password):
                session['username'] = username
                session['is_seller']= True
                session['seller_id']=str(seller.id)
                flash('Successfully logged in..........','success')
                return redirect(url_for('index'))
        else:
            flash('Please enter the valid username and password')
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if len(username) > 8 and len(password) > 8:
            if role == 'customer':
                user = Customer.objects(username=username).first()
                if user:
                    flash('User already exists.', 'error')
                    return render_template('login.html')
                new_user = Customer(username=username)
                new_user.set_password(password)
                session['is_seller'] = False  
            elif role == 'seller':
                user = Seller.objects(username=username).first()
                if user:
                    flash('User already exists.', 'error')
                    return render_template('login.html')
                new_user = Seller(username=username)
                new_user.set_password(password)
                session['is_seller'] = True
                        
            new_user.save()
            session['username'] = username
            if session['is_seller']:
                session['seller_id'] = str(new_user.id)
                # print(new_user.id)
            else:
                session['customer_id'] = str(new_user.id)
                # print(new_user.id)

            flash('You have signed up successfully.', 'success')      
            return redirect(url_for('index'))
        else:
            flash('Username and password must be at least 8 characters long.', 'error')
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_seller', None)
    session.pop('seller_id', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/product_details/<string:product_id>',  methods=['GET'])
def product_details(product_id):
    if check_customer_session:
        product = Products.objects(id=ObjectId(product_id)).first()
        return render_template('product_details.html',product=product)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if check_seller_session():
        if request.method == 'POST':
            product_name = request.form['product_name']
            product_price = request.form['product_price']
            product_description = request.form['product_details']
            product_category = request.form['product_category']

            if 'product_image1' not in request.files or request.files['product_image1'].filename == '':
                flash('At least one Product Image is required.', 'error')
                return render_template('add_product.html')

            images = []
            for file_key in ['product_image1', 'product_image2', 'product_image3', 'product_image4']:
                file = request.files.get(file_key)
                if file and file.filename != '':
                    unique_filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")   # UUID (Universally Unique Identifier)
                    filepath = os.path.join(app.config['uploaded_images'], unique_filename)
                    file.save(filepath)
                    images.append(unique_filename)

            seller_id = session.get('seller_id')
            seller = Seller.objects(id=ObjectId(seller_id)).first()

            if seller:
                new_product = Products(
                    seller_id=seller_id,
                    product_name=product_name,
                    product_description=product_description,
                    product_price=product_price,
                    product_category=product_category,
                    images=images
                )
                new_product.save()
                seller.added_products.append(new_product.id)
                seller.save()
                flash('Product added successfully...!!!', 'success')
                return redirect(url_for('index'))
        return render_template('add_product.html')

@app.route('/my_product')
def my_product():
    if check_seller_session():
        seller_id = session.get('seller_id')
        seller = Seller.objects(id=ObjectId(seller_id)).first()
        if not seller:
            flash("Seller Not Found..!!")
            return redirect(url_for('login'))
        products = [item for item in seller.added_products] 
        return render_template('my_product.html', my_products=products)

@app.route('/edit_product/<string:product_id>', methods=['POST'])
def edit_product(product_id):
    if check_seller_session():
        seller_id = session.get('seller_id')
        seller = Seller.objects(id=ObjectId(seller_id)).first()
        if not seller:
            flash("Seller does not exist..!!")
            return redirect(url_for('index'))

        product = Products.objects(id=ObjectId(product_id)).first()
        if not product:
            return redirect(url_for('my_product'))

        if request.method == 'POST':
            product.product_name = request.form['product_name']
            product.product_price = request.form['product_price']
            product.product_description = request.form['product_description']
            product.product_category = request.form['product_category']

            product.images = []
            for file_key in ['product_image1', 'product_image2', 'product_image3', 'product_image4']:
                file = request.files.get(file_key)
                if file and file.filename != '':
                    unique_filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    filepath = os.path.join(app.config['uploaded_images'], unique_filename)
                    file.save(filepath)
                    product.images.append(unique_filename)
            product.save()
            flash('Product updated successfully', 'success')
            return redirect(url_for('my_product'))
        return render_template('edit_product.html', product=product._id)
    else:
        flash("Session expired, please login again.")
        return redirect(url_for('login'))

@app.route('/delete_product/<string:product_id>', methods=['POST'])
def delete_product(product_id):
    if check_seller_session():
        seller_id = session.get('seller_id')
        seller = Seller.objects(id=ObjectId(seller_id)).first()
        if not seller:
            return jsonify({"status": "error", "message": "Seller not found..!!"}), 404

        product = Products.objects(id=ObjectId(product_id)).first()
        if not product:
            return jsonify({"status": "error", "message": "Product not found..!!"}), 404

        # Remove product from seller's added products
        seller.update(pull__added_products=product.id)
        seller.save()

        # Delete product from database
        product.delete()
        return jsonify({"status": "success", "message": "Product deleted successfully..!!"}), 200
    else:
        return jsonify({"status": "error", "message": "Session expired, please login again."}), 401


@app.route('/show_wishlist')
def show_wishlist():
    if check_customer_session():
        customer_id = session.get('customer_id')
        customer = Customer.objects(id=ObjectId(customer_id)).first()
        if not customer:
            flash("Customer not found...")
            return redirect(url_for('login'))
        wishlist = customer.wishlist
        return render_template('wishlist.html', wish_list = wishlist) 

@app.route('/check_wishlist/<string:product_id>', methods=['POST'])
def check_wishlist(product_id):
    if check_customer_session():
        customer_name = session.get('username')
        customer = Customer.objects(username=customer_name).first()
        product = Products.objects(id=ObjectId(product_id)).first() 
        if not customer:
            return jsonify({"status": "error", "message": "Customer not found"}), 404
        if not product:
            return jsonify({"status": "error", "message": "Product doesn't exist"}), 404
        for item in customer.wishlist:
            if item.id==product.id : 
                customer.update(pull__wishlist=product.id)  
                customer.save()
                return jsonify({"status": "success", "message": "Product removed from wishlist", "product_id": str(product.id)}), 200
        customer.wishlist.append(product.id)
        customer.save()
        return jsonify({"status": "success", "message": "Product added to wishlist", "product_id": str(product.id)}), 200
    return jsonify({"status": "error", "message": "Not authenticated"}), 401

    


@app.route('/add_to_cart/<string:product_id>', methods=['GET','POST'])
def add_to_cart(product_id):
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

        if product in customer.cart_products:
            flash("Product already exists in the cart.")
            return None
        else:
            customer.cart_products.append(product)
            customer.save()
            flash("Product added to the cart!")
            return redirect(url_for) # Redirect to a valid page after adding to the wishlist
    else:
        return redirect(url_for('login'))

            

@app.route('/remove_from_cart/<string:product_id>',  methods=['GET', 'POST'])
def remove_form_cart(product_id):
    if check_customer_session():
        customer_id=session.get('customer_id')
        customer_name = session.get('username')
        if customer_id and customer_name:
            customer = Customer.objects(id=ObjectId(customer_id)).first()
            if not customer:
                flash("Session has expired, Please Login again")
                redirect(url_for('login'))
        else:
            flash("session has expired please login again")
            redirect(url_for('login'))

        product = product.objects(id=ObjectId(product_id)).frist()
        if not product:
            flash("Product not found..!!")
            retrun(url_for('show_wishlist'))

        if product in customer.cart_products:
            customer.update(pull_cart_product=product)
            flash("Product Remove Successfully !")
        else:
            flash("Product Not found In Wishlist !")
    else:
        redirect(url_for('login'))

@app.route('/show_cart')
def show_cart():
    if check_customer_session():
        customer_id = session.get('customer_id')
        customer = Customer.objects(id=ObjectId(customer_id)).first()
        
        if not customer:
            flash('Customer not found. Please log in again.')
            return redirect(url_for('login'))
        
        cart = customer.cart_products
        return render_template('show_cart.html', cart_products=cart)
    return redirect(url_for('login'))

@app.route('/shop')
def shop():
    return 

@app.route('/contact')
def contact():
    return 

if __name__ == "__main__":
    app.run(debug=True)
