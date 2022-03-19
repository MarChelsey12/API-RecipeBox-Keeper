from app import db, login
from flask_login import UserMixin
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(200))
    avatar = db.Column(db.Integer, default='')
    recipes = db.relationship('Recipe', backref='uploaded', lazy="dynamic")
    box = db.relationship('Recipe',
                    secondary = 'collection',
                    backref='card',
                    lazy='dynamic',
                    )

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'
        
    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    def from_dict(self, data):
        self.username = data['username']
        self.email = data['email']
        self.password = self.hash_password(data['password'])
        self.avatar = data['avatar']

    def save(self):
        '''
            Saves user
        '''
        db.session.add(self)
        db.session.commit()

    def add(self, recipe):
        '''
            Add a new Recipe to collection
        '''
        self.box.append(recipe)
        db.session.commit()

    def remove(self, recipe):
        '''
            Removes recipe from collection
        '''
        self.box.remove(recipe)
        db.session.commit()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    ingredients = db.Column(db.Text)
    instructions = db.Column(db.Text)
    cook = db.Column(db.DateTime, default=dt.utcnow)
    servings = db.Column(db.Integer)
    rating = db.Column(db.String(10))
    img = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=dt.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.username'))

    def from_dict(self, data):
        self.title = data['title']
        self.ingredients = data['ingredients']
        self.instructions = data['instructions']
        self.cook = data['cook']
        self.servings = data['servings']
        self.rating = data['rating']
        self.img = data['img']
        self.created_by = data['created_by']

    def to_dict(self):
        return{
        "title":self.title,
        "ingredients":self.ingredients,
        "instructions":self.instructions,
        "cook":self.cook,
        "servings":self.servings,
        "rating":self.rating,
        "img":self.img,
        "created_by":self.created_by,
        }
        

    def save(self):
        db.session.add(self)
        db.session.commit()

class Collection(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return f'<Collection: {self.recipe_id} | {self.user_id}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()