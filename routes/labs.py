"""
Certification Labs routes

Provides simple pages for certification labs (GIA, AGS, IGI, EGL) so the menu can link
to internal pages. Pages are lightweight and can be expanded later.
"""

from flask import Blueprint, render_template

bp = Blueprint('labs', __name__, url_prefix='/labs')


@bp.route('/')
def index():
    page_data = {
        'title': 'Certification Labs',
        'description': 'Information and links to major gemstone certification laboratories.'
    }
    return render_template('labs/index.html', **page_data)


@bp.route('/gia')
def gia():
    return render_template('labs/lab.html', title='GIA', org='Gemological Institute of America', url='https://www.gia.edu')


@bp.route('/ags')
def ags():
    return render_template('labs/lab.html', title='AGS', org='American Gem Society', url='https://www.americangemsociety.org')


@bp.route('/igi')
def igi():
    return render_template('labs/lab.html', title='IGI', org='International Gemological Institute', url='https://www.igi.org')


@bp.route('/egl')
def egl():
    return render_template('labs/lab.html', title='EGL', org='European Gemological Laboratory', url='https://www.eglusa.com')
