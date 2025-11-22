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


@bp.route('/aig')
def aig():
    return render_template('labs/lab.html',
                           title='AIG',
                           org='Asian Institute of Gemological Sciences',
                           website='https://www.aigslab.com',
                           locations='https://www.aigslab.com/contact',
                           services='https://www.aigslab.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/agl')
def agl():
    return render_template('labs/lab.html',
                           title='AGL',
                           org='American Gemological Laboratories',
                           website='https://www.americangemlab.com',
                           locations='https://www.americangemlab.com/contact',
                           services='https://www.americangemlab.com/services',
                           pricing='https://www.americangemlab.com/fees',
                           schedule_fee='https://www.americangemlab.com/fees')


@bp.route('/gubelin')
def gubelin():
    return render_template('labs/lab.html',
                           title='Gübelin',
                           org='Gübelin Gem Lab',
                           website='https://www.gubelingemlab.com',
                           locations='https://www.gubelingemlab.com/contact',
                           services='https://www.gubelingemlab.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/lotus')
def lotus():
    return render_template('labs/lab.html',
                           title='Lotus',
                           org='Lotus Gemology',
                           website='https://www.lotusgemology.com',
                           locations='https://www.lotusgemology.com/contact',
                           services='https://www.lotusgemology.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/grs')
def grs():
    return render_template('labs/lab.html',
                           title='GRS',
                           org='Gem Research Swisslab',
                           website='https://www.gemresearch.ch',
                           locations='https://www.gemresearch.ch/contact',
                           services='https://www.gemresearch.ch/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/aigs')
def aigs():
    return render_template('labs/lab.html',
                           title='AIGS',
                           org='Asian Institute of Gemological Sciences',
                           website='https://www.aigsthailand.com',
                           locations='https://www.aigsthailand.com/contact',
                           services='https://www.aigsthailand.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/ica')
def ica():
    return render_template('labs/lab.html',
                           title='ICA',
                           org='International Colored Gemstone Association',
                           website='https://www.gemstone.org',
                           locations='https://www.gemstone.org/contact',
                           services='https://www.gemstone.org',
                           pricing='',
                           schedule_fee='')


@bp.route('/hrd')
def hrd():
    return render_template('labs/lab.html',
                           title='HRD',
                           org='HRD Antwerp',
                           website='https://www.hrdantwerp.com',
                           locations='https://www.hrdantwerp.com/contact',
                           services='https://www.hrdantwerp.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/aigl')
def aigl():
    return render_template('labs/lab.html',
                           title='AIGL',
                           org='Antwerp Institute of Gemology Laboratory',
                           website='https://www.aigl.org',
                           locations='https://www.aigl.org/contact',
                           services='https://www.aigl.org/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/hkd')
def hkd():
    return render_template('labs/lab.html',
                           title='HKD',
                           org='Hong Kong Diamond Laboratory',
                           website='https://www.hkdlab.com',
                           locations='https://www.hkdlab.com/contact',
                           services='https://www.hkdlab.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/ssef')
def ssef():
    return render_template('labs/lab.html',
                           title='SSEF',
                           org='Swiss Gemmological Institute',
                           website='https://www.ssef.ch',
                           locations='https://www.ssef.ch/contact',
                           services='https://www.ssef.ch/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/gaa')
def gaa():
    return render_template('labs/lab.html',
                           title='GAA',
                           org='Gem and Art Advisory',
                           website='https://www.gemandartadvisory.com',
                           locations='https://www.gemandartadvisory.com/contact',
                           services='https://www.gemandartadvisory.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/gfco')
def gfco():
    return render_template('labs/lab.html',
                           title='GFCO',
                           org='GFCO Swiss Gem Lab',
                           website='https://www.gfcogemlab.ch',
                           locations='https://www.gfcogemlab.ch/contact',
                           services='https://www.gfcogemlab.ch/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/gojiot')
def gojiot():
    return render_template('labs/lab.html',
                           title='GOJIOT',
                           org='GOJIOT Gem Laboratory',
                           website='https://www.gojiot.com',
                           locations='https://www.gojiot.com/contact',
                           services='https://www.gojiot.com/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/algt')
def algt():
    return render_template('labs/lab.html',
                           title='ALGT',
                           org='Antwerp Laboratory for Gemstone Testing',
                           website='https://www.algt.be',
                           locations='https://www.algt.be/contact',
                           services='https://www.algt.be/services',
                           pricing='',
                           schedule_fee='')


@bp.route('/dga')
def dga():
    return render_template('labs/lab.html',
                           title='DGA',
                           org='Dunaigre Gemological Analysis',
                           website='https://www.dga-lab.com',
                           locations='https://www.dga-lab.com/contact',
                           services='https://www.dga-lab.com/services',
                           pricing='',
                           schedule_fee='')
