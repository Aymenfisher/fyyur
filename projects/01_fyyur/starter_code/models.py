from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__='Show'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    artist_id=db.Column(db.Integer,db.ForeignKey("Artist.id"),primary_key=True)
    venue_id=db.Column(db.Integer,db.ForeignKey("Venue.id"),primary_key=True)
    start_time=db.Column(db.DateTime)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(300))
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    venues=db.relationship('Show',backref='venue')

    # TODO DONE: implement any missing fields, as a database migration using Flask-Migrate  DON

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    seeking_venue= db.Column(db.Boolean)
    seeking_description= db.Column(db.String())
    artists=db.relationship('Show',backref='artist')

    # TODO: DONE implement any missing fields, as a database migration using Flask-Migrate DONE

# TODO DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration. DONE
