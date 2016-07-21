# The MIT License
#
#  Copyright 2015 UB Bochum <bibliographie-ub@rub.de>.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import logging
import uuid
import base64
import datetime
import re
import xmlrpc.client
from io import BytesIO

import requests
from requests import RequestException
import simplejson as json
import wtforms_json
import orcid
import time
from flask import Flask, render_template, redirect, request, jsonify, flash, url_for, Markup, g, send_file
from flask.ext.babel import Babel, lazy_gettext, gettext
from flask.ext.bootstrap import Bootstrap
from flask.ext.paginate import Pagination
from flask_humanize import Humanize
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required, \
    make_secure_token
from flask.ext.socketio import SocketIO, emit
from flask_wtf.csrf import CsrfProtect
from flask_redis import Redis
from urllib import parse
from lxml import etree
from datadiff import diff_dict
from fuzzywuzzy import fuzz
from multiprocessing import Pool
from solr_handler import Solr
from processors import mods_processor
from forms import *
import ast
import vocabularies

try:
    import site_secrets as secrets
except ImportError:
    import secrets

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-4s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)

if secrets.DIFFERENT_PROXY_PATH:
    app.wsgi_app = ReverseProxied(app.wsgi_app)

app.debug = True
app.secret_key = secrets.key

app.config['DEBUG_TB_INTERCEPT_REDIRECTS '] = False

Redis(app, 'REDIS_CONSOLIDATE_PERSONS')
Redis(app, 'REDIS_REPLACE_URIS')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

babel = Babel(app)
humanize_filter = Humanize(app)

bootstrap = Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = secrets.BOOTSTRAP_SERVE_LOCAL

if not secrets.APP_SECURITY:
    app.config['WTF_CSRF_ENABLED'] = False

csrf = CsrfProtect(app)

wtforms_json.init()

socketio = SocketIO(app)

FORM_COUNT_RE = re.compile('-\d+$')
GND_RE = re.compile('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')
UUID_RE = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

PUBTYPE2TEXT = {
    'ArticleJournal': lazy_gettext('Article in Journal'),
    'ArticleNewspaper': lazy_gettext('Article in Newspaper'),
    'AudioBook': lazy_gettext('Audio Book'),
    'AudioVideoDocument': lazy_gettext('Audio or Video Document'),
    'Chapter': lazy_gettext('Chapter in...'),
    'ChapterInLegalCommentary': lazy_gettext('Chapter in a Legal Commentary'),
    'ChapterInMonograph': lazy_gettext('Chapter in a Monograph'),
    'Collection': lazy_gettext('Collection'),
    'Conference': lazy_gettext('Conference'),
    'Edition': lazy_gettext('Edition'),
    'InternetDocument': lazy_gettext('Internet Document'),
    'Journal': lazy_gettext('Journal'),
    'Lecture': lazy_gettext('Lecture'),
    'LegalCommentary': lazy_gettext('Legal Commentary'),
    'Monograph': lazy_gettext('Monograph'),
    'MultivolumeWork': lazy_gettext('MultivolumeWork'),
    'Newspaper': lazy_gettext('Newspaper'),
    'Other': lazy_gettext('Other'),
    'Patent': lazy_gettext('Patent'),
    'PressRelease': lazy_gettext('Press Release'),
    'RadioTVProgram': lazy_gettext('Radio or TV Program'),
    'Report': lazy_gettext('Report'),
    'ResearchData': lazy_gettext('Research Data'),
    'Series': lazy_gettext('Series'),
    'Software': lazy_gettext('Software'),
    'SpecialIssue': lazy_gettext('Special Issue'),
    'Standard': lazy_gettext('Standard'),
    'Thesis': lazy_gettext('Thesis'),
}

SUBTYPE2TEXT = {
    'lexicon_article': lazy_gettext('Article in Lexicon'),
    'abstract': lazy_gettext('Abstract'),
    'afterword': lazy_gettext('Afterword'),
    'bachelor_thesis': lazy_gettext('Bachelor Thesis'),
    'diploma_thesis': lazy_gettext('Diploma Thesis'),
    'dissertation': lazy_gettext('Dissertation'),
    'dramatic_work': lazy_gettext('Dramatic Work'),
    'expert_opinion': lazy_gettext('Expert Opinion'),
    'festschrift': lazy_gettext('Festschrift'),
    'first_state_examination': lazy_gettext('1st State Examination'),
    'habilitation': lazy_gettext('Habilitation'),
    'image_database': lazy_gettext('Image Database'),
    'interview': lazy_gettext('Interview'),
    'introduction': lazy_gettext('Foreword'),
    'lecture_notes': lazy_gettext('Lecture Notes'),
    'magisterarbeit': lazy_gettext('Magisterarbeit'),
    'masters_thesis': lazy_gettext("Master's Thesis"),
    'meeting_abstract': lazy_gettext('Meeting Abstract'),
    'notated_music': lazy_gettext('Notated Music'),
    'poster': lazy_gettext('Poster'),
    'poster_abstract': lazy_gettext('Poster Abstract'),
    'report': lazy_gettext('Report'),
    'review': lazy_gettext('Review'),
    'second_state_examination': lazy_gettext('2nd State Examination'),
    'sermon': lazy_gettext('Sermon'),
}

PUBTYPE2FORM = {
    'ArticleJournal': ArticleJournalForm,
    'MultivolumeWork': MultivolumeWorkForm,
    'Monograph': MonographForm,
    'Patent': PatentForm,
    'Chapter': ChapterForm,
    'ChapterInLegalCommentary': ChapterInLegalCommentaryForm,
    'Conference': ConferenceForm,
    'Collection': CollectionForm,
    'Other': OtherForm,
    'Thesis': ThesisForm,
    'ArticleNewspaper': ArticleNewspaperForm,
    'AudioVideoDocument': AudioVideoDocumentForm,
    'Edition': EditionForm,
    'InternetDocument': InternetDocumentForm,
    'Journal': JournalForm,
    'Lecture': LectureForm,
    'LegalCommentary': LegalCommentaryForm,
    'Newspaper': NewspaperForm,
    'PressRelease': PressReleaseForm,
    'RadioTVProgram': RadioTVProgramForm,
    'Series': SeriesForm,
    'Software': SoftwareForm,
    'SpecialIssue': SpecialIssueForm,
    'Standard': StandardForm,
    'Report': ReportForm,
    'ResearchData': ResearchDataForm,
}

ROLE_MAP = {
    'abr': lazy_gettext('Abridger'),
    'act': lazy_gettext('Actor'),
    'aut': lazy_gettext('Author'),
    'aft': lazy_gettext('Author of Afterword'),
    'arr': lazy_gettext('Arranger'),
    'aui': lazy_gettext('Author of Introduction'),
    'brd': lazy_gettext('Broadcaster'),
    'chr': lazy_gettext('Choreographer'),
    'cmp': lazy_gettext('Composer'),
    'ctb': lazy_gettext('Contributor'),
    'cst': lazy_gettext('Costume Designer'),
    'cwt': lazy_gettext('Commentator for written text'),
    'dgg': lazy_gettext('Degree Granting Institution'),
    'drt': lazy_gettext('Director'),
    'edt': lazy_gettext('Editor'),
    'elg': lazy_gettext('Electrician'),
    'fmk': lazy_gettext('Filmmaker'),
    'hnr': lazy_gettext('Honoree'),
    'his': lazy_gettext('Host institution'),
    'ill': lazy_gettext('Illustrator'),
    'itr': lazy_gettext('Instrumentalist'),
    'ive': lazy_gettext('Interviewee'),
    'ivr': lazy_gettext('Interviewer'),
    'inv': lazy_gettext('Inventor'),
    'mod': lazy_gettext('Moderator'),
    'mus': lazy_gettext('Musician'),
    'org': lazy_gettext('Originator'),
    'orm': lazy_gettext('Organizer'),
    'pdr': lazy_gettext('Project Director'),
    'pht': lazy_gettext('Photographer'),
    'pmn': lazy_gettext('Production Manager'),
    'pro': lazy_gettext('Producer'),
    'prg': lazy_gettext('Programmer'),
    'pta': lazy_gettext('Patent applicant'),
    'red': lazy_gettext('Redaktor'),
    'std': lazy_gettext('Set Designer'),
    'sng': lazy_gettext('Singer'),
    'spk': lazy_gettext('Speaker'),
    'stl': lazy_gettext('Storyteller'),
    'trl': lazy_gettext('Translator'),
    'tcd': lazy_gettext('Technical Director'),
    'ths': lazy_gettext('Thesis Advisor'),
}

LANGUAGE_MAP = {
    'eng': lazy_gettext('English'),
    'ger': lazy_gettext('German'),
    'fre': lazy_gettext('French'),
    'rus': lazy_gettext('Russian'),
    'spa': lazy_gettext('Spanish'),
    'ita': lazy_gettext('Italian'),
    'jpn': lazy_gettext('Japanese'),
    'lat': lazy_gettext('Latin'),
    'zhn': lazy_gettext('Chinese'),
    'dut': lazy_gettext('Dutch'),
    'tur': lazy_gettext('Turkish'),
    'por': lazy_gettext('Portuguese'),
    'pol': lazy_gettext('Polish'),
    'gre': lazy_gettext('Greek'),
    'srp': lazy_gettext('Serbian'),
    'cat': lazy_gettext('Catalan'),
    'dan': lazy_gettext('Danish'),
    'cze': lazy_gettext('Czech'),
    'kor': lazy_gettext('Korean'),
    'ara': lazy_gettext('Arabic'),
    'hun': lazy_gettext('Hungarian'),
    'swe': lazy_gettext('Swedish'),
    'ukr': lazy_gettext('Ukranian'),
    'heb': lazy_gettext('Hebrew'),
    'hrv': lazy_gettext('Croatian'),
    'slo': lazy_gettext('Slovak'),
    'nor': lazy_gettext('Norwegian'),
    'rum': lazy_gettext('Romanian'),
    'fin': lazy_gettext('Finnish'),
    'geo': lazy_gettext('Georgian'),
    'bul': lazy_gettext('Bulgarian'),
    'grc': lazy_gettext('Ancient Greek'),
    'ind': lazy_gettext('Indonesian Language'),
    'gmh': lazy_gettext('Middle High German'),
    'mon': lazy_gettext('Mongolian Language'),
    'peo': lazy_gettext('Persian'),
    'alb': lazy_gettext('Albanian'),
    'bos': lazy_gettext('Bosnian'),
}

FREQUENCY_MAP = {
    'completely_irregular': lazy_gettext('Completely Irregular'),
    'annual': lazy_gettext('Annual'),
    'quarterly': lazy_gettext('Quarterly'),
    'semiannual': lazy_gettext('Semiannual'),
    'monthly': lazy_gettext('Monthly'),
    'bimonthly': lazy_gettext('Bimonthly'),
    'three_times_a_year': lazy_gettext('Three Times a Year'),
    'semimonthly': lazy_gettext('Semimonthly'),
    'biennial': lazy_gettext('Biannial'),
    'fifteen_issues_a_year': lazy_gettext('Fifteen Issues a Year'),
    'continuously_updated': lazy_gettext('Continuously Updated'),
    'daily': lazy_gettext('Daily'),
    'semiweekly': lazy_gettext('Semiweekly'),
    'three_times_a_week': lazy_gettext('Three Times a Week'),
    'weekly': lazy_gettext('Weekly'),
    'biweekly': lazy_gettext('Biweekly'),
    'three_times_a_month': lazy_gettext('Three Times a Month'),
    'triennial': lazy_gettext('Triennial'),
}

URL_TYPE_MAP = {
    'hp': lazy_gettext('Homepage'),
    'rg': lazy_gettext('ResearchGate'),
    'ri': lazy_gettext('ResearcherID'),
    'an': lazy_gettext('AcademiaNet'),
    'ae': lazy_gettext('Academia.edu'),
    'wp': lazy_gettext('Wikipedia'),
    'xi': lazy_gettext('Xing'),
    'li': lazy_gettext('LinkedIn'),
    'bl': lazy_gettext('Blog'),
    'fb': lazy_gettext('Facebook'),
    'tw': lazy_gettext('Twitter'),
    'ic': lazy_gettext('identi.ca'),
    'zt': lazy_gettext('Zotero'),
    'md': lazy_gettext('Mendeley'),
    'mi': lazy_gettext('Other'),
}

LICENSE_MAP = {
    'cc_zero': lazy_gettext('Creative Commons Zero - Public Domain'),
    'cc_by': lazy_gettext('Creative Commons Attribution'),
    'cc_by_sa': lazy_gettext('Creative Commons Attribution Share Alike'),
    'cc_by_nd': lazy_gettext('Creative Commons Attribution No Derivatives')
}

PERS_STATUS_MAP = {
    'alumnus': lazy_gettext('Alumnus'),
    'assistant_lecturer': lazy_gettext('Assistant Lecturer'),
    'callcenter': lazy_gettext('Callcenter'),
    'ranking': lazy_gettext('Relevant for Ranking'),
    'external': lazy_gettext('External Staff'),
    'manually_added': lazy_gettext('Manually added'),
    'official': lazy_gettext('Official'),
    'official_ns': lazy_gettext('Official, Non-Scientific'),
    'research_school': lazy_gettext('Doctoral Candidate'),
    'principal_investigator': lazy_gettext('Principal Investigator'),
    'professor': lazy_gettext('Professor'),
    'emeritus': lazy_gettext('Emeritus'),
    'teaching_assistant': lazy_gettext('Teaching Assistant'),
    'tech_admin': lazy_gettext('Technical and Administrative Staff'),
}

LANGUAGES = {
    'de': 'German',
    'de_DE': 'German',
    'en': 'English',
    'en_GB': 'English',
    'en_US': 'English'
}


@humanize_filter.localeselector
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())
    # return 'de_DE'


@app.template_filter('rem_form_count')
def rem_form_count_filter(mystring):
    """Remove trailing form counts to display only categories in FormField/FieldList combinations."""
    return FORM_COUNT_RE.sub('', mystring)


@app.template_filter('mk_time')
def mk_time_filter(mytime):
    try:
        return datetime.datetime.strptime(mytime, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return datetime.datetime.strptime(mytime, '%Y-%m-%dT%H:%M:%S.%fZ')


@app.template_filter('last_split')
def last_split_filter(category):
    return category.rsplit('-', 1)[1]


# Just a temporary hack...
@app.template_filter('get_name')
def get_name(record):
    return json.loads(record.get('wtf_json')).get('name')


@app.template_filter('filter_remove')
def filter_remove_filter(fqstring, category):
    re.compile()


@app.template_filter('deserialize_json')
def deserialize_json_filter(thejson):
    return json.loads(thejson)


def theme(ip):
    # logging.info(ip)
    site = 'dortmund'
    if ip[0].startswith('134.147') or ip[0].startswith('129.217.135.159') or ip[0].startswith('129.217.135.4'):
        site = 'bochum'
    elif ip[0].startswith('127.0.0.1') or ip[0].startswith('129.217'):
        site = 'dortmund'

    return site


def _diff_struct(a, b):
    diffs = ''
    for line in str(diff_dict(a, b)).split('\n'):
        if line.startswith('-'):
            line = line.lstrip('-')
            try:
                cat, val = line.split(': ')
                if val != "''," and cat != "'changed'":
                    diffs += Markup('<b>%s</b>: %s<br/>' % (cat.strip("'"), val.rstrip(',').strip("'")))
            except ValueError:
                pass
    return diffs


@app.route('/redis/test')
@login_required
def redis_test():
    if secrets.APP_SECURITY:
        if current_user.role != 'superadmin':
            flash(gettext('For SuperAdmins ONLY!!!'))
            return redirect(url_for('homepage'))
    try:
        storage_consolidate_persons = app.extensions['redis']['REDIS_CONSOLIDATE_PERSONS']
        storage_replace_uris = app.extensions['redis']['REDIS_REPLACE_URIS']

        storage_consolidate_persons.hset('test_key', 'test_id', 'test_value')  # use pipelining for consolidate persons
        storage_replace_uris.hset('test_key', 'test_id', 'test_value')

        report = storage_consolidate_persons.hgetall('test_key')
        uris = storage_replace_uris.hgetall('test_key')

        logging.info(storage_consolidate_persons.dbsize())
        logging.info(storage_replace_uris.dbsize())
        storage_consolidate_persons.flushdb()
        storage_replace_uris.flushdb()
        logging.info(storage_consolidate_persons.dbsize())
        logging.info(storage_replace_uris.dbsize())

        return '%s / %s' % (report, uris)

    except Exception as e:
        logging.info('REDIS ERROR: %s' % e)
        return 'failed'


@app.route('/dedup/<idtype>/<path:id>')
def dedup(idtype='', id=''):
    resp = {'duplicate': False}
    dedup_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                      fquery=['%s:%s' % (idtype, id)], facet='false')
    dedup_solr.request()
    logging.info(dedup_solr.count())
    if dedup_solr.count() > 0:
        logging.info('poop')
        resp['duplicate'] = True

    return jsonify(resp)


