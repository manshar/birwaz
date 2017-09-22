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
    limit=10, prev_cursor=True, order='-created')

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
# Warmup request
###############################################################################
@app.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'
