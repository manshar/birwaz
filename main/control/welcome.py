# coding: utf-8

import flask

import config

from main import app

import model
import util


###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
  resource_dbs, next_cursor = model.Resource.get_dbs(
    model.Resource.query(model.Resource.hotness > 0),
    limit=20, prev_cursor=True, order='-hotness')

  return flask.render_template(
    'welcome.html',
    html_class='welcome',
    resource_dbs=resource_dbs,
    next_url=util.generate_next_url(next_cursor, base_url=flask.url_for('resource_grid')),
    api_url=flask.url_for('api.resource.list'),
  )


###############################################################################
# Sitemap stuff
###############################################################################
@app.route('/sitemap.xml')
def sitemap():
  response = flask.make_response(flask.render_template(
    'sitemap.xml',
    lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
  ))
  response.headers['Content-Type'] = 'application/xml'
  return response




###############################################################################
# About page
###############################################################################
@app.route('/about')
def about():
  return flask.render_template('about.html',
    html_class='about',
)


###############################################################################
# TOS page
###############################################################################
@app.route('/tos')
def tos():
  return flask.render_template('tos.html',
    html_class='tos',
)


###############################################################################
# Privacy page
###############################################################################
@app.route('/privacy')
def privacy():
  return flask.render_template('privacy.html',
    html_class='privacy',
)


###############################################################################
# License page
###############################################################################
@app.route('/license')
def license():
  return flask.render_template('license.html',
    html_class='license',
)


###############################################################################
# FAQ page
###############################################################################
@app.route('/faq')
def faq():
  return flask.render_template('faq.html',
    html_class='faq',
)



###############################################################################
# Submissions Guidelines page
###############################################################################
@app.route('/submission-guidelines')
def submissionGuidelines():
  return flask.render_template('submission-guidelines.html',
    html_class='submission-guidelines',
)

###############################################################################
# Warmup request
###############################################################################
@app.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'