@app.route('/')
@app.route('/index')
@app.route('/homepage')
def homepage():
    pagination = ''
    page = int(request.args.get('page', 1))
    records = []
    num_found = 0
    mystart = 0
    if current_user.is_authenticated:
        index_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                          start=(page - 1) * 10, query='owner:"' + current_user.email + '"', facet='false')
        index_solr.request()
        num_found = index_solr.count()
        records = index_solr.results
        if num_found == 0:
            flash(gettext("You haven't registered any records with us yet. Please do so now..."), 'danger')
        else:
            pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                                    record_name=lazy_gettext('titles'),
                                    search_msg=lazy_gettext('Showing {start} to {end} of {found} {record_name}'))
            mystart = 1 + (pagination.page - 1) * pagination.per_page
    return render_template('index.html', header=lazy_gettext('Home'), site=theme(request.access_route),
                           numFound=num_found,
                           records=records, pagination=pagination, offset=mystart - 1)


@app.route('/search/external/gbv', methods=['GET', 'POST'])
def search_gbv():
    """Retrieve GBV records by ISBN"""
    isbns = []
    if request.method == 'POST':
        logging.info(request.data)
        isbns = request.data.decode('utf-8').split('\n')
        logging.info(isbns)
    if request.method == 'GET':
        isbns = request.args.get('isbns', '').split('|')
    for isbn in isbns:
        mods = etree.parse(
            'http://sru.gbv.de/gvk?version=1.1&operation=searchRetrieve&query=pica.isb=%s&maximumRecords=10&recordSchema=mods' % isbn)
        logging.info(etree.tostring(mods))
        logging.info(mods_processor.convert(mods, 'hagena1z'))
    return 'poop'


@app.route('/search/external/crossref', methods=['GET', 'POST'])
def search_crossref():
    """Retrieve CrossRef records by DOI"""
    dois = []
    if request.method == 'POST':
        logging.info(request.data)
        dois = request.data.decode('utf-8').split('\n')
        logging.info(dois)
    if request.method == 'GET':
        dois = request.args.get('doi', '').split('|')
    for doi in dois:
        json = requests.get('http://api.crossref.org/works/%s' % doi).json()
        logging.info(json)
    return 'poop'


@app.route('/retrieve/external/wos/<path:doi>')
def fetch_wos(doi):
    ISI_NS = 'http://www.isinet.com/xrpc42'
    ISI = '{%s}' % ISI_NS
    lamr = etree.parse('lamr.xml')
    map_node = etree.Element('map')
    val_node = etree.SubElement(map_node, 'val')
    val_node.attrib['name'] = 'doi'
    val_node.text = doi
    lamr.xpath('.//isi:map[3]', namespaces={'isi': ISI_NS})[0].append(val_node)
    logging.error(etree.tostring(lamr).decode('utf8'))
    return 'poop'
    # return etree.fromstring(
    #     requests.post('https://ws.isiknowledge.com/cps/xrpc', data=etree.tostring(lamr, xml_declaration=True).decode('utf8'),
    #                   headers={'Content-Type': 'application/xml'}).text.encode('utf8'))


@app.route('/persons')
def persons():
    page = int(request.args.get('page', 1))
    mystart = 0
    query = '*:*'
    filterquery = request.values.getlist('filter')

    persons_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                        query=query, start=(page - 1) * 10, core='person',
                        sort='changed desc', json_facet=secrets.DASHBOARD_PERS_FACETS, fquery=filterquery)
    persons_solr.request()

    num_found = persons_solr.count()

    if num_found == 0:
        flash(gettext('There Are No Persons Yet!'))
        return render_template('persons.html', header=lazy_gettext('Persons'), site=theme(request.access_route),
                               facet_data=persons_solr.facets, results=persons_solr.results,
                               offset=mystart - 1, query=query, filterquery=filterquery,
                               now=datetime.datetime.now())
    else:
        pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                                record_name=lazy_gettext('titles'),
                                search_msg=lazy_gettext('Showing {start} to {end} of {found} Persons'))
        mystart = 1 + (pagination.page - 1) * pagination.per_page
    return render_template('persons.html', header=lazy_gettext('Persons'), site=theme(request.access_route),
                           facet_data=persons_solr.facets, results=persons_solr.results,
                           offset=mystart - 1, query=query, filterquery=filterquery, pagination=pagination,
                           now=datetime.datetime.now(), del_redirect='persons')


@app.route('/units')
def units():
    return 'Not Implemented Yet'


@app.route('/serials')
def serials():
    return 'Not Implemented Yet'


@app.route('/search')
def search():
    page = int(request.args.get('page', 1))
    query = request.args.get('q', '')
    # logging.info(query)
    if query == '':
        query = '*:*'
    core = request.args.get('core', 'hb2')
    # logging.info(core)

    filterquery = request.values.getlist('filter')
    sorting = request.args.get('sort', '')
    if sorting == 'relevance':
        sorting = ''
    else:
        sorting = 'fdate desc'

    search_solr = None
    if core == 'hb2':
        search_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                           core=core, start=(page - 1) * 10, query=query,
                           fquery=filterquery, sort=sorting, json_facet=secrets.SOLR_SEARCH_FACETS)
    if core == 'person':
        search_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                           core=core, start=(page - 1) * 10, query=query,
                           fquery=filterquery, sort='changed desc', json_facet=secrets.SOLR_PERSON_FACETS)
    if core == 'organisation':
        search_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                           core=core, start=(page - 1) * 10, query=query,
                           fquery=filterquery, sort='changed desc', json_facet=secrets.SOLR_ORGA_FACETS)
    if core == 'group':
        search_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                           core=core, start=(page - 1) * 10, query=query,
                           fquery=filterquery, sort='changed desc', json_facet=secrets.SOLR_GROUP_FACETS)
    search_solr.request()
    num_found = search_solr.count()
    if num_found == 1:
        if core == 'hb2':
            return redirect(url_for('show_record', record_id=search_solr.results[0].get('id'),
                                    pubtype=search_solr.results[0].get('pubtype')))
        if core == 'person':
            return redirect(url_for('show_person', person_id=search_solr.results[0].get('id')))
        if core == 'organisation':
            return redirect(url_for('show_orga', orga_id=search_solr.results[0].get('id')))
        if core == 'group':
            return redirect(url_for('show_group', group_id=search_solr.results[0].get('id')))
    elif num_found == 0:
        flash(gettext('Your Search Found no Results'))
        return redirect(url_for('homepage'))
    else:
        pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                                record_name=lazy_gettext('titles'),
                                search_msg=lazy_gettext('Showing {start} to {end} of {found} {record_name}'))
        mystart = 1 + (pagination.page - 1) * pagination.per_page
        if core == 'hb2':
            return render_template('resultlist.html', records=search_solr.results, pagination=pagination,
                                   facet_data=search_solr.facets, header=lazy_gettext('Resultlist'), target='search',
                                   core=core, site=theme(request.access_route), offset=mystart - 1, query=query,
                                   filterquery=filterquery)
        if core == 'person':
            return render_template('personlist.html', records=search_solr.results, pagination=pagination,
                                   facet_data=search_solr.facets, header=lazy_gettext('Resultlist'), target='search',
                                   core=core, site=theme(request.access_route), offset=mystart - 1, query=query,
                                   filterquery=filterquery)
        if core == 'organisation':
            return render_template('orgalist.html', records=search_solr.results, pagination=pagination,
                                   facet_data=search_solr.facets, header=lazy_gettext('Resultlist'), target='search',
                                   core=core, site=theme(request.access_route), offset=mystart - 1, query=query,
                                   filterquery=filterquery)
        if core == 'group':
            return render_template('grouplist.html', records=search_solr.results, pagination=pagination,
                                   facet_data=search_solr.facets, header=lazy_gettext('Resultlist'), target='search',
                                   core=core, site=theme(request.access_route), offset=mystart - 1, query=query,
                                   filterquery=filterquery)


@csrf.exempt
@app.route('/apparent_duplicate', methods=['GET', 'POST'])
def apparent_dup():
    if request.method == 'POST':
        logging.info(request.form.get('id'))
        logging.info(request.form.get('apparent_dup'))
        data = {}
        data.setdefault('id', request.form.get('id'))
        data.setdefault('apparent_dup', {}).setdefault('set', request.form.get('apparent_dup'))
        # requests.post('http://%s:%s/solr/%s/update' % (secrets.SOLR_HOST, secrets.SOLR_PORT, secrets.SOLR_CORE),
        #              headers={'Content-type': 'application/json'}, data=json.dumps(data))
        app_dup_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, core='hb2', data=[data])
        app_dup_solr.update()
    return jsonify(data)


@app.route('/store/mods', methods=['POST'])
def store_mods():
    """Store a collection of MODS records in Solr and SolRDF"""


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash('Error in the %s field: %s' % (getattr(form, field).label.text, error), 'error')


