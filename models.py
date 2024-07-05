from mongoengine import Document, StringField, ListField, ReferenceField, FloatField, ObjectIdField
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class Seller(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    added_products = ListField(ReferenceField('Products'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    wishlist = ListField(ReferenceField('Products'))
    cart_products = ListField(ReferenceField('Products'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Products(Document):
    seller_id = ReferenceField('Seller')
    product_name = StringField(required=True)
    product_description = StringField()
    product_price = FloatField(required=True)
    product_category = StringField()
    images = ListField(StringField(), required=True)


