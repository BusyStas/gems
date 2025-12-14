"""
Testing Methods routes

Provides pages for gem testing methodologies including refractive index,
specific gravity, spectroscopy, microscopy, UV fluorescence, and more.
"""

from flask import Blueprint, render_template, url_for, current_app
import requests
from utils.api_client import load_api_key

bp = Blueprint('testing', __name__, url_prefix='/testing')


@bp.route('/')
def index():
    """Testing Methods index page"""
    methods = [
        {
            'title': 'Refractive Index',
            'description': 'Measures how light bends through a gemstone',
            'url': url_for('testing.refractive_index'),
            'icon': 'prism'
        },
        {
            'title': 'Specific Gravity',
            'description': 'Determines density relative to water',
            'url': url_for('testing.specific_gravity'),
            'icon': 'scale'
        },
        {
            'title': 'Spectroscopy',
            'description': 'Analyzes light absorption patterns',
            'url': url_for('testing.spectroscopy'),
            'icon': 'spectrum'
        },
        {
            'title': 'Microscopy',
            'description': 'Examines internal features and inclusions',
            'url': url_for('testing.microscopy'),
            'icon': 'microscope'
        },
        {
            'title': 'UV Fluorescence',
            'description': 'Tests reaction to ultraviolet light',
            'url': url_for('testing.uv_fluorescence'),
            'icon': 'uv'
        },
        {
            'title': 'Inclusion Analysis',
            'description': 'Studies internal characteristics',
            'url': url_for('testing.inclusion_analysis'),
            'icon': 'inclusion'
        },
        {
            'title': 'Dichroscope Analysis',
            'description': 'Detects pleochroism in colored gems',
            'url': url_for('testing.dichroscope'),
            'icon': 'dichroscope'
        },
        {
            'title': 'Polariscope Analysis',
            'description': 'Determines optical character and strain',
            'url': url_for('testing.polariscope'),
            'icon': 'polariscope'
        },
        {
            'title': 'Chelsea Filter Test',
            'description': 'Color filter test for emeralds and other gems',
            'url': url_for('testing.chelsea_filter'),
            'icon': 'filter'
        },
    ]
    return render_template('testing/index.html',
                           title='Testing Methods',
                           description='Gemstone testing methodologies and techniques',
                           methods=methods)