def _record2solr(form, action, relItems=True):
    if action == 'update':
        if form.data.get('editorial_status') == 'new':
            form.editorial_status.data = 'in_process'
        if form.data.get('editorial_status') == 'edited' and current_user.role == 'superadmin':
            form.editorial_status.data = 'final_editing'
    solr_data = {}
    has_part = []
    is_part_of = []
    other_version = []
    id = ''
    is_rubi = False
    is_tudo = False
    # TODO build openurl
    openurl = ''
    for field in form.data:
        # logging.info('%s => %s' % (field, form.data.get(field)))
        if field == 'id':
            solr_data.setdefault('id', form.data.get(field).strip())
            id = form.data.get(field).strip()
        if field == 'same_as':
            for same_as in form.data.get(field):
                if len(same_as.strip()) > 0:
                    solr_data.setdefault('same_as', []).append(same_as.strip())
        if field == 'created':
            if len(form.data.get(field).strip()) == 10:
                solr_data.setdefault('recordCreationDate', '%sT00:00:00.001Z' % form.data.get(field).strip())
            else:
                solr_data.setdefault('recordCreationDate', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        if field == 'changed':
            if len(form.data.get(field).strip()) == 10:
                solr_data.setdefault('recordChangeDate', '%sT00:00:00.001Z' % form.data.get(field).strip())
            else:
                solr_data.setdefault('recordChangeDate', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        if field == 'owner':
            for owner in form.data.get(field):
                solr_data.setdefault('owner', []).append(owner.strip())
        if field == 'catalog':
            for catalog in form.data.get(field):
                solr_data.setdefault('catalog', []).append(catalog.strip())
        if field == 'deskman' and form.data.get(field):
            solr_data.setdefault('deskman', form.data.get(field).strip())
        if field == 'editorial_status':
            solr_data.setdefault('editorial_status', form.data.get(field).strip())
        if field == 'publication_status':
            solr_data.setdefault('publication_status', form.data.get(field).strip())
        if field == 'pubtype':
            solr_data.setdefault('pubtype', form.data.get(field).strip())
        if field == 'subtype':
            solr_data.setdefault('subtype', form.data.get(field).strip())
        if field == 'title':
            solr_data.setdefault('title', form.data.get(field).strip())
            solr_data.setdefault('exacttitle', form.data.get(field).strip())
            solr_data.setdefault('sorttitle', form.data.get(field).strip())
        if field == 'other_title':
            for other_tit in form.data.get(field):
                # logging.info(other_tit)
                if other_tit.get('other_title'):
                    solr_data.setdefault('parallel_title', other_tit.get('other_title').strip())
        if field == 'issued':
            if form.data.get(field):
                solr_data.setdefault('date', form.data.get(field).replace('[', '').replace(']', '').strip())
                solr_data.setdefault('fdate', form.data.get(field).replace('[', '').replace(']', '')[0:4].strip())
                if len(form.data.get(field).replace('[', '').replace(']', '').strip()) == 4:
                    solr_data.setdefault('date_boost',
                                         '%s-01-01T00:00:00Z' % form.data.get(field).replace('[', '').replace(']',
                                                                                                              '').strip())
                elif len(form.data.get(field).replace('[', '').replace(']', '').strip()) == 7:
                    solr_data.setdefault('date_boost',
                                         '%s-01T00:00:00Z' % form.data.get(field).replace('[', '').replace(']',
                                                                                                           '').strip())
                else:
                    solr_data.setdefault('date_boost',
                                         '%sT00:00:00Z' % form.data.get(field).replace('[', '').replace(']',
                                                                                                        '').strip())
        if field == 'publisher':
            solr_data.setdefault('publisher', form.data.get(field).strip())
            solr_data.setdefault('fpublisher', form.data.get(field).strip())
        if field == 'language':
            for lang in form.data.get(field):
                solr_data.setdefault('language', []).append(lang)
        if field == 'locked':
            solr_data.setdefault('locked', form.data.get(field))
        if field == 'person':
            # für alle personen
            for idx, person in enumerate(form.data.get(field)):
                # hat die person einen namen?
                if person.get('name'):
                    solr_data.setdefault('person', []).append(person.get('name').strip())
                    solr_data.setdefault('fperson', []).append(person.get('name').strip())
                    # hat die person eine gnd-id?
                    if person.get('gnd'):
                        # logging.info('drin: gnd: %s' % person.get('gnd'))
                        solr_data.setdefault('pnd', []).append(
                            '%s#%s' % (person.get('gnd').strip(), person.get('name').strip()))
                        # prüfe, ob eine 'person' mit GND im System ist. Wenn ja, setze affiliation_context, wenn nicht
                        # schon belegt.
                        try:
                            query = 'id:%s' % person.get('gnd')
                            gnd_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                            application=secrets.SOLR_APP, core='person', query=query, facet='false',
                                            fields=['wtf_json'])
                            gnd_solr.request()
                            if len(gnd_solr.results) == 0:
                                # logging.info('keine Treffer zu gnd: %s' % person.get('gnd'))
                                flash(
                                    gettext(
                                        'IDs from relation "person" could not be found! Ref: %s' % person.get('gnd')),
                                    'warning')
                            else:
                                # setze den parameter für die boolesche zugehörigkeit
                                myjson = json.loads(gnd_solr.results[0].get('wtf_json'))
                                for catalog in myjson.get('catalog'):
                                    if 'Bochum' in catalog:
                                        # logging.info("%s, %s: yo! rubi!" % (person.get('name'), person.get('gnd')))
                                        form.person[idx].rubi.data = True
                                        solr_data.setdefault('frubi', []).append(person.get('name'))
                                        is_rubi = True
                                    if 'Dortmund' in catalog:
                                        form.person[idx].tudo.data = True
                                        solr_data.setdefault('ftudo', []).append(person.get('name'))
                                        is_tudo = True
                                # details zur zugeörigkeit ermitteln
                                for idx1, doc in enumerate(gnd_solr.results):
                                    myjson = json.loads(doc.get('wtf_json'))
                                    # logging.info(myjson)
                                    for affiliation in myjson.get('affiliation'):
                                        affiliation_id = affiliation.get('organisation_id')
                                        # logging.info(affiliation_id)
                                        # füge affiliation_context dem wtf_json hinzu
                                        if affiliation_id not in form.data.get('affiliation_context'):
                                            form.affiliation_context.append_entry(affiliation_id)
                        except AttributeError as e:
                            logging.error(e)
                    else:
                        # TODO versuche Daten aus dem'person'-Index zu holen (vgl. is_part_of oder has_part)
                        # die gndid muss dann aber auch dem 'wtf' hinzugefügt werden
                        solr_data.setdefault('pnd', []).append(
                            '%s#person-%s#%s' % (form.data.get('id'), idx, person.get('name').strip()))
        if field == 'corporation':
            for idx, corporation in enumerate(form.data.get(field)):
                if corporation.get('name'):
                    solr_data.setdefault('institution', []).append(corporation.get('name').strip())
                    solr_data.setdefault('fcorporation', []).append(corporation.get('name').strip())
                    # TODO reicht gnd hier aus? eher nein, oder?
                    if corporation.get('gnd'):
                        solr_data.setdefault('gkd', []).append(
                            '%s#%s' % (corporation.get('gnd').strip(), corporation.get('name').strip()))
                        # prüfe, ob eine 'person' mit GND im System ist. Wenn ja, setze affiliation_context, wenn nicht
                        # schon belegt.
                        try:
                            query = 'id:%s' % corporation.get('gnd')
                            gnd_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT,
                                            application=secrets.SOLR_APP, core='organisation', query=query, facet='false',
                                            fields=['wtf_json'])
                            gnd_solr.request()
                            if len(gnd_solr.results) == 0:
                                # logging.info('keine Treffer zu gnd: %s' % person.get('gnd'))
                                flash(
                                    gettext(
                                        'IDs from relation "corporation" could not be found! Ref: %s' % corporation.get('gnd')),
                                    'warning')
                                try:
                                    storage_actor_errors = app.extensions['redis']['REDIS_ACTOR_ERRORS_URL']

                                    storage_actor_errors.hset(form.data.get('id'), corporation.get('gnd'), 'corporation not found')

                                except Exception as e:
                                    logging.info('REDIS ERROR: %s' % e)
                                    return 'failed to write data'
                            else:
                                # setze den parameter für die boolesche zugehörigkeit
                                myjson = json.loads(gnd_solr.results[0].get('wtf_json'))
                                for catalog in myjson.get('catalog'):
                                    if 'Bochum' in catalog:
                                        # logging.info("%s, %s: yo! rubi!" % (corporation.get('name'), corporation.get('gnd')))
                                        form.corporation[idx].rubi.data = True
                                        solr_data.setdefault('frubi', []).append(corporation.get('name'))
                                        is_rubi = True
                                    if 'Dortmund' in catalog:
                                        form.corporation[idx].tudo.data = True
                                        solr_data.setdefault('ftudo', []).append(corporation.get('name'))
                                        is_tudo = True
                                # details zur zugeörigkeit ermitteln
                                for idx1, doc in enumerate(gnd_solr.results):
                                    myjson = json.loads(doc.get('wtf_json'))
                                    # logging.info(myjson)
                                    for affiliation in myjson.get('affiliation'):
                                        affiliation_id = affiliation.get('organisation_id')
                                        # logging.info(affiliation_id)
                                        # füge affiliation_context dem wtf_json hinzu
                                        if affiliation_id not in form.data.get('affiliation_context'):
                                            form.affiliation_context.append_entry(affiliation_id)
                        except AttributeError as e:
                            logging.error(e)
                    else:
                        solr_data.setdefault('gkd', []).append(
                            '%s#corporation-%s#%s' % (form.data.get('id'), idx, corporation.get('name').strip()))
                if corporation.get('role'):
                    if 'RadioTVProgram' in form.data.get('pubtype') and corporation.get('role')[0] == 'edt':
                        form.corporation[idx].role.data = 'brd'
                    if 'Thesis' in form.data.get('pubtype') and corporation.get('role')[0] == 'ctb':
                        form.corporation[idx].role.data = 'dgg'
        if field == 'affiliation_context':
            # TODO Datenanreicherung und ID-Verknüpfung mit "Organisation" / Wo ist der Kontext in den Bochumer Daten?
            for context in form.data.get(field):
                # logging.info(context)
                if len(context) > 0:
                    try:
                        query = 'id:%s' % context
                        parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                           application=secrets.SOLR_APP, core='organisation', query=query,
                                           facet='false', fields=['wtf_json'])
                        parent_solr.request()
                        if len(parent_solr.results) == 0:
                            query = 'account:%s' % context
                            parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                               application=secrets.SOLR_APP, core='organisation', query=query,
                                               facet='false', fields=['wtf_json'])
                            parent_solr.request()
                            if len(parent_solr.results) == 0:
                                solr_data.setdefault('fakultaet', []).append(context)
                                flash(
                                    gettext(
                                        'IDs from relation "affiliation" could not be found! Ref: %s' % context),
                                    'warning')
                            for doc in parent_solr.results:
                                myjson = json.loads(doc.get('wtf_json'))
                                # logging.info(myjson.get('pref_label'))
                                label = myjson.get('pref_label')
                                solr_data.setdefault('fakultaet', []).append(label)
                        for doc in parent_solr.results:
                            myjson = json.loads(doc.get('wtf_json'))
                            # logging.info(myjson.get('pref_label'))
                            label = myjson.get('pref_label')
                            solr_data.setdefault('fakultaet', []).append(label)
                    except AttributeError as e:
                        logging.error(e)
        if field == 'group_context':
            # TODO Datenanreicherung und ID-Verknüpfung mit "Group" / Wo ist der Kontext in den Bochumer Daten?
            for context in form.data.get(field):
                # logging.info(context)
                if len(context) > 0:
                    try:
                        query = 'id:%s' % context
                        parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                           application=secrets.SOLR_APP, core='group', query=query, facet='false',
                                           fields=['wtf_json'])
                        parent_solr.request()
                        if len(parent_solr.results) == 0:
                            solr_data.setdefault('group', []).append(context)
                            flash(
                                gettext(
                                    'IDs from relation "group" could not be found! Ref: %s' % context),
                                'warning')
                        for doc in parent_solr.results:
                            myjson = json.loads(doc.get('wtf_json'))
                            # logging.info(myjson.get('pref_label'))
                            label = myjson.get('pref_label')
                            solr_data.setdefault('group', []).append(label)
                    except AttributeError as e:
                        logging.error(e)
        if field == 'description':
            solr_data.setdefault('ro_abstract', form.data.get(field).strip())
        if field == 'container_title':
            solr_data.setdefault('journal_title', form.data.get(field).strip())
            solr_data.setdefault('fjtitle', form.data.get(field).strip())
        if field == 'apparent_dup':
            solr_data.setdefault('apparent_dup', form.data.get(field))
        if field == 'ISSN':
            try:
                for issn in form.data.get(field):
                    solr_data.setdefault('issn', []).append(issn.strip())
                    solr_data.setdefault('isxn', []).append(issn.strip())
            except AttributeError as e:
                logging.error(form.data.get('id'))
                pass
        if field == 'ISBN':
            try:
                for isbn in form.data.get(field):
                    solr_data.setdefault('isbn', []).append(isbn.strip())
                    solr_data.setdefault('isxn', []).append(isbn.strip())
            except AttributeError as e:
                logging.error(form.data.get('id'))
                pass
        if field == 'ISMN':
            try:
                for ismn in form.data.get(field):
                    solr_data.setdefault('ismn', []).append(ismn.strip())
                    solr_data.setdefault('isxn', []).append(ismn.strip())
            except AttributeError as e:
                logging.error(form.data.get('id'))
                pass
        if field == 'PMID':
            solr_data.setdefault('pmid', form.data.get(field).strip())
        if field == 'DOI':
            solr_data.setdefault('doi', form.data.get(field).strip())
        if field == 'WOSID':
            solr_data.setdefault('isi_id', form.data.get(field).strip())
        if field == 'note':
            if 'funded by the Deutsche Forschungsgemeinschaft' in form.data.get(field):
                form.DFG.data = True
                solr_data.setdefault('dfg', form.data.get('DFG'))
        if field == 'DFG':
            solr_data.setdefault('dfg', form.data.get('DFG'))
        if field == 'is_part_of' and len(form.data.get(field)) > 0:
            ipo_ids = []
            ipo_index = {}
            try:
                for idx, ipo in enumerate(form.data.get(field)):
                    if ipo:
                        # logging.info(ipo)
                        if 'is_part_of' in ipo:
                            # logging.info('POOP')
                            if ipo.get('is_part_of') != '':
                                ipo_ids.append(ipo.get('is_part_of'))
                                ipo_index.setdefault(ipo.get('is_part_of'), idx)
                        else:
                            # logging.info('PEEP')
                            ipo_ids.append(ipo)
                            ipo_index.setdefault(ipo, idx)
                query = ''
                if len(ipo_ids) > 1:
                    query = '{!terms f=id}%s' % ','.join(ipo_ids)
                if len(ipo_ids) == 1:
                    query = 'id:%s' % ipo_ids[0]
                if len(ipo_ids) > 0:
                    ipo_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                    application=secrets.SOLR_APP, query=query, rows=len(ipo_ids), facet='false', 
                                    fields=['wtf_json'])
                    ipo_solr.request()
                    if len(ipo_solr.results) == 0:
                        flash(gettext(
                            'Not all IDs from relation "is part of" could not be found! Ref: %s' % form.data.get('id')),
                            'warning')
                    for doc in ipo_solr.results:
                        myjson = json.loads(doc.get('wtf_json'))
                        is_part_of.append(myjson.get('id'))
                        idx = ipo_index.get(myjson.get('id'))
                        solr_data.setdefault('is_part_of', []).append(json.dumps({'pubtype': myjson.get('pubtype'),
                                                                                  'id': myjson.get('id'),
                                                                                  'title': myjson.get('title'),
                                                                                  'issn': myjson.get('issn'),
                                                                                  'isbn': myjson.get('isbn'),
                                                                                  'page_first': form.data.get(field)[
                                                                                      idx].get('page_first', ''),
                                                                                  'page_last': form.data.get(field)[
                                                                                      idx].get('page_last', ''),
                                                                                  'volume': form.data.get(field)[
                                                                                      idx].get('volume', ''),
                                                                                  'issue': form.data.get(field)[
                                                                                      idx].get('issue', '')}))
            except AttributeError as e:
                logging.error(e)
        if field == 'has_part' and len(form.data.get(field)) > 0:
            # for myhp in form.data.get(field):
            # logging.info('HP ' + myhp)
            hp_ids = []
            try:
                for hp in form.data.get(field):
                    if hp.get('has_part') != '':
                        hp_ids.append(hp.get('has_part'))
                logging.info('hp_ids: %s' % len(hp_ids))
                queries = []
                if len(hp_ids) == 1:
                    queries.append('id:%s' % hp_ids[0])
                if len(hp_ids) > 1:
                    query = '{!terms f=id}'
                    tmp = []
                    for hp_id in hp_ids:
                        logging.info('hp_id: %s' % hp_id)
                        logging.info('len(tmp): %s' % len(tmp))
                        logging.info('len(query): %s' % len(query + ','.join(tmp) + ',' + hp_id))
                        if len(tmp) < 2:
                            tmp.append(hp_id)
                        elif len(query + ','.join(tmp) + ',' + hp_id) < 7168:
                            tmp.append(hp_id)
                        else:
                            queries.append('{!terms f=id}%s' % ','.join(tmp))
                            tmp = [hp_id]
                    if len(tmp) > 0:
                        queries.append('{!terms f=id}%s' % ','.join(tmp))
                logging.info('queries: %s' % len(queries))
                if len(queries) > 0:
                    for query in queries:
                        hp_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                       application=secrets.SOLR_APP, query=query, rows=len(hp_ids), facet='false', 
                                       fields=['wtf_json'])
                        hp_solr.request()
                        if len(hp_solr.results) == 0:
                            flash(
                                gettext(
                                    'Not all IDs from relation "has part" could not be found! Ref: %s' % form.data.get(
                                        'id')),
                                'warning')
                        for doc in hp_solr.results:
                            myjson = json.loads(doc.get('wtf_json'))
                            has_part.append(myjson.get('id'))
                            solr_data.setdefault('has_part', []).append(json.dumps({'pubtype': myjson.get('pubtype'),
                                                                                    'id': myjson.get('id'),
                                                                                    'title': myjson.get('title'),
                                                                                    'page_first': myjson.get('is_part_of')[
                                                                                        0].get('page_first', ''),
                                                                                    'page_last': myjson.get('is_part_of')[
                                                                                        0].get('page_last', ''),
                                                                                    'volume': myjson.get('is_part_of')[
                                                                                        0].get('volume', ''),
                                                                                    'issue': myjson.get('is_part_of')[
                                                                                        0].get('issue', '')}))
                            # logging.info(solr_data.get('has_part'))
            except AttributeError as e:
                logging.error('has_part: %s' % e)
        if field == 'other_version' and len(form.data.get(field)) > 0:
            # for myov in form.data.get(field):
            # logging.info('OV ' + myov)
            ov_ids = []
            try:
                for version in form.data.get(field):
                    if version.get('other_version') != '':
                        ov_ids.append(version.get('other_version'))
                query = ''
                if len(ov_ids) > 0:
                    query = '{!terms f=id}%s' % ','.join(ov_ids)
                if len(ov_ids) == 1:
                    query = 'id:%s' % ov_ids[0]
                if len(ov_ids) > 0:
                    ov_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                   application=secrets.SOLR_APP, query=query, facet='false', fields=['wtf_json'])
                    ov_solr.request()
                    if len(ov_solr.results) == 0:
                        flash(
                            gettext(
                                'Not all IDs from relation "other version" could not be found! Ref: %s' % form.data.get(
                                    'id')),
                            'warning')
                    for doc in ov_solr.results:
                        # logging.info(json.loads(doc.get('wtf_json')))
                        myjson = json.loads(doc.get('wtf_json'))
                        other_version.append(myjson.get('id'))
                        solr_data.setdefault('other_version', []).append(json.dumps({'pubtype': myjson.get('pubtype'),
                                                                                     'id': myjson.get('id'),
                                                                                     'title': myjson.get('title'),}))
            except AttributeError as e:
                logging.error(e)
    solr_data.setdefault('rubi', is_rubi)
    solr_data.setdefault('tudo', is_tudo)
    wtf = json.dumps(form.data).replace(' "', '"')
    solr_data.setdefault('wtf_json', wtf)
    # logging.info('has_part: %s' % has_part)
    # logging.info('is_part_of: %s' % is_part_of)
    record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                       application=secrets.SOLR_APP, core='hb2', data=[solr_data])
    record_solr.update()
    # reload all records listed in has_part, is_part_of, other_version
    if relItems:
        for record_id in has_part:
            # lock record
            lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                    application=secrets.SOLR_APP, core='hb2',
                                    data=[{'id': record_id, 'locked': {'set': 'true'}}])
            lock_record_solr.update()
            # search record
            edit_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                    application=secrets.SOLR_APP, core='hb2', query='id:%s' % record_id)
            edit_record_solr.request()
            # load record in form and modify changeDate
            thedata = json.loads(edit_record_solr.results[0].get('wtf_json'))
            form = PUBTYPE2FORM.get(thedata.get('pubtype')).from_json(thedata)
            # add is_part_of to form if not exists
            exists = False
            for ipo in form.data.get('is_part_of'):
                if ipo.get('is_part_of') == id:
                    exists = True
                    break
            if not exists:
                try:
                    is_part_of_form = IsPartOfForm()
                    is_part_of_form.is_part_of.data = id
                    form.is_part_of.append_entry(is_part_of_form.data)
                    form.changed.data = str(datetime.datetime.now())
                    # save record
                    _record2solr(form, action='update', relItems=False)
                except AttributeError as e:
                    flash(gettext('ERROR linking from %s: %s' % (record_id, str(e))), 'error')
            # unlock record
            unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                      application=secrets.SOLR_APP, core='hb2',
                                      data=[{'id': record_id, 'locked': {'set': 'false'}}])
            unlock_record_solr.update()
        for record_id in is_part_of:
            # lock record
            lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                    application=secrets.SOLR_APP, core='hb2',
                                    data=[{'id': record_id, 'locked': {'set': 'true'}}])
            lock_record_solr.update()
            # search record
            edit_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                    application=secrets.SOLR_APP, core='hb2', query='id:%s' % record_id)
            edit_record_solr.request()
            # load record in form and modify changeDate
            thedata = json.loads(edit_record_solr.results[0].get('wtf_json'))
            form = PUBTYPE2FORM.get(thedata.get('pubtype')).from_json(thedata)
            # add has_part to form
            exists = False
            for hpo in form.data.get('has_part'):
                if hpo.get('has_part') == id:
                    exists = True
                    break
            if not exists:
                try:
                    has_part_form = HasPartForm()
                    has_part_form.has_part.data = id
                    form.has_part.append_entry(has_part_form.data)
                    form.changed.data = str(datetime.datetime.now())
                    # save record
                    _record2solr(form, action='update', relItems=False)
                except AttributeError as e:
                    flash(gettext('ERROR linking from %s: %s' % (record_id, str(e))), 'error')
            # unlock record
            unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                      application=secrets.SOLR_APP, core='hb2',
                                      data=[{'id': record_id, 'locked': {'set': 'false'}}])
            unlock_record_solr.update()
        for record_id in other_version:
            # lock record
            lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                    application=secrets.SOLR_APP, core='hb2',
                                    data=[{'id': record_id, 'locked': {'set': 'true'}}])
            lock_record_solr.update()
            # search record
            edit_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                    application=secrets.SOLR_APP, core='hb2', query='id:%s' % record_id)
            edit_record_solr.request()
            # load record in form and modify changeDate
            thedata = json.loads(edit_record_solr.results[0].get('wtf_json'))
            form = PUBTYPE2FORM.get(thedata.get('pubtype')).from_json(thedata)
            # add is_part_of to form
            exists = False
            for ovo in form.data.get('other_version'):
                if ovo.get('other_version') == id:
                    exists = True
                    break
            if not exists:
                try:
                    other_version_form = OtherVersionForm()
                    other_version_form.other_version.data = id
                    form.other_version.append_entry(other_version_form.data)
                    form.changed.data = str(datetime.datetime.now())
                    # save record
                    _record2solr(form, action='update', relItems=False)
                except AttributeError as e:
                    flash(gettext('ERROR linking from %s: %s' % (record_id, str(e))), 'error')
            # unlock record
            unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                      application=secrets.SOLR_APP, core='hb2',
                                      data=[{'id': record_id, 'locked': {'set': 'false'}}])
            unlock_record_solr.update()


@app.route('/orcid2name/<orcid_id>')
@login_required
def orcid2name(orcid_id=''):
    if orcid_id:
        bio = requests.get('https://pub.orcid.org/%s/orcid-bio/' % orcid_id,
                           headers={'Accept': 'application/json'}).json()
        # logging.info(bio.get('orcid-profile').get('orcid-bio').get('personal-details').get('family-name'))
    return jsonify({'name': '%s, %s' % (
    bio.get('orcid-profile').get('orcid-bio').get('personal-details').get('family-name').get('value'),
    bio.get('orcid-profile').get('orcid-bio').get('personal-details').get('given-names').get('value'))})


