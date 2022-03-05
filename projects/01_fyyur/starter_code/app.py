#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from Models import *

#----------------------------------------------------------------------------#
# correcting a BUG that occurs on dateutil parser collection
#----------------------------------------------------------------------------#
import collections
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# End correcting a BUG
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  print("+++++++++++++")
  print("value "+value)
  date = dateutil.parser.parse(value)
  print("Date "+str(date))
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
# Looking at the data provided with the question it appears that we need to
# pull all venues and then pull all shows and then rearrange the venue based on city,
# and do a count on the number of upcoming shows.
#
#
@app.route('/venues')
def venues():
    data =[]
    current_date = datetime.now()
    venues = Venue.query.all()
    unique_venues = set()
    for venue in venues:
        unique_venues.add((venue.city, venue.state))
    for everylocation in unique_venues:
        data.append({"city": everylocation[0],"state": everylocation[1],"venues": []})
    for venue in venues:
        num_upcoming_shows = 0
        shows = Show.query.filter_by(venue_id=venue.id).all()
        for show in shows:
            if show.start_time > current_date:
                num_upcoming_shows += 1
        for dataitem in data:
            if venue.state == dataitem['state'] and venue.city == dataitem['city']:
                dataitem['venues'].append({"id": venue.id,"name": venue.name,"num_upcoming_shows": num_upcoming_shows})
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_termlocal = '%{0}%'.format(search_term)
    result = Venue.query.filter(Venue.name.ilike(search_termlocal))
    response={ "count": result.count(),"data": result }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    nextshowlist=[]
    prevshowlist=[]
    venue = Venue.query.get(venue_id)
    #listofshows=Show.query.filter_by(venue_id=venue_id).all()
    listofshows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
    current_date = datetime.now()
    for show_listitem in listofshows:
        showDictionaryItem ={
            "artist_id": show_listitem.artist.id,
            "artist_name": show_listitem.artist.name,
            "artist_image_link": show_listitem.artist.image_link,
            "start_time": format_datetime(str(show_listitem.start_time))
        }
        prevshowlist.append(showDictionaryItem)

    listofshows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()

    for show_listitem in listofshows:
        showDictionaryItem ={
            "artist_id": show_listitem.artist.id,
            "artist_name": show_listitem.artist.name,
            "artist_image_link": show_listitem.artist.image_link,
            "start_time": format_datetime(str(show_listitem.start_time))
        }
        nextshowlist.append(showDictionaryItem)

    venuedictionary={
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description":venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": prevshowlist,
        "upcoming_shows": nextshowlist,
        "past_shows_count": len(prevshowlist),
        "upcoming_shows_count": len(nextshowlist)
    }
    return render_template('pages/show_venue.html', venue=venuedictionary)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        form = VenueForm()
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data,
                    address=form.address.data,phone=form.phone.data, image_link=form.image_link.data,
                    genres=form.genres.data, facebook_link=form.facebook_link.data, seeking_description=form.seeking_description.data,
                    website_link=form.website_link.data, seeking_talent=form.seeking_talent.data)
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error=True
    finally:
        db.session.close()
        if not error:
              # on successful db insert, flash success
              flash('Venue ' + request.form['name'] + ' was successfully listed!')
              return render_template('pages/home.html')
        else:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            abort (400)



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue_name + ' deleted successfully')
  except:
    flash('an error occured while deleting Venue ' + venue_name)
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data=[]
  for artist in artists:
      data.append({
      "id": artist.id,
      "name": artist.name
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_termlocal = '%{0}%'.format(search_term)
    artists = Artist.query.filter(Artist.name.ilike(search_termlocal)).all()
    current_date = datetime.now()
    artistdata =[]
    for artist in artists:
        listofshows=Show.query.filter_by(artist_id=artist.id).all()
        num_upcoming_shows = 0
        for show in listofshows:
            if show.start_time > current_date:
                num_upcoming_shows+=1
        artistdata.append({"id":artist.id, "name":artist.name, "num_upcoming_shows":num_upcoming_shows})
    countofartists=0
    if len(artists):
        countofartists = len(artists)
    response={"count":countofartists, "data":artistdata}
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    #listofshows=Show.query.filter_by(artist_id=artist_id).all()
    nextshowlist=[]
    prevshowlist=[]
    current_date = datetime.now()
    listofshows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
    print (listofshows)

    for show_listitem in listofshows:
        showDictionaryItem ={
            "venue_id": show_listitem.venue.id,
            "venue_name": show_listitem.venue.name,
            "venue_image_link": show_listitem.venue.image_link,
            "start_time": format_datetime(str(show_listitem.start_time))
        }
        prevshowlist.append(showDictionaryItem)

    listofshows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
    for show_listitem in listofshows:
        showDictionaryItem ={
            "venue_id": show_listitem.venue.id,
            "venue_name": show_listitem.venue.name,
            "venue_image_link": show_listitem.venue.image_link,
            "start_time": format_datetime(str(show_listitem.start_time))
        }
        nextshowlist.append(showDictionaryItem)
    artistdictionary={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "website_link": artist.website_link,
        "image_link": artist.image_link,
        "past_shows": prevshowlist,
        "upcoming_shows": nextshowlist,
        "past_shows_count": len(prevshowlist),
        "upcoming_shows_count": len(nextshowlist)
    }
    return render_template('pages/show_artist.html', artist=artistdictionary)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "website_link":artist.website_link,
        "seeking_venue":artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
      form = ArtistForm()
      artist = Artist.query.get(artist_id)
      artist.name = form.name.data
      artist.phone = form.phone.data
      artist.state = form.state.data
      artist.city = form.city.data
      artist.genres = form.genres.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' is updated')
  except:
      db.session.rolback()
      flash('update failed for artist ' + request.form['name'] )
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  name=""
  try:
      form = VenueForm()
      venue = Venue.query.get(venue_id)
      name = form.name.data
      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      venue.image_link = form.image_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Venue ' + name + ' is updated')
  except:
      db.session.rollback()
      flash('update failed for venue ' + name )
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
  try:
      form = ArtistForm()
      artist = Artist(
                    name=form.name.data,
                    city=form.city.data,
                    state=form.city.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    image_link=form.image_link.data,
                    seeking_venue = form.seeking_venue.data,
                    seeking_description=form.seeking_description.data,
                    website_link= form.website_link.data,
                    facebook_link=form.facebook_link.data
                    )
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    listofshows = []
    shows = Show.query.order_by(db.desc(Show.start_time))
    for show in shows:
      listofshows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
    })
    return render_template('pages/shows.html', shows=listofshows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'],start_time=request.form['start_time'])
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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