@bp.route('/refractive-index')
def refractive_index():
    """Refractive Index testing method"""
    # Fetch gem test properties from API
    untestable_gems = []
    typical_values = {}

    try:
        base_url = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
        token = load_api_key() or ''
        headers = {'X-API-Key': token} if token else {}

        # Fetch all gem test properties
        response = requests.get(
            f"{base_url.rstrip('/')}/api/v2/gem-test-properties",
            params={'limit': 1000},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            test_props = response.json()

            # Also fetch gem names to match with test properties
            gems_response = requests.get(
                f"{base_url.rstrip('/')}/api/v2/gems",
                params={'limit': 1000},
                headers=headers,
                timeout=10
            )

            if gems_response.status_code == 200:
                gems = gems_response.json()
                gem_names = {g.get('GemTypeId'): g.get('GemTypeName') for g in gems}

                # Build typical values and categorize untestable gems
                for prop in test_props:
                    gem_id = prop.get('GemTypeId')
                    gem_name = gem_names.get(gem_id, f'Gem {gem_id}')
                    ri_min = prop.get('RefractiveIndexMin')
                    ri_max = prop.get('RefractiveIndexMax')

                    if ri_min and ri_max:
                        ri_range = f"{ri_min:.4f}-{ri_max:.4f}"
                        typical_values[gem_name] = ri_range

                        # Categorize untestable gems (RI > 1.81)
                        if ri_max > 1.81:
                            if ri_min > 2.4:
                                category = 'Exceptional Brilliance (RI > 2.4)'
                            elif ri_min > 1.9:
                                category = 'Outstanding Brilliance (RI 1.9-2.4)'
                            elif ri_min > 1.81:
                                category = 'Excellent Brilliance (RI > 1.81)'
                            else:
                                category = 'Partial Range Issues (upper range exceeds 1.81)'

                            # Find or create category
                            cat_obj = next((c for c in untestable_gems if c['title'] == category), None)
                            if not cat_obj:
                                cat_obj = {'title': category, 'gems': []}
                                untestable_gems.append(cat_obj)

                            cat_obj['gems'].append({'name': gem_name, 'ri': ri_range})
    except Exception as e:
        current_app.logger.warning(f"Failed to load gem test properties from API: {e}")
        # Fall back to empty data - template will still render
        typical_values = {}
        untestable_gems = []

    return render_template('testing/method.html',
                           title='Refractive Index',
                           method_name='Refractive Index Testing',
                           overview='''The refractive index (RI) is a fundamental optical property that measures
                           how much light bends when entering a gemstone. It is one of the most important
                           diagnostic tools in gemology.''',
                           how_it_works='''A refractometer measures the critical angle of total internal
                           reflection. Light enters the gem and bends at an angle determined by the gem's
                           optical density. The RI reading helps identify gem species.''',
                           equipment=['Gemological refractometer', 'Refractive index liquid (RI 1.81)',
                                      'Polarizing filter', 'Light source (sodium or white LED)'],
                           procedure=[
                               'Clean the gem and refractometer hemicylinder',
                               'Apply a small drop of RI liquid to the hemicylinder',
                               'Place the gem flat on the liquid with the largest facet down',
                               'Look through the eyepiece and read where the shadow edge meets the scale',
                               'Rotate the gem to check for double refraction (birefringence)'
                           ],
                           typical_values=typical_values,
                           limitations='''Cannot read gems with RI above 1.81 (the liquid limit).
                           Curved surfaces and small stones are difficult to measure accurately.''',
                           untestable_gems=untestable_gems)


@bp.route('/specific-gravity')
def specific_gravity():
    """Specific Gravity testing method"""
    return render_template('testing/method.html',
                           title='Specific Gravity',
                           method_name='Specific Gravity Testing',
                           overview='''Specific gravity (SG) measures a gemstone's density relative to water. 
                           It's a non-destructive test that helps identify gems and detect treatments.''',
                           how_it_works='''Using Archimedes' principle, the gem is weighed in air and then 
                           suspended in water. The difference in weight determines the volume displaced, 
                           allowing calculation of density.''',
                           equipment=['Precision balance (0.01g accuracy)', 'Beaker with distilled water',
                                      'Wire basket or gem holder', 'Thermometer'],
                           procedure=[
                               'Weigh the gem in air (W_air)',
                               'Suspend the gem in water using a wire basket',
                               'Record the weight in water (W_water)',
                               'Calculate SG = W_air / (W_air - W_water)',
                               'Adjust for water temperature if needed'
                           ],
                           typical_values={
                               'Diamond': '3.52',
                               'Ruby/Sapphire': '4.00',
                               'Emerald': '2.72',
                               'Quartz': '2.65',
                               'Topaz': '3.53'
                           },
                           limitations='''Small stones are difficult to measure accurately. Porous gems
                           may absorb water, affecting results. Included gems may have variable SG.''')


@bp.route('/spectroscopy')
def spectroscopy():
    """Spectroscopy testing method"""
    return render_template('testing/method.html',
                           title='Spectroscopy',
                           method_name='Spectroscopy Analysis',
                           overview='''Spectroscopy examines how gemstones absorb different wavelengths
                           of light. The absorption pattern creates a unique "fingerprint" for each gem
                           species and can reveal treatments.''',
                           how_it_works='''Light passes through the gem and is analyzed by a spectroscope.
                           Certain wavelengths are absorbed by trace elements, creating dark bands or
                           lines in the spectrum that are characteristic of specific gems.''',
                           equipment=['Hand-held spectroscope or desktop spectrometer',
                                      'Strong light source (fiber optic or LED)',
                                      'Dark room for observation', 'Wavelength calibration source'],
                           procedure=[
                               'Position the gem between the light source and spectroscope',
                               'Adjust focus until the spectrum is sharp',
                               'Note the position and intensity of absorption bands',
                               'Compare observed pattern with reference spectra',
                               'Document findings with wavelength measurements'
                           ],
                           typical_values={
                               'Ruby': '694nm fluorescence doublet, 659/668nm absorption',
                               'Blue Sapphire': '450nm (iron), 471nm bands',
                               'Emerald': '683nm (chrome lines), 680nm doublet',
                               'Alexandrite': 'Chrome spectrum similar to emerald',
                               'Almandine Garnet': 'Broad bands at 505nm, 520nm, 573nm'
                           },
                           limitations='''Pale gems may show weak absorption. Some synthetics have
                           identical spectra to natural gems. Requires practice to interpret correctly.''')


@bp.route('/microscopy')
def microscopy():
    """Microscopy testing method"""
    return render_template('testing/method.html',
                           title='Microscopy',
                           method_name='Microscopic Examination',
                           overview='''Microscopy is the most important tool for identifying gemstones,
                           detecting treatments, and determining natural vs. synthetic origin. Internal
                           features (inclusions) tell the gem's story.''',
                           how_it_works='''A gemological microscope uses darkfield illumination to
                           reveal internal features. Fiber optic lighting and immersion can enhance
                           visibility of inclusions and growth patterns.''',
                           equipment=['Gemological microscope (10x-70x)', 'Darkfield illumination base',
                                      'Fiber optic light source', 'Immersion cell and liquid',
                                      'Stone holder/tweezers'],
                           procedure=[
                               'Clean the gem thoroughly',
                               'Start at low magnification (10x) for overview',
                               'Use darkfield illumination to see inclusions clearly',
                               'Increase magnification to examine specific features',
                               'Rotate the gem to observe from multiple angles',
                               'Document findings with photographs'
                           ],
                           typical_values={
                               'Natural Ruby': 'Silk (rutile needles), fingerprints, crystals',
                               'Synthetic Ruby': 'Curved striae, gas bubbles',
                               'Natural Emerald': 'Three-phase inclusions, jardín',
                               'Treated Emerald': 'Filler in fractures, flash effect',
                               'Diamond': 'Crystals, feathers, clouds, naturals'
                           },
                           limitations='''Clean, high-quality gems may lack diagnostic inclusions.
                           Some treatments are designed to be undetectable. Experience is essential.''')


@bp.route('/uv-fluorescence')
def uv_fluorescence():
    """UV Fluorescence testing method"""
    return render_template('testing/method.html',
                           title='UV Fluorescence',
                           method_name='UV Fluorescence Testing',
                           overview='''UV fluorescence reveals how gemstones react to ultraviolet light.
                           Many gems glow specific colors under UV, which aids identification and can
                           indicate treatments or synthetic origin.''',
                           how_it_works='''Gems are exposed to longwave (365nm) and shortwave (254nm)
                           UV light in a dark environment. Trace elements cause the gem to emit visible
                           light (fluorescence) in characteristic colors.''',
                           equipment=['UV lamp (longwave and shortwave)', 'Dark viewing cabinet',
                                      'UV-protective eyewear', 'White background'],
                           procedure=[
                               'Place gem on white background in UV cabinet',
                               'Dark-adapt your eyes for 30 seconds',
                               'Observe under longwave UV first',
                               'Then observe under shortwave UV',
                               'Note color, intensity, and distribution of fluorescence',
                               'Check for phosphorescence after UV is turned off'
                           ],
                           typical_values={
                               'Diamond': 'Blue (common), yellow, white, none',
                               'Ruby': 'Strong red (Burmese), weak to none (Thai)',
                               'Emerald': 'Usually inert (natural), red (some synthetics)',
                               'Kunzite': 'Strong orange-pink',
                               'Fluorite': 'Blue, violet (often strong)'
                           },
                           limitations='''Fluorescence varies within gem species. Some treatments affect
                           fluorescence. Never look directly at UV light without protection.''')


@bp.route('/inclusion-analysis')
def inclusion_analysis():
    """Inclusion Analysis testing method"""
    return render_template('testing/method.html',
                           title='Inclusion Analysis',
                           method_name='Inclusion Analysis',
                           overview='''Inclusions are internal features that provide crucial information
                           about a gem's identity, origin, and whether it's natural or synthetic. They
                           are the gemstone's "fingerprint."''',
                           how_it_works='''Using microscopy and specialized lighting, gemologists identify
                           and document inclusions. Different gem species, localities, and formation
                           conditions produce characteristic inclusion assemblages.''',
                           equipment=['Gemological microscope', 'Darkfield and brightfield illumination',
                                      'Fiber optic lighting', 'Immersion cell', 'Reference materials'],
                           procedure=[
                               'Examine gem under various lighting conditions',
                               'Identify inclusion types (crystals, needles, liquids, etc.)',
                               'Note distribution patterns and relationships',
                               'Compare with known reference inclusions',
                               'Document findings with photomicrography'
                           ],
                           typical_values={
                               'Burma Ruby': 'Short rutile silk, calcite, apatite',
                               'Kashmir Sapphire': 'Tourmaline, zircon, "milky" appearance',
                               'Colombian Emerald': 'Three-phase inclusions, pyrite',
                               'Zambian Emerald': 'Amphibole, mica, blocky inclusions',
                               'Sri Lanka Sapphire': 'Long rutile silk, zircon halos'
                           },
                           limitations='''Clean gems may lack diagnostic inclusions. Some inclusions
                           are common to multiple localities. Expert interpretation required.''')


@bp.route('/dichroscope')
def dichroscope():
    """Dichroscope Analysis testing method"""
    return render_template('testing/method.html',
                           title='Dichroscope Analysis',
                           method_name='Dichroscope Analysis',
                           overview='''The dichroscope detects pleochroism—the property of showing
                           different colors when viewed from different directions. It's essential for
                           identifying many colored gemstones.''',
                           how_it_works='''The dichroscope uses calcite or polarizing filters to split
                           light into two polarized beams. If the gem is pleochroic, two different
                           colors appear side by side in the viewing window.''',
                           equipment=['Calcite dichroscope or polarizing filter type',
                                      'Strong light source (LED or daylight)',
                                      'Dark background'],
                           procedure=[
                               'Hold the dichroscope close to your eye',
                               'Position the gem between the dichroscope and light',
                               'Rotate the gem slowly while observing',
                               'Note if one color or two colors are visible',
                               'Check multiple orientations for strongest pleochroism'
                           ],
                           typical_values={
                               'Ruby': 'Strong: purplish-red / orangy-red',
                               'Blue Sapphire': 'Strong: violetish-blue / greenish-blue',
                               'Emerald': 'Distinct: bluish-green / yellowish-green',
                               'Tanzanite': 'Strong: blue / purple / green-yellow',
                               'Tourmaline': 'Strong: dark / light body color'
                           },
                           limitations='''Singly refractive gems (diamond, spinel, garnet) show no
                           pleochroism. Pale gems may show weak effects. Orientation affects results.''')


@bp.route('/polariscope')
def polariscope():
    """Polariscope Analysis testing method"""
    # Fetch gem optical character data from API
    typical_values = {}

    try:
        base_url = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
        token = load_api_key() or ''
        headers = {'X-API-Key': token} if token else {}

        # Fetch all gem test properties
        response = requests.get(
            f"{base_url.rstrip('/')}/api/v2/gem-test-properties",
            params={'limit': 1000},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            test_props = response.json()

            # Also fetch gem names to match with test properties
            gems_response = requests.get(
                f"{base_url.rstrip('/')}/api/v2/gems",
                params={'limit': 1000},
                headers=headers,
                timeout=10
            )

            if gems_response.status_code == 200:
                gems = gems_response.json()
                gem_names = {g.get('GemTypeId'): g.get('GemTypeName') for g in gems}

                # Build typical values from optical character data
                for prop in test_props:
                    gem_id = prop.get('GemTypeId')
                    gem_name = gem_names.get(gem_id, f'Gem {gem_id}')
                    optical_char = prop.get('OpticalCharacter')

                    if optical_char:
                        typical_values[gem_name] = optical_char
    except Exception as e:
        current_app.logger.warning(f"Failed to load gem test properties from API: {e}")
        # Fall back to empty data - template will still render
        typical_values = {}

    return render_template('testing/method.html',
                           title='Polariscope Analysis',
                           method_name='Polariscope Analysis',
                           overview='''The polariscope determines a gem's optical character (singly or
                           doubly refractive), detects strain, and can help identify aggregate
                           materials and certain treatments.''',
                           how_it_works='''Two polarizing filters are crossed at 90°, blocking light.
                           When a doubly refractive gem is placed between them, it appears light and
                           dark as rotated. Singly refractive gems remain dark.''',
                           equipment=['Polariscope (two polarizing filters)', 'Light source',
                                      'Conoscope lens (optional for optic figure)',
                                      'Gem holder'],
                           procedure=[
                               'Cross the polarizers until the field is dark',
                               'Place the gem between the filters',
                               'Rotate the gem 360° and observe changes',
                               'If gem stays dark: singly refractive',
                               'If gem blinks light/dark 4 times: doubly refractive',
                               'Use conoscope for optic figure if doubly refractive'
                           ],
                           typical_values=typical_values,
                           limitations='''Small gems are difficult to observe. Strain can cause
                           singly refractive gems to appear doubly refractive. Practice required.''')


@bp.route('/chelsea-filter')
def chelsea_filter():
    """Chelsea Filter Test method"""
    return render_template('testing/method.html',
                           title='Chelsea Filter Test',
                           method_name='Chelsea Filter Test',
                           overview='''The Chelsea filter is a simple color filter that helps separate
                           emeralds from their simulants and can aid in identifying certain other gems.
                           It transmits only deep red and yellow-green light.''',
                           how_it_works='''Chrome-bearing gems (like natural emerald) absorb yellow-green
                           and transmit red light through the filter, appearing pink to red. Non-chrome
                           green gems remain green or grayish.''',
                           equipment=['Chelsea filter', 'Strong incandescent or LED light',
                                      'White background', 'Known reference stones'],
                           procedure=[
                               'View the gem in good incandescent light without filter',
                               'Hold the Chelsea filter close to your eye',
                               'Observe the gem through the filter',
                               'Note the color seen (red, pink, green, or gray)',
                               'Compare with known reference stones'
                           ],
                           typical_values={
                               'Colombian Emerald': 'Pink to red (chrome)',
                               'Zambian Emerald': 'Often weaker reaction',
                               'Green Glass': 'Remains green or gray',
                               'Chrome Tourmaline': 'Red (similar to emerald)',
                               'Synthetic Emerald': 'Strong red (high chrome)'
                           },
                           limitations='''Not definitive—chrome tourmaline and some synthetic emeralds
                           show similar reactions. Some natural emeralds show weak or no reaction.
                           Should be used with other tests.''')