@app.route('/orcid/register')
@login_required
def orcid_login():
    code = request.args.get('code', '')
    api = orcid.PublicAPI(secrets.orcid_sandbox_client_id, secrets.orcid_sandbox_client_secret, sandbox=True)
    if code == '':
        url = api.get_login_url(secrets.orcid_scopes, '%s%s' % (secrets.APP_BASE_URL, url_for('orcid_login')),
                                email=current_user.email)
        return redirect(url)
    else:
        try:
            token = api.get_token_from_authorization_code(code, '%s%s' % (secrets.APP_BASE_URL, url_for('orcid_login')))
            orcid_id = token.get('orcid')

            # add orcid_id to person if exists. if not exists person then create an entity
            try:
                query = 'email:%s' % current_user.email
                person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                   application=secrets.SOLR_APP, core='person', query=query, facet='false',
                                   fields=['wtf_json'])
                person_solr.request()
                if len(person_solr.results) == 0:
                    logging.info('keine Treffer zu email in personl: %s' % current_user.email)
                for idx1, doc in enumerate(person_solr.results):
                    myjson = json.loads(doc.get('wtf_json'))
                    logging.info('id: %s' % myjson.get('id'))
                    lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                            application=secrets.SOLR_APP, core='person',
                                            data=[{'id': myjson.get('id'), 'locked': {'set': 'true'}}])
                    lock_record_solr.update()

                    edit_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                            application=secrets.SOLR_APP, query='id:%s' % myjson.get('id'),
                                            core='person', facet='false')
                    edit_person_solr.request()

                    thedata = json.loads(edit_person_solr.results[0].get('wtf_json'))

                    form = PersonAdminForm.from_json(thedata)
                    form.changed.data = str(datetime.datetime.now())
                    form.orcid.data = orcid_id

                    _person2solr(form)
                    unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                              application=secrets.SOLR_APP, core='person',
                                              data=[{'id': myjson.get('id'), 'locked': {'set': 'false'}}])
                    unlock_record_solr.update()

            except AttributeError as e:
                logging.error(e)
            flash(gettext('Your institutional account %s is now linked to your ORCID!' % orcid_id))
            return redirect(url_for('homepage'))
        except RequestException as e:
            logging.error(e.response.text)
            flash(gettext('ORCID-ERROR: %s' % e.response.text), 'error')
            return redirect(url_for('homepage'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    page = int(request.args.get('page', 1))
    mystart = 0
    query = '*:*'
    filterquery = request.values.getlist('filter')
    logging.info(filterquery)
    dashboard_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                          application=secrets.SOLR_APP, start=(page - 1) * 10, query=query,
                          sort='recordCreationDate desc', json_facet=secrets.DASHBOARD_FACETS, fquery=filterquery)
    dashboard_solr.request()

    num_found = dashboard_solr.count()
    pagination = ''
    if num_found == 0:
        flash(gettext('There Are No Records Yet!'), 'danger')
    else:
        pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                                record_name=lazy_gettext('titles'),
                                search_msg=lazy_gettext('Showing {start} to {end} of {found} {record_name}'))
        mystart = 1 + (pagination.page - 1) * pagination.per_page

    return render_template('dashboard.html', records=dashboard_solr.results, facet_data=dashboard_solr.facets,
                           header=lazy_gettext('Dashboard'), site=theme(request.access_route), offset=mystart - 1,
                           query=query, filterquery=filterquery, pagination=pagination, now=datetime.datetime.now(),
                           core='hb2', target='dashboard', del_redirect='dashboard', numFound=num_found
                           )


@app.route('/make_user/<user_id>')
@login_required
def make_user(user_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    if user_id:
        ma_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                       application=secrets.SOLR_APP, core='hb2_users', data=[{'id': user_id, 'role': {'set': 'user'}}])
        ma_solr.update()
        flash(gettext('%s downgraded to user!' % user_id), 'success')
        return redirect(url_for('superadmin'))
    else:
        flash(gettext('You did not supply an ID!'), 'danger')
        return redirect(url_for('superadmin'))


@app.route('/make_admin/<user_id>')
@login_required
def make_admin(user_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    if user_id:
        ma_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                       application=secrets.SOLR_APP, core='hb2_users', data=[{'id': user_id, 'role': {'set': 'admin'}}])
        ma_solr.update()
        flash(gettext('%s made to admin!' % user_id), 'success')
        return redirect(url_for('superadmin'))
    else:
        flash(gettext('You did not supply an ID!'), 'danger')
        return redirect(url_for('superadmin'))


@app.route('/make_superadmin/<user_id>')
@login_required
def make_superadmin(user_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    if user_id:
        ma_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                       application=secrets.SOLR_APP, core='hb2_users',
                       data=[{'id': user_id, 'role': {'set': 'superadmin'}}])
        ma_solr.update()
        flash(gettext('%s upgraded to superadmin!' % user_id), 'success')
        return redirect(url_for('superadmin'))
    else:
        flash(gettext('You did not supply an ID!'), 'danger')
        return redirect(url_for('superadmin'))


@app.route('/superadmin', methods=['GET'])
@login_required
def superadmin():
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    # Get locked records that were last changed more than one hour ago...
    page = int(request.args.get('page', 1))
    locked_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                       core='hb2',
                       fquery=['locked:true', 'recordChangeDate:[* TO NOW-1HOUR]'], sort='recordChangeDate asc',
                       start=(page - 1) * 10)
    locked_solr.request()
    num_found = locked_solr.count()
    pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                            record_name=lazy_gettext('records'),
                            search_msg=lazy_gettext('Showing {start} to {end} of {found} {record_name}'))
    mystart = 1 + (pagination.page - 1) * pagination.per_page

    solr_dumps = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, application=secrets.SOLR_APP, 
                      core='hb2_users', query='id:*.json', facet='false', rows=10000)
    solr_dumps.request()
    num_found = solr_dumps.count()
    form = FileUploadForm()

    return render_template('superadmin.html', locked_records=locked_solr.results,
                           header=lazy_gettext('Superadmin Board'),
                           import_records=solr_dumps.results, offset=mystart - 1, pagination=pagination,
                           del_redirect='superadmin', form=form, site=theme(request.access_route))


@app.route('/unlock/<record_id>', methods=['GET'])
@login_required
def unlock(record_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    if record_id:
        unlock_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, core='hb2',
                           data=[{'id': record_id, 'locked': {'set': 'false'}}])
        unlock_solr.update()

    redirect_url = 'superadmin'
    if get_redirect_target():
        redirect_url = get_redirect_target()

    return redirect(url_for(redirect_url))


@app.route('/unlock/person/<person_id>', methods=['GET'])
@login_required
def unlock_person(person_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    if person_id:
        unlock_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, core='person',
                           data=[{'id': person_id, 'locked': {'set': 'false'}}])
        unlock_solr.update()

    redirect_url = 'superadmin'
    if get_redirect_target():
        redirect_url = get_redirect_target()

    return redirect(url_for(redirect_url))


@app.route('/unlock/organisation/<orga_id>', methods=['GET'])
@login_required
def unlock_orga(orga_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    if orga_id:
        unlock_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, core='organisation',
                           data=[{'id': orga_id, 'locked': {'set': 'false'}}])
        unlock_solr.update()

    redirect_url = 'superadmin'
    if get_redirect_target():
        redirect_url = get_redirect_target()

    return redirect(url_for(redirect_url))


@app.route('/unlock/group/<group_id>', methods=['GET'])
@login_required
def unlock_group(group_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    if group_id:
        unlock_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, core='group',
                           data=[{'id': group_id, 'locked': {'set': 'false'}}])
        unlock_solr.update()

    redirect_url = 'superadmin'
    if get_redirect_target():
        redirect_url = get_redirect_target()

    return redirect(url_for(redirect_url))


@app.route('/create/from_file', methods=['GET', 'POST'])
@login_required
def file_upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        # logging.info(form.file.data.headers)
        if 'tu-dortmund' in current_user.email:
            upload_resp = requests.post(secrets.REDMINE_URL + 'uploads.json',
                                        headers={'Content-type': 'application/octet-stream',
                                                 'X-Redmine-API-Key': secrets.REDMINE_KEY},
                                        data=form.file.data.stream.read())
            logging.info(upload_resp.status_code)
            logging.info(upload_resp.headers)
            logging.info(upload_resp.text)
            logging.info(upload_resp.json())
            data = {}
            data.setdefault('issue', {}).setdefault('project_id', secrets.REDMINE_PROJECT)
            data.setdefault('issue', {}).setdefault('subject', 'Datei zur Dateneingabe')
            uploads = {}
            uploads.setdefault('token', upload_resp.json().get('upload').get('token'))
            uploads.setdefault('filename', form.file.data.filename)
            uploads.setdefault('content_type', form.file.data.mimetype)
            data.setdefault('issue', {}).setdefault('uploads', []).append(uploads)
            description = ''
            description += 'Dateiname: %s\n' % form.file.data.filename
            description += 'Melder-Mail: %s\n' % current_user.email
            description += 'Melder-Name: %s\n' % current_user.name
            description += u'Mime-Type: %s\n' % form.file.data.mimetype
            data.setdefault('issue', {}).setdefault('description', description)
            logging.info(data)
            issue_resp = requests.post(secrets.REDMINE_URL + 'issues.json', headers={'Content-type': 'application/json',
                                                                                     'X-Redmine-API-Key': secrets.REDMINE_KEY},
                                       data=json.dumps(data))
            logging.info(issue_resp.status_code)
            logging.info(issue_resp.text)
        else:
            trac = xmlrpc.client.ServerProxy(
                secrets.TRAC_URL % (secrets.TRAC_USER, secrets.TRAC_PW))
            attrs = {
                'component': 'Dateneingang',
                'owner': 'hbbot',
                'milestone': 'Kampagne2015',
                'type': 'task',
            }
            admin_record = ''
            admin_record += 'Dateiname: %s\n' % form.file.data.filename
            admin_record += 'Melder-Mail: %s\n' % current_user.email
            admin_record += 'Melder-Name: %s\n' % current_user.name
            admin_record += u'Mime-Type: %s\n' % form.file.data.mimetype
            logging.info(admin_record)
            ticket = trac.ticket.create('Datendatei: %s' % form.file.data.filename, admin_record, attrs, True)
            attachment = trac.ticket.putAttachment(str(ticket), form.file.data.filename, 'Datei zur Dateneingabe',
                                                   form.file.data.stream.read(), True)
            # return redirect('http://bibliographie-trac.ub.rub.de/ticket/' + str(ticket))
        flash(gettext(
            'Thank you for uploading your data! We will now edit them and make them available as soon as possible.'))
    return render_template('file_upload.html', header=lazy_gettext('Dashboard'), site=theme(request.access_route),
                           form=form)


@app.route('/containers')
def containers():
    return 'poop'


@app.route('/organisations')
def orgas():
    page = int(request.args.get('page', 1))
    mystart = 0
    query = '*:*'
    filterquery = request.values.getlist('filter')

    orgas_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                      application=secrets.SOLR_APP, query=query, start=(page - 1) * 10, core='organisation',
                      sort='changed desc', json_facet=secrets.DASHBOARD_ORGA_FACETS, fquery=filterquery)
    orgas_solr.request()

    num_found = orgas_solr.count()

    if num_found == 0:
        flash(gettext('There Are No Organisations Yet!'))
        return render_template('orgas.html', header=lazy_gettext('Organisations'), site=theme(request.access_route),
                               facet_data=orgas_solr.facets, results=orgas_solr.results,
                               offset=mystart - 1, query=query, filterquery=filterquery, now=datetime.datetime.now())
    else:
        pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                                record_name=lazy_gettext('titles'),
                                search_msg=lazy_gettext('Showing {start} to {end} of {found} Organisational Units'))
        mystart = 1 + (pagination.page - 1) * pagination.per_page
    return render_template('orgas.html', header=lazy_gettext('Organisations'), site=theme(request.access_route),
                           facet_data=orgas_solr.facets, results=orgas_solr.results,
                           offset=mystart - 1, query=query, filterquery=filterquery, pagination=pagination,
                           now=datetime.datetime.now())


def _orga2solr(form, action, linkChildren=True):
    tmp = {}
    parents = []
    id = form.data.get('id').strip()
    logging.info('ID: %s' % id)
    if not form.data.get('editorial_status'):
        form.editorial_status.data = 'new'
    if action == 'update':
        if form.data.get('editorial_status') == 'new':
            form.editorial_status.data = 'in_process'
        if form.data.get('editorial_status') == 'edited' and current_user.role == 'superadmin':
            form.editorial_status.data = 'final_editing'
    if not form.data.get('owner'):
        tmp.setdefault('owner', ['daten.ub@tu-dortmund.de'])
    else:
        tmp.setdefault('owner', form.data.get('owner'))
    for field in form.data:
        if field == 'orga_id':
            tmp.setdefault('orga_id', form.data.get(field))
        elif field == 'same_as':
            for same_as in form.data.get(field):
                if len(same_as.strip()) > 0:
                    tmp.setdefault('same_as', []).append(same_as.strip())
        elif field == 'alt_label':
            for alt_label in form.data.get(field):
                tmp.setdefault('alt_label', []).append(alt_label.strip())
        elif field == 'dwid':
            for account in form.data.get(field):
                tmp.setdefault('account', []).append(account.strip())
            if len(form.data.get('gnd')) == 0 and len(form.data.get(field)[0].strip()) > 0:
                form.id.data = form.data.get(field)[0].strip()
        elif field == 'gnd':
            if len(form.data.get(field)) > 0:
                tmp.setdefault('gnd', form.data.get(field).strip())
                form.id.data = form.data.get(field).strip()
        elif field == 'created':
            tmp.setdefault('created', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        elif field == 'changed':
            tmp.setdefault('changed', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        elif field == 'deskman' and form.data.get(field):
            tmp.setdefault('deskman', form.data.get(field).strip())
        elif field == 'editorial_status':
            tmp.setdefault('editorial_status', form.data.get(field))
        elif field == 'catalog':
            for catalog in form.data.get(field):
                tmp.setdefault('catalog', catalog.strip())
        elif field == 'destatis':
            for destatis in form.data.get(field):
                if destatis.get('destatis_label'):
                    tmp.setdefault('destatis_label', []).append(destatis.get('destatis_label').strip())
                if destatis.get('destatis_id'):
                    tmp.setdefault('destatis_id', []).append(destatis.get('destatis_id').strip())
        elif field == 'parent_label' and len(form.data.get('parent_label')) > 0:
            tmp.setdefault('fparent', form.data.get(field))
            tmp.setdefault('parent_label', form.data.get(field))
        elif field == 'parent_id' and len(form.data.get('parent_id')) > 0:
            parent = form.data.get(field)
            # logging.info('parent: %s' % parent)
            parents.append(parent)
            # logging.info('parents: %s' % parents)
            tmp.setdefault('parent_id', parent)
            if not form.data.get('parent_label') or len(form.data.get('parent_label')) == 0:
                try:
                    query = 'id:%s' % form.data.get(field)
                    parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                       application=secrets.SOLR_APP, core='organisation', query=query, facet='false',
                                       fields=['wtf_json'])
                    parent_solr.request()
                    logging.info('Treffer für %s: %s' % (form.data.get(field), len(parent_solr.results)))
                    if len(parent_solr.results) == 0:
                        flash(
                            gettext(
                                'IDs from relation "parent_id" could not be found! Ref: %s' % form.data.get(field)),
                            'warning')
                    else:
                        for doc in parent_solr.results:
                            myjson = json.loads(doc.get('wtf_json'))
                            # logging.info(myjson.get('pref_label'))
                            label = myjson.get('pref_label')
                            tmp.setdefault('parent_label', label)
                            tmp.setdefault('fparent', label)
                            form.parent_label.data = label
                except AttributeError as e:
                    logging.error(e)
        elif field == 'children':
            # logging.info('children in form of %s : %s' % (id, form.data.get(field)))
            # TODO search for child labels in store and extent the child fields
            for idx, child in enumerate(form.data.get(field)):
                if child:
                    if 'child_id' in child and 'child_label' in child:
                        if child.get('child_id') != '' and child.get('child_label') == '':
                            try:
                                query = 'id:%s' % child.get('child_id')
                                child_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                                  application=secrets.SOLR_APP, core='organisation', query=query, 
                                                  facet='false', fields=['wtf_json'])
                                child_solr.request()
                                if len(child_solr.results) == 0:
                                    flash(
                                        gettext(
                                            'IDs from relation "child_id" could not be found! Ref: %s' % child.get('child_id')),
                                        'warning')
                                for doc in child_solr.results:
                                    myjson = json.loads(doc.get('wtf_json'))
                                    # logging.info('child: %s / %s' % (idx, form.children[idx].data))
                                    label = myjson.get('pref_label')
                                    # logging.info('label: %s' % label)
                                    form.children[idx].child_label.data = label
                                    # logging.info('child: %s / %s' % (idx, form.children[idx].data))
                            except AttributeError as e:
                                logging.error(e)

            child_ids = []
            try:
                for child in form.data.get(field):
                    if child:
                        if 'child_id' in child:
                            if child.get('child_id') != '':
                                child_ids.append(child.get('child_id'))
                query = ''
                if len(child_ids) > 1:
                    query = '{!terms f=id}%s' % ','.join(child_ids)
                if len(child_ids) == 1:
                    query = 'id:%s' % child_ids[0]
                # logging.info('query = %s' % query)
                if len(child_ids) > 0:
                    children_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                         application=secrets.SOLR_APP, core='organisation', query=query, facet='false',
                                         fields=['wtf_json'])
                    children_solr.request()
                    if len(children_solr.results) == 0:
                        flash(gettext(
                            'Not all IDs from relation "children" could be found! Ref: %s' % form.data.get('id')),
                            'warning')
                    for idx, doc in enumerate(children_solr.results):
                        myjson = json.loads(doc.get('wtf_json'))
                        tmp.setdefault('children', []).append(json.dumps({'id': myjson.get('id'),
                                                                          'label': myjson.get('pref_label')}))
                        tmp.setdefault('fchildren', myjson.get('pref_label'))
                else:
                    for child in form.data.get(field):
                        if 'child_label' in child:
                            if child.get('child_label') != '':
                                tmp.setdefault('fchildren', child.get('child_label'))
            except AttributeError as e:
                logging.error('work on children: %s' % e)
        else:
            if form.data.get(field):
                if field != 'id':
                    tmp.setdefault(field, form.data.get(field))
    # TODO search for organisations with id in parent_id; deduplicate with existing children
    # search record
    search_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, core='organisation', rows=100, query='parent_id:%s' % id)
    search_orga_solr.request()
    if len(search_orga_solr.results) > 0:
        children = form.data.get('children')
        for result in search_orga_solr.results:
            # TODO if result.get('id') not in current children
            exists = False
            for child in children:
                logging.info('%s vs. %s' % (child.get('child_id'), result.get('id')))
                if child.get('child_id') == result.get('id'):
                    exists = True
                    break
            if not exists:
                childform = ChildForm()
                childform.child_id.data = result.get('id')
                childform.child_label.data = result.get('pref_label')
                form.children.append_entry(childform.data)
    # save record to index
    try:
        logging.info('%s vs. %s' % (id, form.data.get('id')))
        if id != form.data.get('id'):
            delete_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT,
                                    application=secrets.SOLR_APP, core='organisation', del_id=id)
            delete_orga_solr.delete()
            form.same_as.append_entry(id)
            tmp.setdefault('id', form.data.get('id'))
            tmp.setdefault('same_as', []).append(id)

            id = form.data.get('id')
        else:
            tmp.setdefault('id', id)
        # build json
        wtf_json = json.dumps(form.data)
        tmp.setdefault('wtf_json', wtf_json)
        # logging.info(tmp)
        orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT,
                         application=secrets.SOLR_APP, core='organisation', data=[tmp])
        orga_solr.update()
    except AttributeError as e:
        logging.error(e)
    # add link to parent
    if linkChildren:
        logging.info('parents: %s' % parents)
        for parent_id in parents:
            # search record
            edit_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                  application=secrets.SOLR_APP, core='organisation', query='id:%s' % parent_id)
            edit_orga_solr.request()
            # load orga in form and modify changeDate
            if len(edit_orga_solr.results) > 0:
                # lock record
                lock_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                      application=secrets.SOLR_APP, core='organisation', 
                                      data=[{'id': parent_id, 'locked': {'set': 'true'}}])
                lock_orga_solr.update()
                # edit
                try:
                    thedata = json.loads(edit_orga_solr.results[0].get('wtf_json'))
                    form = OrgaAdminForm.from_json(thedata)
                    # TODO add child to form if not exists
                    exists = False
                    for child in form.data.get('children'):
                        logging.info('%s == %s ?' % (child.get('child_id'), id))
                        if child.get('child_id') == id:
                            exists = True
                            break
                    if not exists:
                        try:
                            childform = ChildForm()
                            childform.child_id.data = id
                            form.children.append_entry(childform.data)
                            form.changed.data = str(datetime.datetime.now())
                            # save record
                            _orga2solr(form, action='update', linkChildren=False)
                        except AttributeError as e:
                            flash(gettext('ERROR linking from %s: %s' % (parent_id, str(e))), 'error')
                except TypeError as e:
                    logging.error(e)
                    logging.error('thedate: %s' % edit_orga_solr.results[0].get('wtf_json'))
                # unlock record
                unlock_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                        application=secrets.SOLR_APP, core='organisation', 
                                        data=[{'id': parent_id, 'locked': {'set': 'false'}}])
                unlock_orga_solr.update()
            else:
                logging.info('Cuurently there is no record for parent_id %s!' % parent_id)

    return id

