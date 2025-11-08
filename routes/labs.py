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
    return render_template('labs/lab.html',
                           title='GIA',
                           org='Gemological Institute of America',
                           website='https://www.gia.edu',
                           locations='https://www.gia.edu/gia-labs',
                           services='https://www.gia.edu/gia-services',
                           pricing='https://www.gia.edu/doc/ColoredStones_FeeSchedule_MASTER_Q3_2025_USD.pdf',
                           schedule_fee='https://www.gia.edu/doc/ColoredStones_FeeSchedule_MASTER_Q3_2025_USD.pdf')


@bp.route('/ags')
def ags():
    return render_template('labs/lab.html',
                           title='AGS',
                           org='American Gem Society',
                           website='https://www.americangemlab.com',
                           locations='https://www.americangemlab.com/locations',
                           services='https://www.americangemlab.com/services',
                           pricing='https://www.americangemlab.com/fees',
                           schedule_fee='https://www.americangemlab.com/fees')


@bp.route('/igi')
def igi():
    return render_template('labs/lab.html',
                           title='IGI',
                           org='International Gemological Institute',
                           website='https://www.igi.org',
                           locations='https://www.igi.org/contact-us',
                           services='https://www.igi.org/services',
                           pricing='https://www.igi.org/services',
                           schedule_fee='')


@bp.route('/egl')
def egl():
    return render_template('labs/lab.html',
                           title='EGL',
                           org='European Gemological Laboratory',
                           website='https://www.eglusa.com',
                           locations='https://www.eglusa.com/locations',
                           services='https://www.eglusa.com/services',
                           pricing='https://www.eglusa.com/services',
                           schedule_fee='')
