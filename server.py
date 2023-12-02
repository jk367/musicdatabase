
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://jhk2199:password1234@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT L.name, L.year_founded, COUNT(*) AS total FROM Labels L, Releases R WHERE R.l_name = L.name AND R.year_FOUNDED = L.year_founded GROUP BY L.name, L.year_founded ORDER BY total DESC LIMIT 5")
  by_album = []
  for result in cursor:
    by_album.append(result) 
  cursor.close()

  cursor = g.conn.execute("SELECT L.name, L.year_founded, COUNT(*) AS total FROM Labels L, Signed_By S, Wrote W WHERE S.l_name = L.name AND S.year_founded = L.year_founded AND S.a_name = W.name AND S.dob = W.dob GROUP BY L.name, L.year_founded ORDER BY total DESC LIMIT 5")
  by_song = []
  for result in cursor:
    by_song.append(result) 
  cursor.close()

  context = dict(album=by_album, song=by_song)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/search')
def search():
  args = request.args
  raw_query = args.get("q")
  query = '%{}%'.format(raw_query.lower())
  domain = args.get("in")

  if domain == "Releases":
    cursor = g.conn.execute("SELECT * FROM Releases WHERE LOWER(title) LIKE %s", query)
  elif domain == "Songs":
    cursor = g.conn.execute("SELECT * FROM Songs WHERE LOWER(title) LIKE %s", query)
  elif domain == "Artists":
    cursor = g.conn.execute("SELECT * FROM Artists WHERE LOWER(name) LIKE %s", query)
  elif domain == "Labels":
    cursor = g.conn.execute("SELECT * FROM Labels WHERE LOWER(name) LIKE %s", query)
  elif domain == "Genres":
    cursor = g.conn.execute("SELECT * FROM Genres WHERE LOWER(name) LIKE %s", query)
  elif domain == "Instruments":
    cursor = g.conn.execute("SELECT * FROM Instruments WHERE LOWER(name) LIKE %s", query)
  else:
    cursor = None

  names = []
  for result in cursor:
    names.append(result)
  cursor.close()
  context = dict(data = names, domain=domain, query=raw_query)

  return render_template("search.html", **context)


@app.route('/release')
def release():
  args = request.args
  upc = args.get("upc")

  # get release info
  cursor = g.conn.execute("SELECT * FROM Releases WHERE upc = %s", upc)
  names = []
  for result in cursor:
    names.append(result)
    break
  cursor.close()

  # get tracklist
  cursor = g.conn.execute("SELECT B.isrc, B.track_number, S.title, S.length, S.year_recorded, S.spotify_id FROM Belongs_To B, Songs S WHERE B.upc = %s AND S.isrc = B.isrc", upc)
  songs = []
  for result in cursor:
    songs.append(result)
  cursor.close()

  # get artist list
  cursor = g.conn.execute("SELECT A.name, A.dob FROM Artists A, Recorded_On R WHERE R.upc = %s AND R.name = A.name AND R.DOB = A.DOB", upc)
  artists = []
  for result in cursor:
    artists.append(result)
  cursor.close()

  # get genre list
  cursor = g.conn.execute("SELECT G.name FROM Includes I, Genres G WHERE I.upc = %s AND I.name = G.name", upc)
  genres = []
  for result in cursor:
    genres.append(result)
  cursor.close()


  context = dict(release=names, songs=songs, artists=artists, genres=genres)

  return render_template("releases.html", **context)

@app.route('/song')
def song():
  args = request.args
  isrc = args.get("isrc")

  # get song info
  cursor = g.conn.execute("SELECT * FROM Songs WHERE isrc = %s", isrc)
  names = []
  for result in cursor:
    names.append(result)
    break
  cursor.close()

  # get album list
  cursor = g.conn.execute("SELECT B.upc, B.track_number, R.title, R.year_released FROM Belongs_To B, Releases R WHERE B.isrc = %s AND R.upc = B.upc", isrc)
  albums = []
  for result in cursor:
    albums.append(result)
  cursor.close()

  # get artist list
  cursor = g.conn.execute("SELECT A.name, A.dob FROM Artists A, Wrote W WHERE W.isrc = %s AND W.name = A.name AND W.DOB = A.DOB", isrc)
  artists = []
  for result in cursor:
    artists.append(result)
  cursor.close()


  context = dict(song=names, albums=albums, artists=artists)

  return render_template("songs.html", **context)