@app.route('/create/organisation', methods=['GET', 'POST'])
@login_required
def new_orga():
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    form = OrgaAdminForm()

    if form.validate_on_submit():
        # logging.info(form.data)
        _orga2solr(form, action='create')

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return show_orga(form.data.get('id').strip())
        # return redirect(url_for('orgas'))

    form.id.data = uuid.uuid4()
    form.owner[0].data = current_user.email
    form.created.data = datetime.datetime.now()
    form.changed.data = datetime.datetime.now()
    # return render_template('linear_form.html', header=lazy_gettext('New Organisation'), site=theme(request.access_route), form=form, action='create', pubtype='organisation')
    return render_template('tabbed_form.html', header=lazy_gettext('New Organisation'),
                           site=theme(request.access_route), form=form, action='create', pubtype='organisation')


@app.route('/groups')
def groups():
    page = int(request.args.get('page', 1))
    mystart = 0
    query = '*:*'
    filterquery = request.values.getlist('filter')

    groups_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                       application=secrets.SOLR_APP, query=query, start=(page - 1) * 10, core='group',
                       sort='changed desc', json_facet=secrets.DASHBOARD_GROUP_FACETS, fquery=filterquery)
    groups_solr.request()

    num_found = groups_solr.count()

    if num_found == 0:
        flash(gettext('There Are No Working Groups Yet!'))
        return render_template('groups.html', header=lazy_gettext('Working Groups'), site=theme(request.access_route),
                               facet_data=groups_solr.facets, results=groups_solr.results,
                               offset=mystart - 1, query=query, filterquery=filterquery, now=datetime.datetime.now())
    else:
        pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                                record_name=lazy_gettext('titles'),
                                search_msg=lazy_gettext('Showing {start} to {end} of {found} Working Groups'))
        mystart = 1 + (pagination.page - 1) * pagination.per_page
    return render_template('groups.html', header=lazy_gettext('Working Groups'), site=theme(request.access_route),
                           facet_data=groups_solr.facets, results=groups_solr.results,
                           offset=mystart - 1, query=query, filterquery=filterquery, pagination=pagination,
                           now=datetime.datetime.now())


def _group2solr(form, action):
    tmp = {}
    if not form.data.get('editorial_status'):
        form.editorial_status.data = 'new'
    if action == 'update':
        if form.data.get('editorial_status') == 'new':
            form.editorial_status.data = 'in_process'
        if form.data.get('editorial_status') == 'edited' and current_user.role == 'superadmin':
            form.editorial_status.data = 'final_editing'
    if not form.data.get('owner'):
        tmp.setdefault('owner', ['daten.ub@tu-dortmund.de'])
    else:
        tmp.setdefault('owner', form.data.get('owner'))
    for field in form.data:
        if field == 'group_id':
            tmp.setdefault('group_id', form.data.get(field))
        elif field == 'same_as':
            for same_as in form.data.get(field):
                if len(same_as.strip()) > 0:
                    tmp.setdefault('same_as', []).append(same_as.strip())
        elif field == 'alt_label':
            for alt_label in form.data.get(field):
                tmp.setdefault('alt_label', []).append(alt_label.data.strip())
        elif field == 'dwid':
            tmp.setdefault('account', form.data.get(field))
        elif field == 'gnd':
            tmp.setdefault('gnd', form.data.get(field))
        elif field == 'created':
            tmp.setdefault('created', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        elif field == 'changed':
            tmp.setdefault('changed', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        elif field == 'deskman' and form.data.get(field):
            tmp.setdefault('deskman', form.data.get(field).strip())
        elif field == 'editorial_status':
            tmp.setdefault('editorial_status', form.data.get(field))
        elif field == 'catalog':
            for catalog in form.data.get(field):
                tmp.setdefault('catalog', catalog.strip())
        elif field == 'destatis':
            for destatis in form.data.get(field):
                if destatis.get('destatis_label'):
                    tmp.setdefault('destatis_label', []).append(destatis.get('destatis_label').strip())
                if destatis.get('destatis_id'):
                    tmp.setdefault('destatis_id', []).append(destatis.get('destatis_id').strip())
        elif field == 'parent_id' and len(form.data.get('parent_id')) > 0 and (
            not form.data.get('parent_label') or len(form.data.get('parent_label')) == 0):
            tmp.setdefault('parent_id', form.data.get(field))
            try:
                query = 'id:%s' % form.data.get(field)
                parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                   application=secrets.SOLR_APP, core='group', query=query, facet='false',
                                   fields=['wtf_json'])
                parent_solr.request()
                if len(parent_solr.results) == 0:
                    flash(
                        gettext(
                            'IDs from relation "parent_id" could not be found! Ref: %s' % form.data.get(field)),
                        'warning')
                for doc in parent_solr.results:
                    myjson = json.loads(doc.get('wtf_json'))
                    # logging.info(myjson.get('pref_label'))
                    label = myjson.get('pref_label')
                    tmp.setdefault('parent_label', label)
                    tmp.setdefault('fparent', label)
                    form.parent_label.data = label
            except AttributeError as e:
                logging.error(e)
        elif field == 'parent_label' and len(form.data.get('parent_label')) > 0 and (
            not form.data.get('parent_id') or len(form.data.get('parent_id')) == 0):
            tmp.setdefault('fparent', form.data.get(field))
            tmp.setdefault('parent_label', form.data.get(field))
        else:
            if form.data.get(field):
                tmp.setdefault(field, form.data.get(field))
    wtf_json = json.dumps(form.data)
    tmp.setdefault('wtf_json', wtf_json)
    # logging.info(tmp)
    groups_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                       application=secrets.SOLR_APP, core='group', data=[tmp])
    groups_solr.update()


@app.route('/create/group', methods=['GET', 'POST'])
@login_required
def new_group():
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    form = GroupAdminForm()

    if form.validate_on_submit():
        # logging.info(form.data)
        _group2solr(form)

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return show_group(form.data.get('id').strip())
        # return redirect(url_for('groups'))

    form.id.data = uuid.uuid4()
    form.owner[0].data = current_user.email
    form.created.data = datetime.datetime.now()
    form.changed.data = datetime.datetime.now()

    return render_template('linear_form.html', header=lazy_gettext('New Working Group'),
                           site=theme(request.access_route), form=form, action='create', pubtype='group')


def _person2solr(form, action):
    tmp = {}
    if not form.data.get('editorial_status'):
        form.editorial_status.data = 'new'
    if action == 'update':
        if form.data.get('editorial_status') == 'new':
            form.editorial_status.data = 'in_process'
        if form.data.get('editorial_status') == 'edited' and current_user.role == 'superadmin':
            form.editorial_status.data = 'final_editing'
    if not form.data.get('owner'):
        tmp.setdefault('owner', ['daten.ub@tu-dortmund.de'])
    else:
        tmp.setdefault('owner', form.data.get('owner'))

    new_id = form.data.get('id')
    for field in form.data:
        if field == 'name':
            tmp.setdefault('name', form.data.get(field).strip())
        elif field == 'same_as':
            for same_as in form.data.get(field):
                if len(same_as.strip()) > 0:
                    tmp.setdefault('same_as', []).append(same_as.strip())
        elif field == 'gnd':
            if len(form.data.get(field).strip()) > 0:
                tmp.setdefault('gnd', form.data.get(field).strip())
                new_id = form.data.get(field).strip()
        elif field == 'dwid':
            tmp.setdefault('dwid', form.data.get(field))
            logging.info('%s vs. %s' % (form.data.get(field).strip(), form.data.get('gnd')))
            if len(form.data.get('gnd')) == 0 and len(form.data.get(field).strip()) > 0:
                new_id = form.data.get(field).strip().strip()
        elif field == 'email':
            tmp.setdefault('email', form.data.get(field))
        elif field == 'rubi':
            tmp.setdefault('rubi', form.data.get(field))
        elif field == 'tudo':
            tmp.setdefault('tudo', form.data.get(field))
        elif field == 'created':
            tmp.setdefault('created', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        elif field == 'changed':
            tmp.setdefault('changed', form.data.get(field).strip().replace(' ', 'T') + 'Z')
        elif field == 'catalog':
            for catalog in form.data.get(field):
                tmp.setdefault('catalog', catalog.strip())
        elif field == 'status':
            for status in form.data.get(field):
                tmp.setdefault('personal_status', []).append(status.strip())
        elif field == 'editorial_status':
            tmp.setdefault('editorial_status', form.data.get(field))
        elif field == 'deskman' and form.data.get(field):
            tmp.setdefault('deskman', form.data.get(field).strip())
        elif field == 'catalog':
            for catalog in form.data.get(field):
                tmp.setdefault('catalog', catalog.strip())
        elif field == 'research_interest':
            for research_interest in form.data.get(field):
                tmp.setdefault('research_interest', []).append(research_interest.strip())
        elif field == 'url':
            for url in form.data.get(field):
                tmp.setdefault('url', []).append(url.get('label').strip())
        elif field == 'membership':
            for membership in form.data.get(field):
                if membership.get('label'):
                    tmp.setdefault('membership', []).append(membership.get('label').strip())
        elif field == 'award':
            for award in form.data.get(field):
                if award.get('label'):
                    tmp.setdefault('award', []).append(award.get('label').strip())
        elif field == 'project':
            for project in form.data.get(field):
                if project.get('label'):
                    tmp.setdefault('project', []).append(project.get('label').strip())
                if project.get('project_id') and project.get('label'):
                    tmp.setdefault('project_id', []).append(
                        '%s#%s' % (project.get('project_id').strip(), project.get('label').strip()))
                if project.get('project_type'):
                    tmp.setdefault('project_type', []).append(project.get('project_type'))
        elif field == 'thesis':
            for thesis in form.data.get(field):
                if thesis.get('label'):
                    tmp.setdefault('thesis', []).append(thesis.get('label').strip())
        elif field == 'affiliation':
            for affiliation in form.data.get(field):
                if affiliation.get('label'):
                    tmp.setdefault('affiliation', []).append(affiliation.get('label').strip())
                    tmp.setdefault('faffiliation', []).append(affiliation.get('label').strip())
                else:
                    if len(affiliation.get('organisation_id')) > 0:
                        try:
                            query = 'id:%s' % affiliation.get('organisation_id')
                            parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                               application=secrets.SOLR_APP, core='organisation', query=query,
                                               facet='false', fields=['wtf_json'])
                            parent_solr.request()
                            if len(parent_solr.results) == 0:
                                query = 'account:%s' % affiliation.get('organisation_id')
                                parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                                   application=secrets.SOLR_APP, core='organisation', query=query,
                                                   facet='false', fields=['wtf_json'])
                                parent_solr.request()
                                if len(parent_solr.results) == 0:
                                    flash(
                                        gettext(
                                            'IDs from relation "organisation_id" could not be found! Ref: %s' % affiliation.get(
                                                'organisation_id')),
                                        'warning')
                                for doc in parent_solr.results:
                                    myjson = json.loads(doc.get('wtf_json'))
                                    # logging.info(myjson.get('pref_label'))
                                    label = myjson.get('pref_label')
                                    tmp.setdefault('affiliation', []).append(label.strip())
                                    tmp.setdefault('faffiliation', []).append(label.strip())
                            for doc in parent_solr.results:
                                myjson = json.loads(doc.get('wtf_json'))
                                # logging.info(myjson.get('pref_label'))
                                label = myjson.get('pref_label')
                                tmp.setdefault('affiliation', []).append(label.strip())
                                tmp.setdefault('faffiliation', []).append(label.strip())
                        except AttributeError as e:
                            logging.error(e)
        elif field == 'group':
            for group in form.data.get(field):
                if group.get('label'):
                    tmp.setdefault('group', []).append(group.get('label').strip())
                    tmp.setdefault('fgroup', []).append(group.get('label').strip())
                else:
                    if len(group.get('group_id')) > 0:
                        try:
                            query = 'id:%s' % group.get('group_id')
                            parent_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                               application=secrets.SOLR_APP, core='group', query=query, facet='false',
                                               fields=['wtf_json'])
                            parent_solr.request()
                            if len(parent_solr.results) == 0:
                                flash(
                                    gettext(
                                        'IDs from relation "group_id" could not be found! Ref: %s' % group.get(
                                            'group_id')),
                                    'warning')
                            for doc in parent_solr.results:
                                myjson = json.loads(doc.get('wtf_json'))
                                # logging.info(myjson.get('pref_label'))
                                label = myjson.get('pref_label')
                                tmp.setdefault('group', []).append(label.strip())
                                tmp.setdefault('fgroup', []).append(label.strip())
                        except AttributeError as e:
                            logging.error(e)
        elif field == 'cv':
            for cv in form.data.get(field):
                if cv.get('label'):
                    tmp.setdefault('cv', []).append(cv.get('label').strip())
        elif field == 'editor':
            for editor in form.data.get(field):
                if editor.get('label'):
                    tmp.setdefault('editor', []).append(editor.get('label').strip())
                if editor.get('issn'):
                    tmp.setdefault('editor_issn', []).append(editor.get('issn'))
                if editor.get('zdbid'):
                    tmp.setdefault('editor_zdbid', []).append(editor.get('zdbid'))
        elif field == 'reviewer':
            for reviewer in form.data.get(field):
                if reviewer.get('label'):
                    tmp.setdefault('reviewer', []).append(reviewer.get('label').strip())
                if reviewer.get('issn'):
                    tmp.setdefault('reviewer_issn', []).append(reviewer.get('issn'))
                if reviewer.get('zdbid'):
                    tmp.setdefault('reviewer_zdbid', []).append(reviewer.get('zdbid'))
        else:
            if form.data.get(field):
                if field != 'id':
                    # logging.info('%s => %s' % (field, form.data.get(field)))
                    tmp.setdefault(field, form.data.get(field))

    doit = False
    if action == 'create':
        person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, core='person', query='id:%s' % new_id,
                           facet='false', fields=['wtf_json'])
        person_solr.request()
        if len(person_solr.results) == 0:
            doit = True
    else:
        doit = True

    # logging.info('new_id: %s for %s' % (new_id, form.data.get('id')))
    # logging.info('doit: %s for %s' % (doit, form.data.get('id')))

    if doit:
        if new_id != form.data.get('id'):
            form.same_as.append_entry(form.data.get('id'))
            tmp.setdefault('same_as', []).append(form.data.get('id'))
            # delete record with current id
            try:
                delete_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT,
                                          application=secrets.SOLR_APP, core='person', del_id=form.data.get('id'))
                delete_person_solr.delete()
            except AttributeError as e:
                logging.error(e)
            form.id.data = new_id
        tmp.setdefault('id', new_id)
        wtf_json = json.dumps(form.data)
        tmp.setdefault('wtf_json', wtf_json)
        person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, core='person', data=[tmp])
        person_solr.update()

    return doit, new_id


