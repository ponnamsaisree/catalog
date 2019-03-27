from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_file import Base, Apssdc, Team_Details, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///apssdc_db.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "APSSDC"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
gts_ca = session.query(Apssdc).all()


# login for the user
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    gts_ca = session.query(Apssdc).all()
    sbit = session.query(Team_Details).all()
    return render_template('login.html',
                           STATE=state, gts_ca=gts_ca, sbit=sbit)
    # return render_template('myhome.html', STATE=state
    # gts_ca=gts_ca,sbit=sbit)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

# Here it shows the home


@app.route('/')
@app.route('/home')
def home():
    gts_ca = session.query(Apssdc).all()
    return render_template('myhome.html', gts_ca=gts_ca)

# ApssdcSite for admins


@app.route('/ApssdcSite')
def ApssdcSite():
    try:
        if login_session['username']:
            name = login_session['username']
            gts_ca = session.query(Apssdc).all()
            bit = session.query(Apssdc).all()
            sbit = session.query(Team_Details).all()
            return render_template('myhome.html', gts_ca=gts_ca,
                                   bit=bit, sbit=sbit, uname=name)
    except:
        return redirect(url_for('showLogin'))


# It shows the details
@app.route('/ApssdcSite/<int:sbid>/AllTeams')
def showApssdc(sbid):
    gts_ca = session.query(Apssdc).all()
    bit = session.query(Apssdc).filter_by(id=sbid).one()
    sbit = session.query(Team_Details).filter_by(apssdc_name_id=sbid).all()
    try:
        if login_session['username']:
            return render_template('showApssdc.html', gts_ca=gts_ca,
                                   bit=bit, sbit=sbit,
                                   uname=login_session['username'])
    except:
        return render_template('showApssdc.html',
                               gts_ca=gts_ca, bit=bit, sbit=sbit)


# Here we can add a new Apssdc