@app.route('/artist')
def artist():
  args = request.args
  name = args.get("name")
  dob = args.get("dob")

  # get artist info
  cursor = g.conn.execute("SELECT * FROM Artists WHERE name = %s AND DOB = %s", name, dob)
  names = []
  for result in cursor:
    names.append(result)
    break
  cursor.close()

  # get album list
  cursor = g.conn.execute("SELECT X.upc, R.title, R.year_released FROM Recorded_On X, Releases R WHERE X.name = %s AND X.DOB = %s AND X.upc = R.upc", name, dob)
  albums = []
  for result in cursor:
    albums.append(result)
  cursor.close()

  # get song list
  cursor = g.conn.execute("SELECT W.isrc, S.title, S.year_recorded FROM Wrote W, Songs S WHERE W.isrc = S.isrc AND W.name = %s AND W.DOB = %s", name, dob)
  songs = []
  for result in cursor:
    songs.append(result)
  cursor.close()

  # get label list
  cursor = g.conn.execute("SELECT S.l_name, S.year_founded FROM Signed_By S, Labels L WHERE S.a_name = %s AND S.DOB = %s AND S.l_name = L.name AND S.year_founded = L.year_founded", name, dob)
  labels = []
  for result in cursor:
    labels.append(result)
  cursor.close()

  # get instrument list
  cursor = g.conn.execute("SELECT P.i_name FROM Plays P, Instruments I WHERE P.a_name = %s AND P.DOB = %s AND P.i_name = I.name", name, dob)
  instruments = []
  for result in cursor:
    instruments.append(result)
  cursor.close()


  context = dict(artist=names, albums=albums, songs=songs, labels=labels, instruments=instruments)

  return render_template("artists.html", **context)

@app.route('/label')
def label():
  args = request.args
  name = args.get("name")
  year_founded = args.get("year_founded")

  # get release info
  cursor = g.conn.execute("SELECT * FROM Labels WHERE name = %s AND year_founded = %s", name, year_founded)
  names = []
  for result in cursor:
    names.append(result)
    break
  cursor.close()

  # get album list
  cursor = g.conn.execute("SELECT R.title, R.year_released, R.upc, R.label_number FROM Releases R WHERE R.l_name = %s AND R.year_founded = %s", name, year_founded)
  albums = []
  for result in cursor:
    albums.append(result)
  cursor.close()

  # get artist list
  cursor = g.conn.execute("SELECT S.a_name, S.dob, S.from_date, S.to_date FROM Signed_By S, Artists A WHERE S.l_name = %s AND S.year_founded = %s AND S.a_name = A.name AND S.DOB = A.DOB", name, year_founded)
  artists = []
  for result in cursor:
    artists.append(result)
  cursor.close()

  context = dict(label=names, albums=albums, artists=artists)

  return render_template("labels.html", **context)

@app.route('/genre')
def genre():
  args = request.args
  name = args.get("name")

  # get genre info
  cursor = g.conn.execute("SELECT * FROM Genres WHERE name = %s", name)
  names = []
  for result in cursor:
    names.append(result)
    break
  cursor.close()

  # get instrument list
  cursor = g.conn.execute("SELECT A.i_name FROM Associated_With A, Instruments I WHERE A.i_name = I.name AND A.g_name = %s", name)
  instruments = []
  for result in cursor:
    instruments.append(result)
  cursor.close()

  # get album list
  cursor = g.conn.execute("SELECT I.upc, R.title, R.year_released FROM Includes I, Releases R WHERE I.upc = R.upc AND I.name = %s", name)
  albums = []
  for result in cursor:
    albums.append(result)
  cursor.close()

  context = dict(genre=names, instruments=instruments, albums=albums)

  return render_template("genres.html", **context)

@app.route('/instrument')
def instrument():
  args = request.args
  name = args.get("name")

  # get instrument info
  cursor = g.conn.execute("SELECT * FROM Instruments WHERE name = %s", name)
  names = []
  for result in cursor:
    names.append(result)
    break
  cursor.close()

  # get artist list
  cursor = g.conn.execute("SELECT P.a_name, P.dob FROM Plays P, Artists A WHERE P.a_name = A.name AND P.DOB = A.dob AND P.I_name = %s", name)
  artists = []
  for result in cursor:
    artists.append(result)
  cursor.close()

  # get genre list
  cursor = g.conn.execute("SELECT A.g_name FROM Associated_With A, Genres G WHERE A.i_name = %s AND A.g_name = G.name", name)
  genres = []
  for result in cursor:
    genres.append(result)
  cursor.close()

  context = dict(instrument=names, artists=artists, genres=genres)

  return render_template("instruments.html", **context)



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