@app.route('/create/person', methods=['GET', 'POST'])
@login_required
def new_person():
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    form = PersonAdminForm()
    if form.validate_on_submit():
        # logging.info(form.data)
        doit, new_id = _person2solr(form, action='create')
        if doit:

            time.sleep(secrets.WAITING_FOR_REDIRECT)
            return show_person(form.data.get('id').strip())
            # return redirect(url_for('persons'))
        else:
            flash(gettext('A person with id %s already exists!' % new_id), 'danger')
            return render_template('tabbed_form.html', header=lazy_gettext('New Person'),
                                   site=theme(request.access_route), form=form, action='create', pubtype='person')

    form.created.data = datetime.datetime.now()
    form.changed.data = datetime.datetime.now()
    form.id.data = uuid.uuid4()
    form.owner[0].data = current_user.email

    return render_template('tabbed_form.html', header=lazy_gettext('New Person'), site=theme(request.access_route),
                           form=form, action='create', pubtype='person')


@app.route('/create/person_from_gnd', methods=['GET', 'POST'])
@login_required
def new_person_from_gnd():
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    gndid = request.args.get('gndid', '')
    if gndid == '':
        # render id request form
        form = PersonFromGndForm()
        if form.validate_on_submit():
            return redirect(url_for('new_person_from_gnd', gndid=form.data.get('gnd')))

        return render_template('linear_form.html', header=lazy_gettext('New Person from GND'),
                               site=theme(request.access_route), form=form, action='create', pubtype='person_from_gnd')
    else:
        # get data fron GND and render pre filled person form
        url = 'http://d-nb.info/gnd/%s/about/lds.rdf' % gndid

        # get data, convert and put to PersonAdminForm
        RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        GNDO = 'http://d-nb.info/standards/elementset/gnd#'
        OWL = 'http://www.w3.org/2002/07/owl#'
        NSDICT = {'r': RDF, 'g': GNDO, 'o': OWL}

        record = etree.parse(url)
        logging.info(etree.tostring(record))

        if record:
            form = PersonAdminForm()

            if record.xpath('//g:preferredNameForThePerson', namespaces=NSDICT):
                logging.info('Name: %s' % record.xpath('//g:preferredNameForThePerson', namespaces=NSDICT)[0].text)
                form.name.data = record.xpath('//g:preferredNameForThePerson', namespaces=NSDICT)[0].text
            if record.xpath('//g:gender', namespaces=NSDICT):
                logging.info('Gender: %s' % record.xpath('//g:gender/@r:resource', namespaces=NSDICT)[0])
                if 'male' in record.xpath('//g:gender/@r:resource', namespaces=NSDICT)[0]:
                    form.salutation.data = 'm'
                elif 'female' in record.xpath('//g:gender/@r:resource', namespaces=NSDICT)[0]:
                    form.salutation.data = 'f'
            if record.xpath('//o:sameAs', namespaces=NSDICT):
                if 'orcid' in record.xpath('//o:sameAs/@r:resource', namespaces=NSDICT)[0]:
                    logging.info(
                        'ORCID: %s' % record.xpath('//o:sameAs/@r:resource', namespaces=NSDICT)[0].split('org/')[1])
                    form.orcid.data = record.xpath('//o:sameAs/@r:resource', namespaces=NSDICT)[0].split('org/')[1]
            if record.xpath('//g:affiliation', namespaces=NSDICT):
                logging.info('Affiliation: %s' %
                             record.xpath('//g:affiliation/@r:resource', namespaces=NSDICT)[0].split('/gnd/')[1])
                form.affiliation[0].organisation_id.data = \
                record.xpath('//g:affiliation/@r:resource', namespaces=NSDICT)[0].split('/gnd/')[1]

            form.gnd.data = gndid

            form.created.data = str(datetime.datetime.now())
            form.changed.data = str(datetime.datetime.now())
            form.id.data = uuid.uuid4()
            form.owner[0].data = current_user.email

            # is gndid or name or orcid currently in hb2?
            try:
                query = 'gnd:%s' % form.data.get('gnd')
                person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                   application=secrets.SOLR_APP, core='person', query=query, facet='false',
                                   fields=['id'])
                person_solr.request()
                if len(person_solr.results) > 0:
                    flash('%s is apparently duplicate: %s! (GND id found.)' % (gndid, person_solr.results[0].get('id')),
                          category='warning')
                else:
                    query = 'orcid:%s' % form.data.get('orcid')
                    person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                       application=secrets.SOLR_APP, core='person', query=query, facet='false',
                                       fields=['id'])
                    person_solr.request()
                    if len(person_solr.results) > 0:
                        flash('%s is apparently duplicate: %s! (ORCID found.)' % (
                        gndid, person_solr.results[0].get('id')), category='warning')
                    else:
                        query = 'name:%s' % form.data.get('name')
                        person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                           application=secrets.SOLR_APP, core='person', query=query, facet='false',
                                           fields=['id'])
                        person_solr.request()
                        if len(person_solr.results) > 0:
                            for person in person_solr.results:
                                flash('%s is apparently duplicate: %s! (Name found.)' % (gndid, person.get('id')),
                                      category='warning')
            except AttributeError as e:
                logging.error(e)

            return render_template('tabbed_form.html', form=form,
                                   header=lazy_gettext('Edit: %(person)s', person=form.data.get('name')),
                                   locked=True, site=theme(request.access_route), action='update', pubtype='person',
                                   record_id=form.data.get('id'))
        else:
            flash(gettext('The requested ID %s is not known in GND!' % gndid))
            return redirect(url_for('/create/person_from_gnd'))


@app.route('/create/person_from_orcid', methods=['GET', 'POST'])
@login_required
def new_person_from_orcid(orcid=''):
    if request.method == 'GET':
        # render id request form
        return render_template('person_from_orcid.html')
    else:
        # get data fron ORCID and render pre filled person form
        url = 'http://d-nb.info/gnd/%s/about/lds.xml' % orcid

        # get data, convert and put to PersonAdminForm

        return render_template('tabbed_form.html', form=form,
                               header=lazy_gettext('Edit: %(person)s', person=form.data.get('name')),
                               locked=True, site=theme(request.access_route), action='update', pubtype='person',
                               record_id=person_id)


@app.route('/create/publication')
@login_required
def new_by_form():
    return render_template('pubtype_list.html', header=lazy_gettext('New Record by Publication Type'),
                           site=theme(request.access_route))


@app.route('/create/from_identifiers')
@login_required
def new_by_identifiers():
    return ('Not implemented yet...')


@app.route('/create/from_search')
@login_required
def new_by_search():
    return ('Not implemented yet...')


@app.route('/create/<pubtype>', methods=['GET', 'POST'])
@login_required
def new_record(pubtype='ArticleJournal'):
    form = PUBTYPE2FORM.get(pubtype)()

    # logging.info(form)

    if request.is_xhr:
        logging.info(request.form)
        form = PUBTYPE2FORM.get(pubtype)(request.form)
        logging.info(form)
        # logging.info(request.form.person)
        # Do we have any data already?
        if not form.title.data:
            solr_data = {}
            wtf = json.dumps(form.data)
            solr_data.setdefault('wtf_json', wtf)
            for field in form.data:
                # logging.info('%s => %s' % (field, form.data.get(field)))
                if field == 'id':
                    solr_data.setdefault('id', form.data.get(field).strip())
                if field == 'created':
                    solr_data.setdefault('recordCreationDate', form.data.get(field).strip().replace(' ', 'T') + 'Z')
                if field == 'changed':
                    solr_data.setdefault('recordChangeDate', form.data.get(field).strip().replace(' ', 'T') + 'Z')
                if field == 'owner':
                    solr_data.setdefault('owner', form.data.get(field).strip())
                if field == 'pubtype':
                    solr_data.setdefault('pubtype', form.data.get(field).strip())
                if field == 'editorial_status':
                    solr_data.setdefault('editorial_status', form.data.get(field).strip())
            record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                               application=secrets.SOLR_APP, core='hb2', data=[solr_data])
            record_solr.update()
        else:
            _record2solr(form, action='create')
        return jsonify({'status': 200})

    for person in form.person:
        if current_user.role == 'admin' or current_user.role == 'superadmin':
            person.role.choices = vocabularies.ADMIN_ROLES
        else:
            person.role.choices = vocabularies.USER_ROLES

    if current_user.role == 'admin' or current_user.role == 'superadmin':
        form.pubtype.choices = vocabularies.ADMIN_PUBTYPES
    else:
        form.pubtype.choices = vocabularies.USER_PUBTYPES

    if form.validate_on_submit():
        # logging.info(form)
        # logging.info(form.person.name)
        if form.errors:
            flash_errors(form)
            return render_template('tabbed_form.html', form=form, header=lazy_gettext('New Record'),
                                   site=theme(request.access_route), action='create', pubtype=pubtype)
        _record2solr(form, action='create')
        # return redirect(url_for('dashboard'))
        # logging.info(form.data)
        # logging.info(form.data.get('id').strip())

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return show_record(pubtype, form.data.get('id').strip())

    if request.args.get('subtype'):
        form.subtype.data = request.args.get('subtype')
    form.id.data = str(uuid.uuid4())
    form.created.data = datetime.datetime.now()
    form.changed.data = datetime.datetime.now()
    form.owner[0].data = current_user.email
    form.pubtype.data = pubtype

    # for person in form.person:
    #    if current_user.role == 'admin':
    #        person.role.choices = ADMIN_ROLES
    #    else:
    #        person.role.choices = USER_ROLES

    return render_template('tabbed_form.html', form=form, header=lazy_gettext('New Record'),
                           site=theme(request.access_route), pubtype=pubtype, action='create',
                           record_id=form.id.data)


@app.route('/retrieve/<pubtype>/<record_id>')
def show_record(pubtype, record_id=''):
    show_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, query='id:%s' % record_id)
    show_record_solr.request()

    if len(show_record_solr.results) == 0:
        flash('The requested record %s was not found!' % record_id, category='warning')
        return redirect(url_for('dashboard'))
    else:
        is_part_of = show_record_solr.results[0].get('is_part_of')
        has_part = show_record_solr.results[0].get('has_part')
        other_version = show_record_solr.results[0].get('other_version')

        thedata = json.loads(show_record_solr.results[0].get('wtf_json'))
        locked = show_record_solr.results[0].get('locked')
        form = PUBTYPE2FORM.get(pubtype).from_json(thedata)

        return render_template('record.html', record=form, header=form.data.get('title'),
                               site=theme(request.access_route), action='retrieve', record_id=record_id,
                               del_redirect=url_for('dashboard'), pubtype=pubtype, role_map=ROLE_MAP,
                               lang_map=LANGUAGE_MAP, pubtype_map=PUBTYPE2TEXT, subtype_map=SUBTYPE2TEXT,
                               license_map=LICENSE_MAP, frequency_map=FREQUENCY_MAP, locked=locked, is_part_of=is_part_of, has_part=has_part,
                               other_version=other_version)


@app.route('/retrieve/person/<person_id>')
def show_person(person_id=''):
    show_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, query='gnd:%s' % person_id, core='person',
                            facet='false')
    show_person_solr.request()

    if len(show_person_solr.results) == 0:
        show_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                application=secrets.SOLR_APP, query='id:%s' % person_id, core='person',
                                facet='false')
        show_person_solr.request()

        if len(show_person_solr.results) == 0:
            show_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT,
                                    application=secrets.SOLR_APP, query='dwd:%s' % person_id, core='person',
                                    facet='false')
            show_person_solr.request()

            if len(show_person_solr.results) == 0:
                show_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT,
                                        application=secrets.SOLR_APP, query='same_as:%s' % person_id, core='person',
                                        facet='false')
                show_person_solr.request()

                if len(show_person_solr.results) == 0:
                    flash('The requested record %s was not found!' % person_id, category='warning')
                    return redirect(url_for('persons'))
                else:
                    thedata = json.loads(show_person_solr.results[0].get('wtf_json'))
                    form = PersonAdminForm.from_json(thedata)

                    return render_template('person.html', record=form, header=form.data.get('name'),
                                           site=theme(request.access_route), action='retrieve', record_id=person_id,
                                           pubtype='person', del_redirect=url_for('persons'),
                                           url_map=URL_TYPE_MAP, pers_status_map=PERS_STATUS_MAP)
            else:
                thedata = json.loads(show_person_solr.results[0].get('wtf_json'))
                form = PersonAdminForm.from_json(thedata)

                return render_template('person.html', record=form, header=form.data.get('name'),
                                       site=theme(request.access_route), action='retrieve', record_id=person_id,
                                       pubtype='person', del_redirect=url_for('persons'),
                                       url_map=URL_TYPE_MAP, pers_status_map=PERS_STATUS_MAP)
        else:
            thedata = json.loads(show_person_solr.results[0].get('wtf_json'))
            form = PersonAdminForm.from_json(thedata)

            return render_template('person.html', record=form, header=form.data.get('name'),
                                   site=theme(request.access_route), action='retrieve', record_id=person_id,
                                   pubtype='person', del_redirect=url_for('persons'),
                                   url_map=URL_TYPE_MAP, pers_status_map=PERS_STATUS_MAP)
    else:
        thedata = json.loads(show_person_solr.results[0].get('wtf_json'))
        form = PersonAdminForm.from_json(thedata)

        return render_template('person.html', record=form, header=form.data.get('name'),
                               site=theme(request.access_route), action='retrieve', record_id=person_id,
                               pubtype='person', del_redirect=url_for('persons'),
                               url_map=URL_TYPE_MAP, pers_status_map=PERS_STATUS_MAP)


@app.route('/retrieve/organisation/<orga_id>')
def show_orga(orga_id=''):
    show_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                          application=secrets.SOLR_APP, query='id:%s' % orga_id, core='organisation', facet='false')
    show_orga_solr.request()

    if len(show_orga_solr.results) == 0:
        show_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                              application=secrets.SOLR_APP, query='account:%s' % orga_id, core='organisation',
                              facet='false')
        show_orga_solr.request()

        if len(show_orga_solr.results) == 0:
            show_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT,
                                  application=secrets.SOLR_APP, query='same_as:%s' % orga_id, core='organisation',
                                  facet='false')
            show_orga_solr.request()

            if len(show_orga_solr.results) == 0:
                flash('The requested record %s was not found!' % orga_id, category='warning')
                return redirect(url_for('orgas'))
            else:
                thedata = json.loads(show_orga_solr.results[0].get('wtf_json'))
                form = OrgaAdminForm.from_json(thedata)

                return render_template('orga.html', record=form, header=form.data.get('pref_label'),
                                       site=theme(request.access_route), action='retrieve', record_id=orga_id,
                                       pubtype='organisation', del_redirect=url_for('orgas'))
        else:
            thedata = json.loads(show_orga_solr.results[0].get('wtf_json'))
            form = OrgaAdminForm.from_json(thedata)

            return render_template('orga.html', record=form, header=form.data.get('pref_label'),
                                   site=theme(request.access_route), action='retrieve', record_id=orga_id,
                                   pubtype='organisation', del_redirect=url_for('orgas'))
    else:
        thedata = json.loads(show_orga_solr.results[0].get('wtf_json'))
        form = OrgaAdminForm.from_json(thedata)

        return render_template('orga.html', record=form, header=form.data.get('pref_label'),
                               site=theme(request.access_route), action='retrieve', record_id=orga_id,
                               pubtype='organisation', del_redirect=url_for('orgas'))


