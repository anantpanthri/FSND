# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from datetime import datetime
from logging import Formatter, FileHandler
from babel import dates
from dateutil import parser
from flask import Flask, render_template, request, redirect, url_for, flash, logging, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, func, Column, Integer, ForeignKey
from forms import *

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Shows(db.Model):
    __tablename__ = 'shows'
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('Artist.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('Venue.id'), nullable=False)
    start_time = Column('start_time', db.DateTime())


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
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    genres = db.Column(db.ARRAY(db.String()))
    seeking_description = db.Column(db.String(500))
    venues = db.relationship('Artist', secondary="shows", backref=db.backref('shows', lazy='joined'))

    def __repr__(self):
        return 'Venue Id:{} | Name: {}'.format(self.id, self.name)


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
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    genres = db.Column(db.ARRAY(db.String()))
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
        return 'Artist Id:{} | Name: {}'.format(self.id, self.name)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
def get_dictionary_from_result(result):
    # converts data into a dictionary
    list_dict = []
    for i in result:
        i_dict = i._asdict()
        list_dict.append(i_dict)
    return list_dict


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


@app.route('/venues')
def venues():
    groupby_venues = (db.session.query(
        Venue.city,
        Venue.state
    ).group_by(Venue.city, Venue.state))
    data = get_dictionary_from_result(groupby_venues)
    for area in data:
        area['venues'] = [object_as_dict(venue) for venue in Venue.query.filter_by(city=area['city']).all()]
        for ven in area['venues']:
            ven['num_shows'] = db.session.query(func.count(Shows.venue_id)).filter(Shows.venue_id == ven['id']).filter(
                Shows.start_time > datetime.now()).all()[0][0]

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_venue = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    count = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).count()
    response = {
        "count": count,
        "data": search_venue
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    single_venue = Venue.query.get(venue_id)
    single_venue.past_shows = (db.session.query(
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Shows)
                               .filter(Shows.venue_id == venue_id)
                               .filter(Shows.artist_id == Artist.id)
                               .filter(Shows.start_time <= datetime.now())
                               .all())

    single_venue.upcoming_shows = (db.session.query(
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Shows)
                                   .filter(Shows.venue_id == venue_id)
                                   .filter(Shows.artist_id == Artist.id)
                                   .filter(Shows.start_time > datetime.now())
                                   .all())

    single_venue.past_shows_count = (db.session.query(
        func.count(Shows.venue_id))
                                     .filter(Shows.venue_id == venue_id)
                                     .filter(Shows.start_time < datetime.now())
                                     .all())[0][0]

    single_venue.upcoming_shows_count = (db.session.query(
        func.count(Shows.venue_id))
                                         .filter(Shows.venue_id == venue_id)
                                         .filter(Shows.start_time > datetime.now())
                                         .all())[0][0]

    return render_template('pages/show_venue.html', venue=single_venue)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_form = VenueForm(request.form)
    flashType = 'not success'
    try:
        newVenue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            facebook_link=request.form['facebook_link']
        )
        db.session.add(newVenue)
        db.session.commit()
        flashType = 'success'
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash(venue_form.error)
        error = "Failed!!!"
        flash('Sorry Venue ' + request.form['name'] + ' was not successfully listed!')
    finally:
        db.session.close()
    return render_template('pages/home.html', flashType=flashType)


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'), code=303)


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = [object_as_dict(artist) for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_artist = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    count = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).count()
    response = {
        "count": count,
        "data": search_artist
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    single_artist = Artist.query.get(artist_id)
    single_artist.past_shows = (db.session.query(
        Venue.id.label("venue_id"),
        Venue.name.label("venue_name"),
        Venue.image_link.label("venue_image_link"),
        Shows)
                                .filter(Shows.artist_id == artist_id)
                                .filter(Shows.venue_id == Venue.id)
                                .filter(Shows.start_time <= datetime.now())
                                .all())

    single_artist.upcoming_shows = (db.session.query(
        Venue.id.label("venue_id"),
        Venue.name.label("venue_name"),
        Venue.image_link.label("venue_image_link"),
        Shows)
                                    .filter(Shows.artist_id == artist_id)
                                    .filter(Shows.venue_id == Venue.id)
                                    .filter(Shows.start_time > datetime.now())
                                    .all())

    single_artist.past_shows_count = (db.session.query(
        func.count(Shows.artist_id))
                                      .filter(Shows.artist_id == artist_id)
                                      .filter(Shows.start_time < datetime.now())
                                      .all())[0][0]

    single_artist.upcoming_shows_count = (db.session.query(
        func.count(Shows.artist_id))
                                          .filter(Shows.artist_id == artist_id)
                                          .filter(Shows.start_time > datetime.now())
                                          .all())[0][0]

    genres = single_artist.genres
    single_artist.genres = []
    for genre in genres:
        x = (''.join(genres))
    single_artist.genres += x.strip('}{').split(',')
    return render_template('pages/show_artist.html', artist=single_artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    ''' artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }'''
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    flashType = 'success'
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name'],
        artist.city = request.form['city'],
        artist.state = request.form['state'],
        artist.phone = request.form['phone'],
        artist.genres = request.form['genres'],
        artist.facebook_link = request.form['facebook_link']
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated')
    except Exception as  e:
        flashType = 'failed'
        flash('Artist ' + request.form['name'] + ' Failed')
        print('Error while update', e)
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id, flashType=flashType))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    flashType = 'not success'
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name'],
        venue.city = request.form['city'],
        venue.state = request.form['state'],
        venue.address = request.form['address'],
        venue.phone = request.form['phone'],
        venue.genres = request.form.getlist('genres'),
        genres = venue.genres
        venue.genres = []
        for genre in genres:
            venue.genres += genre
        venue.facebook_link = request.form['facebook_link']
        db.session.add(venue)
        db.session.commit()
        flashType = "success"
        flash('Venue ' + request.form['name'] + ' was successfully updated')
    except Exception as e:
        print('Failed', e)
        flash('Venue ' + request.form['name'] + ' Failed!')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id, flashType=flashType))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    flashType = 'failed'
    try:
        newArtist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            facebook_link=request.form['facebook_link'],
            genres=request.form.getlist('genres')
        )
        db.session.add(newArtist)
        db.session.commit()
        flashType = 'success'
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html', flashType=flashType)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = (db.session.query(
        Venue.id.label("venue_id"),
        Venue.name.label("venue_name"),
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Shows)
            .filter(Shows.venue_id == Venue.id)
            .filter(Shows.artist_id == Artist.id)
            .all())

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    flashType = 'failed'
    try:
        newShow = Shows(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time']
        )
        db.session.add(newShow)
        db.session.commit()
        flashType = 'success'
        flash('Show was successfully listed!')
    except Exception as  e:
        print(e)
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html', flashType=flashType)


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