@app.route('/ApssdcSite/addApssdc_Name', methods=['POST', 'GET'])
def addApssdc_Name():
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        apssdc_name = Apssdc(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(apssdc_name)
        session.commit()
        return redirect(url_for('ApssdcSite'))
    else:
        return render_template('addApssdc_Name.html', gts_ca=gts_ca)

# Here we can edit a particular Apssdc name


@app.route('/ApssdcSite/<int:sbid>/edit', methods=['POST', 'GET'])
def editApssdc_Name(sbid):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    editApssdc_Name = session.query(Apssdc).filter_by(id=sbid).one()
    creator = getUserInfo(editApssdc_Name.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this apssdcname."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('ApssdcSite'))
    if request.method == "POST":
        if request.form['name']:
            editApssdc_Name.name = request.form['name']
        session.add(editApssdc_Name)
        session.commit()
        flash("Apssdc Edited Successfully")
        return redirect(url_for('ApssdcSite'))
    else:
        # gts_ca is global variable we can them in entire application
        return render_template('editApssdc_Name.html',
                               sb=editApssdc_Name, gts_ca=gts_ca)

# delete particular apssdc name


@app.route('/ApssdcSite/<int:sbid>/delete', methods=['POST', 'GET'])
def deleteApssdc_Name(sbid):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    sb = session.query(Apssdc).filter_by(id=sbid).one()
    creator = getUserInfo(sb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this apssdc name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('ApssdcSite'))
    if request.method == "POST":
        session.delete(sb)
        session.commit()
        flash("Apssdc Deleted Successfully")
        return redirect(url_for('ApssdcSite'))
    else:
        return render_template('deleteApssdc_Name.html', sb=sb, gts_ca=gts_ca)

# add a team details to a particular apssdc


@app.route('/ApssdcSite/addApssdc_Name/addApssdc_Details/<string:sbname>/add',
           methods=['GET', 'POST'])
def addApssdc_Details(sbname):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    bit = session.query(Apssdc).filter_by(name=sbname).one()
    # See if the logged in user is not the owner
    creator = getUserInfo(bit.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new customer"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showApssdc', sbid=bit.id))
    if request.method == 'POST':
        team_name = request.form['team_name']
        description = request.form['description']
        team_count = request.form['team_count']
        teamdetails = Team_Details(team_name=team_name,
                                   description=description,
                                   team_count=team_count,
                                   apssdc_name_id=bit.id,
                                   user_id=login_session['user_id'])
        session.add(teamdetails)
        session.commit()
        return redirect(url_for('showApssdc', sbid=bit.id))
    else:
        return render_template('addApssdc_Details.html',
                               sbname=bit.name, gts_ca=gts_ca)

# edit a team details of a apssdc


@app.route('/ApssdcSite/<int:sbid>/<string:sbename>/edit',
           methods=['GET', 'POST'])
def editTeam_Details(sbid, sbename):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    sb = session.query(Apssdc).filter_by(id=sbid).one()
    teamdetails = session.query(Team_Details)\
        .filter_by(team_name=sbename).one()
    #  See if the logged in user is not the owner
    creator = getUserInfo(sb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user !=  owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this details"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showApssdc', sbid=sb.id))
    # POST methods
    if request.method == 'POST':
        teamdetails.team_name = request.form['team_name']
        teamdetails.description = request.form['description']
        teamdetails.team_count = request.form['team_count']
        session.add(teamdetails)
        session.commit()
        flash("Details Edited Successfully")
        return redirect(url_for('showApssdc', sbid=sbid))
    else:
        return render_template('editTeam_Details.html',
                               sbid=sbid, teamdetails=teamdetails,
                               gts_ca=gts_ca)

# Here we can delete a team details


@app.route('/ApssdcSite/<int:sbid>/<string:sbename>/delete',
           methods=['GET', 'POST'])
def deleteTeam_Details(sbid, sbename):
    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('showLogin'))
    sb = session.query(Apssdc).filter_by(id=sbid).one()
    teamdetails = session.query(Team_Details
                                ).filter_by(team_name=sbename).one()
    # See if the logged in user is not the owner
    creator = getUserInfo(sb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this details"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showApssdc', sbid=sb.id))
    if request.method == "POST":
        session.delete(teamdetails)
        session.commit()
        flash("Deleted details Successfully")
        return redirect(url_for('showApssdc', sbid=sbid))
    else:
        return render_template('deleteTeam_Details.html',
                               sbid=sbid, teamdetails=teamdetails,
                               gts_ca=gts_ca)

# USER LOGOUT


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'
                           })[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected user..'
                                            ), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json
# It displays the all details that you have


@app.route('/ApssdcSite/JSON')
def allApssdcJSON():
    apssdc_names = session.query(Apssdc).all()
    category_dict = [c.serialize for c in apssdc_names]
    for c in range(len(category_dict)):
        teamnames = [i.serialize for i in session.query(
                     Team_Details
                     ).filter_by(apssdc_name_id=category_dict[c]["id"]).all()]
        if teamnames:
            category_dict[c]["apssdc"] = teamnames
    return jsonify(Apssdc=category_dict)

# Displays the apssdc name and its id


@app.route('/ApssdcSite/apssdc_Name/JSON')
def categoriesJSON():
    apssdc = session.query(Apssdc).all()
    return jsonify(apssdc_Name=[c.serialize for c in apssdc])

# It displays all team details in apssdc


@app.route('/ApssdcSite/apssdc/JSON')
def detailsJSON():
    details = session.query(Team_Details).all()
    return jsonify(apssdc=[i.serialize for i in details])

# It displays the details in a apssdc


@app.route('/ApssdcSite/<path:apssdcname>/apssdc/JSON')
def categorydetailsJSON(apssdcname):
    apssdcName = session.query(Apssdc).filter_by(name=apssdcname).one()
    apssdc = session.query(Team_Details).filter_by(apssdc_name=apssdcName)\
        .all()
    return jsonify(apssdcName=[i.serialize for i in apssdc])

# It displays the details that you given


@app.route('/ApssdcSite/<path:apssdcname>/<path:teamdetails_name>/JSON')
def DetailsJSON(apssdcname, teamdetails_name):
    apssdcName = session.query(Apssdc).filter_by(name=apssdcname).one()
    teamDetailsName = session.query(Team_Details).filter_by(
           team_name=teamdetails_name, apssdc_name=apssdcName).one()
    return jsonify(teamDetailsName=[teamDetailsName.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