@app.route('/retrieve/organisation/<orga_id>/links')
def show_orga_links(orga_id=''):
    linked_entities = {}
    # TODO get all orgas with parent_id=orga_id plus parent_id of orga_id
    children = []
    get_orgas_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                          application=secrets.SOLR_APP, query='parent_id:%s' % orga_id, core='organisation', facet='false')
    get_orgas_solr.request()
    if len(get_orgas_solr.results) > 0:
        for child in get_orgas_solr.results:
            children.append(child.get('id'))

    parents = []
    show_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                          application=secrets.SOLR_APP, query='id:%s' % orga_id, core='organisation', facet='false')
    show_orga_solr.request()
    thedata = json.loads(show_orga_solr.results[0].get('wtf_json'))
    form = OrgaAdminForm.from_json(thedata)
    if form.data.get('parent_id') and len(form.data.get('parent_id')) > 0:
        parents.append(form.data.get('parent_id'))

    linked_entities.setdefault('parents', parents)
    linked_entities.setdefault('children', children)

    # TODO get all persons with affiliation.organisation_id=orga_id
    persons = []
    ## TODO export der personen!!!
    get_persons_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, query='*:*', core='person', facet='false')
    get_persons_solr.request()
    if len(get_persons_solr.results) > 0:
        for person in get_persons_solr.results:
            thedata = json.loads(person.get('wtf_json'))
            logging.info(thedata)
            affiliations = thedata.get('affiliation')
            logging.info(affiliations)
            for affiliation in affiliations:
                if affiliation.get('organisation_id') == orga_id:
                    persons.append(person.get('id'))

    linked_entities.setdefault('persons', persons)

    # TODO get all publications with affiliation_context=orga_id
    publications = []
    get_publications_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                 application=secrets.SOLR_APP, query='affiliation_context:%s' % orga_id, core='hb2', 
                                 facet='false')
    get_publications_solr.request()
    if len(get_publications_solr.results) > 0:
        for record in get_publications_solr.results:
            publications.append(record.get('id'))

    linked_entities.setdefault('publications', publications)

    return jsonify(linked_entities)


@app.route('/retrieve/group/<group_id>')
def show_group(group_id=''):
    show_group_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, query='id:%s' % group_id, core='group', facet='false')
    show_group_solr.request()

    if len(show_group_solr.results) == 0:
        flash('The requested record %s was not found!' % group_id, category='warning')
        return redirect(url_for('groups'))
    else:
        thedata = json.loads(show_group_solr.results[0].get('wtf_json'))
        form = GroupAdminForm.from_json(thedata)

        return render_template('group.html', record=form, header=form.data.get('pref_label'),
                               site=theme(request.access_route), action='retrieve', record_id=group_id,
                               pubtype='group', del_redirect=url_for('groups'))


@app.route('/update/organisation/<orga_id>', methods=['GET', 'POST'])
@login_required
def edit_orga(orga_id=''):
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, core='organisation',
                            data=[{'id': orga_id, 'locked': {'set': 'true'}}])
    lock_record_solr.update()

    edit_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                          application=secrets.SOLR_APP, query='id:%s' % orga_id, core='organisation')
    edit_orga_solr.request()

    if request.method == 'POST':
        form = OrgaAdminForm()
    else:
        if len(edit_orga_solr.results) == 0:
            flash('The requested organisation %s was not found!' % orga_id, category='warning')
            return redirect(url_for('orgas'))
        else:
            thedata = json.loads(edit_orga_solr.results[0].get('wtf_json'))
            form = OrgaAdminForm.from_json(thedata)

    if form.validate_on_submit():
        if form.errors:
            flash_errors(form)
            return render_template('tabbed_form.html', form=form,
                                   header=lazy_gettext('Edit: %(title)s', title=form.data.get('title')),
                                   site=theme(request.access_route), action='update')
        redirect_id = _orga2solr(form, action='update')
        unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                  application=secrets.SOLR_APP, core='organistion',
                                  data=[{'id': orga_id, 'locked': {'set': 'false'}}])
        unlock_record_solr.update()

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return show_orga(redirect_id)
        # return redirect(url_for('orgas'))

    form.changed.data = datetime.datetime.now()

    return render_template('tabbed_form.html', form=form,
                           header=lazy_gettext('Edit: %(orga)s', orga=form.data.get('pref_label')),
                           locked=True, site=theme(request.access_route), action='update', pubtype='organisation',
                           record_id=orga_id)


@app.route('/update/group/<group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id=''):
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, core='group',
                            data=[{'id': group_id, 'locked': {'set': 'true'}}])
    lock_record_solr.update()

    edit_group_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, query='id:%s' % group_id, core='group')
    edit_group_solr.request()

    thedata = json.loads(edit_group_solr.results[0].get('wtf_json'))

    if request.method == 'POST':
        form = GroupAdminForm()
    else:
        form = GroupAdminForm.from_json(thedata)

    if form.validate_on_submit():
        if form.errors:
            flash_errors(form)
            return render_template('linear_form.html', form=form,
                                   header=lazy_gettext('Edit: %(title)s', title=form.data.get('title')),
                                   site=theme(request.access_route), action='update')
        _group2solr(form)
        unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                  application=secrets.SOLR_APP, core='group',
                                  data=[{'id': group_id, 'locked': {'set': 'false'}}])
        unlock_record_solr.update()

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return show_group(form.data.get('id').strip())
        # return redirect(url_for('groups'))

    form.changed.data = datetime.datetime.now()

    return render_template('linear_form.html', form=form,
                           header=lazy_gettext('Edit: %(group)s', group=form.data.get('pref_label')),
                           locked=True, site=theme(request.access_route), action='update', pubtype='group',
                           record_id=group_id)


@app.route('/update/person/<person_id>', methods=['GET', 'POST'])
@login_required
def edit_person(person_id=''):
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash(gettext('For Admins ONLY!!!'))
        return redirect(url_for('homepage'))
    lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, core='person',
                            data=[{'id': person_id, 'locked': {'set': 'true'}}])
    lock_record_solr.update()

    idfield = 'id'
    if GND_RE.match(person_id):
        idfield = 'gnd'
    edit_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, query='%s:%s' % (idfield, person_id), core='person',
                            facet='false')
    edit_person_solr.request()

    if request.method == 'POST':
        form = PersonAdminForm()
    else:
        if len(edit_person_solr.results) == 0:
            flash('The requested person %s was not found!' % person_id, category='warning')
            return redirect(url_for('persons'))
        else:
            thedata = json.loads(edit_person_solr.results[0].get('wtf_json'))
            form = PersonAdminForm.from_json(thedata)

    logging.info(form.data)
    if form.validate_on_submit():
        if form.errors:
            flash_errors(form)
            return render_template('tabbed_form.html', form=form,
                                   header=lazy_gettext('Edit: %(title)s', title=form.data.get('title')),
                                   site=theme(request.access_route), action='update')
        _person2solr(form, action='update')
        unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                  application=secrets.SOLR_APP, core='person',
                                  data=[{'id': person_id, 'locked': {'set': 'false'}}])
        unlock_record_solr.update()

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return show_person(form.data.get('id').strip())
        # return redirect(url_for('persons'))

    form.changed.data = datetime.datetime.now()

    return render_template('tabbed_form.html', form=form,
                           header=lazy_gettext('Edit: %(person)s', person=form.data.get('name')),
                           locked=True, site=theme(request.access_route), action='update', pubtype='person',
                           record_id=person_id)


@app.route('/update/<pubtype>/<record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id='', pubtype=''):
    cptask = request.args.get('cptask', False)
    logging.info('cptask = %s' % cptask)

    lock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, core='hb2',
                            data=[{'id': record_id, 'locked': {'set': 'true'}}])
    lock_record_solr.update()

    edit_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                            application=secrets.SOLR_APP, core='hb2', query='id:%s' % record_id)
    edit_record_solr.request()

    thedata = json.loads(edit_record_solr.results[0].get('wtf_json'))

    # TODO if admin or superadmin or (user and editorial_status=='new')

    if request.method == 'POST':
        # logging.info('POST')
        form = PUBTYPE2FORM.get(pubtype)()
        # logging.info(form.data)
    elif request.method == 'GET':
        # logging.info('GET')
        form = PUBTYPE2FORM.get(pubtype).from_json(thedata)
        # logging.info(form.data)

    if current_user.role == 'admin' or current_user.role == 'superadmin':
        form.pubtype.choices = vocabularies.ADMIN_PUBTYPES
    else:
        form.pubtype.choices = vocabularies.USER_PUBTYPES

    if thedata.get('pubtype') != pubtype:
        diff = _diff_struct(thedata, form.data)
        if len(diff) > 0:
            # flash(Markup(lazy_gettext('<p><i class="fa fa-exclamation-triangle fa-3x"></i> <h3>The following data are incompatible with this publication type</h3></p>')) + _diff_struct(thedata, form.data), 'error')
            flash(Markup(lazy_gettext(
                '<p><i class="fa fa-exclamation-triangle fa-3x"></i> <h3>The publication type for the following data has changed. Please check the data.</h3></p>')) + diff,
                  'warning')
        form.pubtype.data = pubtype

    for person in form.person:
        if current_user.role == 'admin' or current_user.role != 'superadmin':
            person.role.choices = vocabularies.ADMIN_ROLES
        else:
            person.role.choices = vocabularies.USER_ROLES

    if form.validate_on_submit():

        if form.errors:
            flash_errors(form)
            return render_template('tabbed_form.html', form=form,
                                   header=lazy_gettext('Edit: %(title)s', title=form.data.get('title')),
                                   site=theme(request.access_route), action='update', pubtype=pubtype)
        _record2solr(form, action='update')
        unlock_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                  application=secrets.SOLR_APP, core='hb2',
                                  data=[{'id': record_id, 'locked': {'set': 'false'}}])
        unlock_record_solr.update()
        # return redirect(url_for('dashboard'))

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return show_record(pubtype, form.data.get('id').strip())

    form.changed.data = datetime.datetime.now()
    form.deskman.data = current_user.email

    # if cptask: delete redis record for record_id
    if cptask:
        try:
            storage_consolidate_persons = app.extensions['redis']['REDIS_CONSOLIDATE_PERSONS']
            storage_consolidate_persons.delete(record_id)
        except Exception as e:
            logging.info('REDIS ERROR: %s' % e)
            flash('Could not delete task for %s' % record_id, 'danger')

    return render_template('tabbed_form.html', form=form, header=lazy_gettext('Edit: %(title)s',
                                                                              title=form.data.get('title')),
                           locked=True, site=theme(request.access_route), action='update',
                           pubtype=pubtype, record_id=record_id)


@app.route('/delete/<record_id>')
def delete_record(record_id=''):
    if current_user.role == 'admin':
        # load record
        edit_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                application=secrets.SOLR_APP, core='hb2', query='id:%s' % record_id)
        edit_record_solr.request()
        thedata = json.loads(edit_record_solr.results[0].get('wtf_json'))
        pubtype = thedata.get('pubtype')
        form = PUBTYPE2FORM.get(pubtype).from_json(thedata)
        # TODO if exists links of type 'other_version' (proof via Solr-Queries if not exists is_other_version_of), 'has_parts', then ERROR!
        # modify status to 'deleted'
        form.editorial_status.data = 'deleted'
        form.changed.data = str(datetime.datetime.now())
        form.deskman.data = current_user.email
        # save record
        _record2solr(form, action='update')
        # return
        flash(gettext('Set editorial status of %s to deleted!' % record_id))

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    elif current_user.role == 'superadmin':
        delete_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                  application=secrets.SOLR_APP, core='hb2', del_id=record_id)
        delete_record_solr.delete()
        flash(gettext('Record %s deleted!' % record_id))

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    else:
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))


@app.route('/delete/person/<person_id>')
def delete_person(person_id=''):
    # TODO if admin
    if current_user.role == 'admin':
        flash(gettext('Set status of %s to deleted!' % person_id))
        # load person
        edit_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                application=secrets.SOLR_APP, core='person', query='id:%s' % person_id)
        edit_person_solr.request()

        thedata = json.loads(edit_person_solr.results[0].get('wtf_json'))
        form = PersonAdminForm.from_json(thedata)
        # modify status to 'deleted'
        form.editorial_status.data = 'deleted'
        form.changed.data = str(datetime.datetime.now())
        form.deskman.data = current_user.email
        # save person
        _person2solr(form, action='delete')

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    # TODO if superadmin
    elif current_user.role == 'superadmin':
        delete_person_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                  application=secrets.SOLR_APP, core='person', del_id=person_id)
        delete_person_solr.delete()
        flash(gettext('Person %s deleted!' % person_id))

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    else:
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))


@app.route('/delete/organisation/<orga_id>')
def delete_orga(orga_id=''):
    # TODO if admin
    if current_user.role == 'admin':
        flash(gettext('Set status of %s to deleted!' % orga_id))
        # load orga
        edit_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                              application=secrets.SOLR_APP, core='organisation', query='id:%s' % orga_id)
        edit_orga_solr.request()

        thedata = json.loads(edit_orga_solr.results[0].get('wtf_json'))
        form = OrgaAdminForm.from_json(thedata)
        # modify status to 'deleted'
        form.editorial_status.data = 'deleted'
        form.changed.data = str(datetime.datetime.now())
        form.deskman.data = current_user.email
        # save orga
        _orga2solr(form, action='delete')

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    # TODO if superadmin
    elif current_user.role == 'superadmin':
        delete_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                application=secrets.SOLR_APP, core='organisation', del_id=orga_id)
        delete_orga_solr.delete()
        flash(gettext('Organisation %s deleted!' % orga_id))

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    else:
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))


@app.route('/delete/group/<group_id>')
def delete_group(group_id=''):
    # TODO if admin
    if current_user.role == 'admin':
        flash(gettext('Set status of %s to deleted!' % group_id))
        # load group
        edit_orga_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                              application=secrets.SOLR_APP, core='group', query='id:%s' % group_id)
        edit_orga_solr.request()

        thedata = json.loads(edit_orga_solr.results[0].get('wtf_json'))
        form = GroupAdminForm.from_json(thedata)
        # modify status to 'deleted'
        form.editorial_status.data = 'deleted'
        form.changed.data = str(datetime.datetime.now())
        form.deskman.data = current_user.email
        # save group
        _group2solr(form)

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    # TODO if superadmin
    elif current_user.role == 'superadmin':
        delete_group_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                 application=secrets.SOLR_APP, core='group', del_id=group_id)
        delete_group_solr.delete()
        flash(gettext('Working Group %s deleted!' % group_id))

        time.sleep(secrets.WAITING_FOR_REDIRECT)
        return jsonify({'deleted': True})
    else:
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))


@app.route('/add/file')
def add_file():
    pass


@app.route('/duplicates')
def duplicates():
    pagination = ''
    page = int(request.args.get('page', 1))
    duplicates_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, start=(page - 1) * 10, fquery=['dedupid:[* TO *]'],
                           group='true', group_field='dedupid', group_limit=100, facet='false')
    duplicates_solr.request()
    logging.info(duplicates_solr.response)
    num_found = duplicates_solr.count()
    if num_found == 0:
        flash(gettext('There are currently no Duplicates!'))
        return redirect(url_for('dashboard'))
    pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                            record_name=lazy_gettext('duplicate groups'),
                            search_msg=lazy_gettext('Showing {start} to {end} of {found} {record_name}'))
    mystart = 1 + (pagination.page - 1) * pagination.per_page
    return render_template('duplicates.html', groups=duplicates_solr.results, pagination=pagination,
                           header=lazy_gettext('Duplicates'), site=theme(request.access_route), offset=mystart - 1)


