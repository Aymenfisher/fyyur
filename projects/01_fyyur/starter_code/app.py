#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO DONE: connect to a local postgresql database 
migrate=Migrate(app,db)
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
    genres = db.Column(db.String())
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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: DOONE  replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  cities=Venue.query.distinct(Venue.city).all()
  data=[]
  for c in cities:
    city_venues=Venue.query.filter(Venue.city==c.city).all()
    d={
      "city":c.city,
      "state":c.state,
      "venues":[]
    }
    for cc in city_venues:
      venues_dict={
        "id":cc.id,
        "name":cc.name,
        "num_upcoming_shows":str(len(Show.query.filter(Show.venue_id==cc.id,Show.start_time>datetime.now()).all()))
      }
      d['venues'].append(venues_dict)
    data.append(d)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO:DONE  implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  seeking=str(request.form.get('search_term')).lower()
  venues_response=Venue.query.filter(Venue.name.ilike('%{}%'.format(seeking))).all()
  response={
    "count": len(venues_response),
    "data": []
  }
  for v in venues_response:
    response["data"].append({
      "id":v.id,
      "name":v.name,
      "num_upcoming_shows":len(Show.query.filter(Show.venue_id==v.id).all())
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: DONE replace with real venue data from the venues table, using venue_id
  venues=Venue.query.all()
  datas=[]
  for venue in venues:
    venue_shows=Show.query.join(Venue,Show.venue_id==venue.id).all() #using join
    past_list=[i for i in venue_shows if i.start_time<datetime.now()]
    upcoming_list=[i for i in venue_shows if i.start_time>datetime.now()]
    d={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres[1:-1].split(','), #genres is a required field, even its not , it will return empty string, this will work.
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(past_list),
    "upcoming_shows_count": len(upcoming_list), 
    }
    for s in past_list:
      pp={
        "artist_id":s.artist_id,
        "artist_name": Artist.query.filter(Artist.id==s.artist_id).all()[0].name,
        "artist_image_link":Artist.query.filter(Artist.id==s.artist_id).all()[0].image_link,
        "start_time":str(s.start_time)
      }
      d["past_shows"].append(pp)
    for s in upcoming_list:
      uu={
        "artist_id":s.artist_id,
        "artist_name": Artist.query.filter(Artist.id==s.artist_id).all()[0].name,
        "artist_image_link":Artist.query.filter(Artist.id==s.artist_id).all()[0].image_link,
        "start_time":str(s.start_time)
      }
      d["upcoming_shows"].append(uu)
    datas.append(d)
  data = list(filter(lambda d: d['id'] == venue_id, datas))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  err=False
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  new_venue=Venue(name=form.name.data,city=form.city.data,state=form.state.data,address=form.address.data,image_link=form.image_link.data,
  genres=form.genres.data,facebook_link=form.facebook_link.data,website_link=form.website_link.data,seeking_talent=form.seeking_talent.data,
  seeking_description=form.seeking_description.data)
  try:
    if form.validate_on_submit():
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + form.name.data + ' was successfully listed!') # on successful db insert, flash success
    else:
      flash('An error occurred. Venue could not be listed.') #on unsuccessful db insert, flash an error instead.
  except:
    err=True
    db.session.rollback()
  finally:
    if err:
      flash('An error occurred. Venue  could not be listed.') #on unsuccessful db insert, flash an error instead.
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE','GET','POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Show.query.filter(Show.venue_id==venue_id).delete()
    Venue.query.filter(Venue.id==venue_id).delete()
    db.session.commit()
  except:
    flash('Could not delete venue, an error occured')
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist=Artist.query.all()
  data=[]
  for a in artist:
    data.append({
      "id": a.id,
      "name": a.name
    }
    )
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  seeking=str(request.form.get('search_term')).lower()
  artists_found=Artist.query.filter(Artist.name.ilike('%{}%'.format(seeking))).all()
  response={
    "count": len(artists_found),
    "data": []
  }
  for a in artists_found:
    response["data"].append({
      "id":a.id,
      "name":a.name,
      "num_upcoming_shows":len(Show.query.filter(Show.artist_id==a.id).all())
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  theartists=Artist.query.get(artist_id)
  venues=Venue.query.all()
  artist_shows=Show.query.join(Artist,Show.artist_id==artist_id).all()
  past_shows=[i for i in artist_shows if i.start_time<datetime.now()]
  upcoming_shows=[i for i in artist_shows if i.start_time>datetime.now()]
  data={
    "id":theartists.id,
    "name":theartists.name,
    "genres":theartists.genres[1:-1].split(','),
    "city":theartists.city,
    "state":theartists.state,
    "phone":theartists.phone,
    "website":theartists.website_link,
    "facebook_link":theartists.facebook_link,
    "seeking_venue":theartists.seeking_venue,
    "seeking_description":theartists.seeking_description,
    "image_link":theartists.image_link,
    "past_shows":[],
    "upcoming_shows": [],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    }
  for p in past_shows:
    pdata={
      "venue_id":p.venue_id,
      "venue_name":Venue.query.filter(Venue.id==p.venue_id).all()[0].name,
      "venue_image_link":Venue.query.filter(Venue.id==p.venue_id).all()[0].name,
      "start_time":str(p.start_time)
    }
    data["past_shows"].append(pdata)
  for p in upcoming_shows:
    udata={
      "venue_id":p.venue_id,
      "venue_name":Venue.query.filter(Venue.id==p.venue_id).all()[0].name,
      "venue_image_link":Venue.query.filter(Venue.id==p.venue_id).all()[0].name,
      "start_time":str(p.start_time)
    }
    data["upcoming_shows"].append(udata)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  theartist=Artist.query.filter(Artist.id==artist_id).all()[0]
  artist={
    "id": artist_id,
    "name": theartist.name,
    "genres": theartist.genres,
    "city": theartist.city,
    "state": theartist.state,
    "phone": theartist.phone,
    "website": theartist.website_link,
    "facebook_link": theartist.facebook_link,
    "seeking_venue": theartist.seeking_venue,
    "seeking_description": theartist.seeking_description,
    "image_link": theartist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form=ArtistForm()
  artist=Artist.query.get(artist_id)
  try:
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.image_link=form.image_link.data
      artist.genres=form.genres.data
      artist.facebook_link=form.facebook_link.data
      artist.website_link=form.website_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      db.session.commit()
  except:
      db.session.rollback()
      flash('Could not update Artist, an error occured')
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id)) 

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  thevenue=Venue.query.get(venue_id)
  venue={
    "id": thevenue.id,
    "name": thevenue.name,
    "genres": thevenue.genres,
    "address": thevenue.address,
    "city": thevenue.city,
    "state": thevenue.state,
    "phone": thevenue.phone,
    "website": thevenue.website_link,
    "facebook_link": thevenue.facebook_link,
    "seeking_talent": thevenue.seeking_talent,
    "seeking_description": thevenue.seeking_description,
    "image_link": thevenue.image_link
  }
  # TODO Done: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO:Done take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form=VenueForm()
  venue=Venue.query.get(venue_id)
  try:
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.address=form.address.data
      venue.phone=form.phone.data
      venue.image_link=form.image_link.data
      venue.genres=form.genres.data
      venue.facebook_link=form.facebook_link.data
      venue.website_link=form.website_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      db.session.commit()
  except:
    db.session.rollback()
    flash('Could not update the venue , an error occured')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  err=False
  new_artist=Artist(name=form.name.data,city=form.city.data,state=form.state.data,phone=form.phone.data,image_link=form.image_link.data,
  genres=form.genres.data,facebook_link=form.facebook_link.data,website_link=form.website_link.data,seeking_venue=form.seeking_venue.data,
  seeking_description=form.seeking_description.data)
  try:
    # on successful db insert, flash success
    if form.validate_on_submit():
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
    else:
      flash('An error occurred. Artist could not be listed.') #on unsuccessful db insert, flash an error instead.
  except:
    err=True
    db.session.rollback()
  finally:
    if err:
      flash('An error occurred. Artist could not be listed.')
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  shows=Show.query.all()
  for s in shows:
    d={
      "venue_id":s.venue_id,
      "venue_name":Venue.query.filter(Venue.id==s.venue_id).all()[0].name,
      "artist_id":s.artist_id,
      "artist_name":Artist.query.filter(Artist.id==s.artist_id).all()[0].name,
      "artist_image_link":Artist.query.filter(Artist.id==s.artist_id).all()[0].image_link,
      "start_time":str(s.start_time)
    }
    data.append(d)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  new_show=Show(artist_id=form.artist_id.data,venue_id=form.venue_id.data,start_time=form.start_time.data)
  err=False
  try:
    if form.validate_on_submit():
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')  # on successful db insert, flash success
    else:
      flash('An error occurred. Show could not be listed.')  #on unsuccessful db insert, flash an error instead.
  except:
    err=True
    db.session.rollback()
  finally:
    if err:
      flash('An error occurred. Show could not be listed.')
    db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
