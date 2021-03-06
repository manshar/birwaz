# coding: utf-8

import flask
import flask_wtf
import wtforms

import auth
import config
import task
import util

from main import app


class FeedbackForm(flask_wtf.FlaskForm):
  message = wtforms.TextAreaField(
    u'الرسالة',
    [wtforms.validators.required()], filters=[util.strip_filter],
  )
  email = wtforms.StringField(
    u'بريدك الإلكتروني',
    [wtforms.validators.optional(), wtforms.validators.email()],
    filters=[util.email_filter],
  )
  recaptcha = flask_wtf.RecaptchaField()


@app.route('/feedback/', methods=['GET', 'POST'])
def feedback():
  if not config.CONFIG_DB.feedback_email:
    return flask.abort(418)

  form = FeedbackForm(obj=auth.current_user_db())
  if not config.CONFIG_DB.has_anonymous_recaptcha or auth.is_logged_in():
    del form.recaptcha
  if form.validate_on_submit():
    body = '%s\n\n%s' % (form.message.data, form.email.data)
    kwargs = {'reply_to': form.email.data} if form.email.data else {}
    task.send_mail_notification('%s...' % body[:48].strip(), body, **kwargs)
    flask.flash(u'شكراً لإرسالك الرسالة!', category='success')
    return flask.redirect(flask.url_for('welcome'))

  return flask.render_template(
    'feedback.html',
    title=u'تواصل معنا',
    html_class='feedback',
    form=form,
  )