@app.route(('/consolidate/persons'))
def consolidate_persons():
    if secrets.APP_SECURITY:
        if current_user.role != 'admin' and current_user.role != 'superadmin':
            flash(gettext('For Admins ONLY!!!'))
            return redirect(url_for('homepage'))
    # Die ursprünglich hier definierte Funktion ist aus Gründen der Perfomance in ein separates Skript ausgelagert
    # worden. Diese kann nun zb. einmal täglich ausgeführt werden. Die Ergebnisse landen in einer Redis-Instanz.
    # Hier werden nun die Ergebnisse aus dieser Redis-Instanz geholt und angezeigt.

    try:
        storage_consolidate_persons = app.extensions['redis']['REDIS_CONSOLIDATE_PERSONS']

        results = []
        for key in storage_consolidate_persons.keys('*'):
            thedata = storage_consolidate_persons.get(key)
            results.append(ast.literal_eval(thedata.decode('UTF-8')))

        # logging.info(results)
        # return 'TASKS to consolidate persons: %s / %s' % (len(results), json.dumps(results[0], indent=4))
        return render_template('consolidate_persons.html', results=results, count=len(results),
                               header=lazy_gettext('Consolidate Persons'), site=theme(request.access_route))

    except Exception as e:
        logging.info('REDIS ERROR: %s' % e)
        return 'failed to read data'


########################################################################################################################


class UserNotFoundError(Exception):
    pass


class User(UserMixin):
    def __init__(self, id, role='', name='', email='', accesstoken='', gndid=''):
        self.id = id
        self.name = name
        self.role = role
        self.email = email
        self.gndid = gndid
        self.accesstoken = accesstoken
        user_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                         application=secrets.SOLR_APP, core='hb2_users', query='id:%s' % id, facet='false')
        user_solr.request()
        if user_solr.count() > 0:
            _user = user_solr.results[0]
            self.name = _user.get('name')
            self.role = _user.get('role')
            self.email = _user.get('email')
            self.gndid = _user.get('gndid')
            self.accesstoken = _user.get('accesstoken')

    def __repr__(self):
        return '<User %s: %s>' % (self.id, self.name)

    @classmethod
    def get_user(self_class, id):
        user_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                         application=secrets.SOLR_APP, core='hb2_users', query='id:%s' % id, facet='false')
        user_solr.request()

        return user_solr.results[0]

    @classmethod
    def get(self_class, id):
        try:
            return self_class(id)
        except UserNotFoundError:
            return None


class LoginForm(Form):
    username = StringField(lazy_gettext('Username'))
    password = PasswordField(lazy_gettext('Password'))
    wayf = HiddenField(lazy_gettext('Where Are You From?'))


def is_safe_url(target):
    ref_url = parse.urlparse(request.host_url)
    test_url = parse.urlparse(parse.urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


@login_manager.user_loader
def load_user(id):
    return User.get(id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(request.form.get('username'))
        # user_info = user.get_user(request.form.get('username'))
        next = get_redirect_target()
        if request.form.get('wayf') == 'bochum':
            authuser = requests.post('https://api.ub.rub.de/ldap/authenticate/',
                                     data={'nocheck': 'true',
                                           'userid': base64.b64encode(request.form.get('username').encode('ascii')),
                                           'passwd': base64.b64encode(
                                               request.form.get('password').encode('ascii'))}).json()
            # logging.info(authuser)
            if authuser.get('email'):
                user_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                 application=secrets.SOLR_APP, core='hb2_users', query='id:%s' % authuser.get('id'),
                                 facet='false')
                user_solr.request()
                if user_solr.count() == 0:
                    tmp = {}
                    accesstoken = make_secure_token(
                        base64.b64encode(request.form.get('username').encode('ascii')) + base64.b64encode(
                            request.form.get('password').encode('ascii')))
                    tmp.setdefault('id', request.form.get('username').encode('ascii'))
                    tmp.setdefault('name', '%s %s' % (authuser.get('given_name'), authuser.get('last_name')))
                    tmp.setdefault('email', authuser.get('email'))
                    if user.role == '' or user.role == 'user':
                        tmp.setdefault('role', 'user')
                    else:
                        tmp.setdefault('role', user.role)
                    tmp.setdefault('accesstoken', accesstoken)
                    user.name = '%s %s' % (authuser.get('given_name'), authuser.get('last_name'))
                    user.email = authuser.get('email')
                    user.accesstoken = accesstoken
                    new_user_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                         application=secrets.SOLR_APP, core='hb2_users', data=[tmp], facet='false')
                    new_user_solr.update()
                login_user(user)

                return redirect(next or url_for('homepage'))
            else:
                flash(gettext("Username and Password Don't Match"), 'danger')
                return redirect('login')
        elif request.form.get('wayf') == 'dortmund':
            # 010188
            authuser = requests.post('https://api.ub.tu-dortmund.de/paia/auth/login',
                                     data={
                                         'username': request.form.get('username').encode('ascii'),
                                         'password': request.form.get('password').encode('ascii'),
                                         'grant_type': 'password',
                                     },
                                     headers={'Accept': 'application/json', 'Content-type': 'application/json'}).json()
            # logging.info(authuser)
            if authuser.get('access_token'):
                user_info = requests.get('https://api.ub.tu-dortmund.de/paia/core/%s' % authuser.get('patron'),
                                         headers={
                                             'Accept': 'application/json',
                                             'Authorization': '%s %s' % (
                                             authuser.get('token_type'), authuser.get('access_token'))
                                         }).json()
                # logging.info(user_info)
                user_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                 application=secrets.SOLR_APP, core='hb2_users',
                                 query='accesstoken:%s' % authuser.get('access_token'), facet='false')
                user_solr.request()
                if user_solr.count() == 0:
                    tmp = {}
                    tmp.setdefault('id', user_info.get('username'))
                    tmp.setdefault('name', user_info.get('name'))
                    tmp.setdefault('email', user_info.get('email'))
                    # TODO for repo: get faculty information
                    # TODO https://bitbucket.org/beno/python-sword2/wiki/Home
                    if user.role == '' or user.role == 'user':
                        tmp.setdefault('role', 'user')
                    else:
                        tmp.setdefault('role', user.role)
                    tmp.setdefault('accesstoken', authuser.get('access_token'))
                    # logging.info(tmp)
                    user.name = user_info.get('name')
                    user.email = user_info.get('email')
                    user.accesstoken = authuser.get('access_token')
                    new_user_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                                         application=secrets.SOLR_APP, core='hb2_users', data=[tmp], facet='false')
                    new_user_solr.update()
                login_user(user)
                return redirect(next or url_for('homepage'))
            else:
                flash(gettext("Username and Password Don't Match"), 'danger')
                return redirect('login')

    form = LoginForm()
    next = get_redirect_target()
    # return render_template('login.html', form=form, header='Sign In', next=next, orcid_sandbox_client_id=orcid_sandbox_client_id)
    return render_template('login.html', form=form, header='Sign In', next=next, site=theme(request.access_route))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('homepage')


ORCID_RE = re.compile('\d{4}-\d{4}-\d{4}-\d{4}')


@socketio.on('lock', namespace='/hb2')
def lock_message(message):
    print('Locked ' + message.get('data'))
    emit('locked', {'data': message['data']}, broadcast=True)


@socketio.on('unlock', namespace='/hb2')
def unlock_message(message):
    print(message)
    # resp = requests.get('http://127.0.0.1:8983/solr/hb2/query?q=id:%s&fl=editorial_status&omitHeader=true' % message.get('data')).json()
    # status = resp.get('response').get('docs')[0].get('editorial_status')
    # print(status)
    print('Unlocked ' + message.get('data'))
    # emit('unlocked', {'data': {'id': message.get('data'), 'status': status}}, broadcast=True)
    emit('unlocked', {'data': message.get('data')}, broadcast=True)


@socketio.on('connect', namespace='/hb2')
def connect():
    emit('my response', {'data': 'connected'})


@app.route('/export/solr_dump/<core>')
@login_required
def export_solr_dump(core=''):
    if secrets.APP_SECURITY:
        if current_user.role != 'superadmin':
            flash(gettext('For SuperAdmins ONLY!!!'))
            return redirect(url_for('homepage'))
    '''
    Export the wtf_json field of every doc in the index to a new document in the users core and to the user's local file
    system. Uses the current user's ID and a timestamp as the document ID and file name.
    '''
    if core != 'hb2_users':
        filename = '%s_%s.json' % (core, int(time.time()))
        export_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, export_field='wtf_json', core=core)
        export_docs = export_solr.export()
        # target_solr = Solr(application=secrets.SOLR_APP, core='hb2_users', data=[{'id': filename, 'core': core, 'dump': json.dumps(export_docs)}])
        # target_solr.update()
        return send_file(BytesIO(str.encode(json.dumps(export_docs))), attachment_filename=filename, as_attachment=True,
                         cache_timeout=1, add_etags=True)
    else:
        flash('Cannot export hb2_users this way!', 'error')
        return redirect('superadmin')


@app.route('/export/not_imported_records/<core>')
@login_required
def export_not_imported_records(core=''):
    if secrets.APP_SECURITY:
        if current_user.role != 'superadmin':
            flash(gettext('For SuperAdmins ONLY!!!'))
            return redirect(url_for('homepage'))
    '''
    Export the wtf_json field of every doc in the index to a new document in the users core and to the user's local file
    system. Uses the current user's ID and a timestamp as the document ID and file name.
    '''
    if core != 'hb2_users':
        filename = '%s_%s.json' % (core, int(time.time()))
        export_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                           application=secrets.SOLR_APP, query='-editorial_status:imported', export_field='wtf_json', 
                           core=core)
        export_docs = export_solr.export()
        # target_solr = Solr(application=secrets.SOLR_APP, core='hb2_users', data=[{'id': filename, 'core': core, 'dump': json.dumps(export_docs)}])
        # target_solr.update()
        return send_file(BytesIO(str.encode(json.dumps(export_docs))), attachment_filename=filename, as_attachment=True,
                         cache_timeout=1, add_etags=True)
    else:
        flash('Cannot export hb2_users this way!', 'error')
        return redirect('superadmin')


@app.route('/export/serials')
@login_required
def export_serials():
    if secrets.APP_SECURITY:
        if current_user.role != 'superadmin':
            flash(gettext('For SuperAdmins ONLY!!!'))
            return redirect(url_for('homepage'))
    '''
    Export the wtf_json field of every doc in the index to a new document in the users core and to the user's local file
    system. Uses the current user's ID and a timestamp as the document ID and file name.
    '''
    filename = '%s_%s.json' % ('serials', int(time.time()))
    export_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                       application=secrets.SOLR_APP, query='pubtype:Series or pubtype:Jounral', export_field='wtf_json',
                       core='hb2')
    export_docs = export_solr.export()
    return send_file(BytesIO(str.encode(json.dumps(export_docs, indent=4))), attachment_filename=filename, as_attachment=True,
                     cache_timeout=1, add_etags=True)


@app.route('/import/solr_dumps')
@login_required
def import_solr_dumps():
    if secrets.APP_SECURITY:
        if current_user.role != 'superadmin':
            flash(gettext('For SuperAdmins ONLY!!!'))
            return redirect(url_for('homepage'))
    '''
    Import Solr dumps either from the users core or from the local file system.
    '''
    page = int(request.args.get('page', 1))
    solr_dumps = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                      application=secrets.SOLR_APP, core='hb2_users', query='id:*.json', facet='false',
                      start=(page - 1) * 10)
    solr_dumps.request()
    num_found = solr_dumps.count()
    pagination = Pagination(page=page, total=num_found, found=num_found, bs_version=3, search=True,
                            record_name=lazy_gettext('dumps'),
                            search_msg=lazy_gettext('Showing {start} to {end} of {found} {record_name}'))
    mystart = 1 + (pagination.page - 1) * pagination.per_page
    form = FileUploadForm()
    return render_template('solr_dumps.html', records=solr_dumps.results, offset=mystart - 1, pagination=pagination,
                           header=lazy_gettext('Import Dump'), del_redirect='import/solr_dumps', form=form)


def _import_data(doc):
    form = PUBTYPE2FORM.get(doc.get('pubtype')).from_json(doc)
    return _record2solr(form, action='create')


def _import_person_data(doc):
    form = PersonAdminForm.from_json(doc)
    return _person2solr(form, action='create')


def _import_orga_data(doc):
    form = OrgaAdminForm.from_json(doc)
    return _orga2solr(form, action='create')


def _import_group_data(doc):
    form = GroupAdminForm.from_json(doc)
    return _group2solr(form, action='create')


@app.route('/import/solr_dump/<filename>', methods=['GET', 'POST'])
@login_required
def import_solr_dump(filename=''):
    if secrets.APP_SECURITY:
        if current_user.role != 'superadmin':
            flash(gettext('For SuperAdmins ONLY!!!'))
            return redirect(url_for('homepage'))
    thedata = ''
    solr_data = []
    type = ''
    if request.method == 'GET':
        if filename:
            import_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                               application=secrets.SOLR_APP, core='hb2_users', query='id:%s' % filename, facet='false')
            import_solr.request()
            thedata = json.loads(import_solr.results[0].get('dump')[0])
            type = import_solr.results[0].get('core')
    elif request.method == 'POST':
        form = FileUploadForm()
        if form.validate_on_submit():
            if not form.type.data:
                flash('Please select a data type!', 'error')
                return redirect('superadmin')
            else:
                type = form.type.data
            if not form.file.data:
                flash('Please select a data file!', 'error')
                return redirect('superadmin')
            else:
                thedata = json.loads(form.file.data.stream.read())

    # pool = Pool(4)
    # solr_data.append(pool.map(_import_data, thedata))
    target = 'dashboard'
    if type == 'publication':
        for mydata in thedata:
            _import_data(mydata)
    elif type == 'person':
        for mydata in thedata:
            _import_person_data(mydata)
        target = 'persons'
    elif type == 'organisation':
        for mydata in thedata:
            _import_orga_data(mydata)
        target = 'organisations'
    elif type == 'group':
        for mydata in thedata:
            _import_group_data(mydata)
        target = 'groups'

    flash('%s records imported!' % len(thedata), 'success')
    return redirect(target)


def _update_data(doc):
    form = PUBTYPE2FORM.get(doc.get('pubtype')).from_json(doc)
    return _record2solr(form, action='update')


def _update_person_data(doc):
    form = PersonAdminForm.from_json(doc)
    return _person2solr(form, action='update')


def _update_orga_data(doc):
    form = OrgaAdminForm.from_json(doc)
    return _orga2solr(form, action='update')


def _update_group_data(doc):
    form = GroupAdminForm.from_json(doc)
    return _group2solr(form, action='update')


@app.route('/update/solr_dump/<filename>', methods=['GET', 'POST'])
@login_required
def update_solr_dump(filename=''):
    if secrets.APP_SECURITY:
        if current_user.role != 'superadmin':
            flash(gettext('For SuperAdmins ONLY!!!'))
            return redirect(url_for('homepage'))
    thedata = ''
    type = ''
    if request.method == 'GET':
        if filename:
            update_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                               application=secrets.SOLR_APP, core='hb2_users', query='id:%s' % filename, facet='false')
            update_solr.request()
            thedata = json.loads(update_solr.results[0].get('dump')[0])
            type = update_solr.results[0].get('core')
    elif request.method == 'POST':
        form = FileUploadForm()
        if form.validate_on_submit():
            if not form.type.data:
                flash('Please select a data type!', 'error')
                return redirect('superadmin')
            else:
                type = form.type.data
            if not form.file.data:
                flash('Please select a data file!', 'error')
                return redirect('superadmin')
            else:
                thedata = json.loads(form.file.data.stream.read())

    # pool = Pool(4)
    # solr_data.append(pool.map(_import_data, thedata))
    target = 'dashboard'
    if type == 'publication':
        for mydata in thedata:
            _update_data(mydata)
    elif type == 'person':
        for mydata in thedata:
            _update_person_data(mydata)
        target = 'persons'
    elif type == 'organisation':
        for mydata in thedata:
            _update_orga_data(mydata)
        target = 'organisations'
    elif type == 'group':
        for mydata in thedata:
            _update_group_data(mydata)
        target = 'groups'

    flash('%s records imported!' % len(thedata), 'success')
    return redirect(target)


@app.route('/delete/solr_dump/<record_id>')
@login_required
def delete_dump(record_id=''):
    if current_user.role != 'superadmin':
        flash(gettext('For SuperAdmins ONLY!!!'))
        return redirect(url_for('homepage'))
    delete_record_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                              application=secrets.SOLR_APP, core='hb2_users', del_id=record_id)
    delete_record_solr.delete()

    return jsonify({'deleted': True})


@app.route('/retrieve/related_items/<relation>/<record_ids>')
def show_related_item(relation='', record_ids=''):
    query = '{!terms f=id}%s' % record_ids
    if ',' not in record_ids:
        query = 'id:%s' % record_ids
    relation_solr = Solr(host=secrets.SOLR_HOST, port=secrets.SOLR_PORT, 
                         application=secrets.SOLR_APP, query=query, facet='false')
    relation_solr.request()

    return jsonify({'relation': relation, 'docs': relation_solr.results})


@app.route('/contact')
def contact():
    site = theme(request.access_route)
    if site == 'bochum':
        return redirect('mailto:bibliographie-ub.rub.de')
    elif site == 'dortmund':
        return redirect('http://www.ub.tu-dortmund.de/mail.html')
    else:
        return redirect('mailto:bibliographie-ub.rub.de')


# if __name__ == '__main__':
#     app.run()

if __name__ == '__main__':
    socketio.run(app, port=secrets.APP_PORT)
