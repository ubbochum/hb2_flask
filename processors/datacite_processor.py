__author__ = 'hagbeck'

# The MIT License
#
#  Copyright 2016 UB Dortmund <daten.ub@tu-dortmund.de>.
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

import datetime
import uuid
import logging
import simplejson as json
from simplejson import JSONDecodeError
import requests

try:
    import site_secrets as secrets
except ImportError:
    import secrets

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-4s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )

# https://api.datacite.org/

# TODO see https://schema.datacite.org/meta/kernel-3.1/doc/DataCite-MetadataKernel_v3.1.pdf
DATACITE_PUBTYPES = {
    'book': 'Monograph',
    'book-chapter': 'Chapter',
    'book-edited': 'Collection',
    'book-section': 'Chapter',
    'book-series': 'Series',
    'book-set': 'Monograph',
    'book-track': 'Chapter',
    'component': 'Report',
    'data-set': 'ResearchData',
    'dissertation': 'Thesis',
    'journal-article': 'ArticleJournal',
    'journal': 'Journal',
    'journal-issue': 'Collection',
    'journal-volume': 'Collection',
    'monograph': 'Monograph',
    'other': 'Report',
    'preprint': 'Report',
    'proceedings': 'Conference',
    'proceedings-article': 'Chapter',
    'reference': 'Collection',
    'reference-entry': 'Chapter',
    'report': 'Report',
    'report-series': 'Series',
    'standard': 'Standard',
    'standard-series': 'Series',
}


def datacite2csl(doi='', query=''):

    rows = 10

    csl_json = []

    record = {}
    try:
        if doi != '':
            record = requests.get('https://api.datacite.org/works/%s' % doi).json()
        elif query != '':
            record = requests.get('https://api.datacite.org/works?rows=%s&query=%s' % (rows, query)).json()
        else:
            record.setdefault('data', [])
    except JSONDecodeError:
        pass

    if doi != '':
        if record.get('data'):
            datacite_items = record.get('data')
        else:
            datacite_items = []
    elif query != '':
        datacite_items = record.get('data')
    else:
        datacite_items = []

    for item in datacite_items:

        if item.get('type') == 'works':
            csl_record = {}

            doi_from_data = item.get('attributes').get('doi')
            csl_record.setdefault('doi', doi_from_data)
            csl_record.setdefault('id', doi_from_data)

            csl_type = item.get('attributes').get('resource-type')
            csl_record.setdefault('type', csl_type)

            title = item.get('attributes').get('title')
            csl_record.setdefault('title', title)

            issued = item.get('attributes').get('published')
            csl_issued = {'raw': issued}
            csl_record.setdefault('issued', csl_issued)

            journal_title = None
            for jtitle in item.get('attributes').get('container-title'):
                if jtitle != '':
                    journal_title = jtitle
                    break

            if journal_title is not None:
                csl_record.setdefault('parent_title', journal_title)

            authors = []
            if item.get('attributes').get('author'):
                for author in item.get('attributes').get('author'):
                    if author.get('literal'):
                        tmp = author.get('literal').split(' ')
                        authors.append({'family': tmp[len(tmp)-1], 'given': author.get('literal').replace(' %s' % tmp[len(tmp)-1], '')})
                        # authors.append({'literal': author.get('literal')})
                    elif author.get('family') or author.get('given'):
                        authors.append({'family': author.get('family'), 'given': author.get('given')})

            if item.get('attributes').get('editor'):
                for editor in item.get('attributes').get('editor'):
                    authors.append({'family': editor.get('family'), 'given': editor.get('given')})

            if len(authors) > 0:
                csl_record.setdefault('author', authors)

            publisher_id = item.get('attributes').get('publisher-id')

            for item1 in datacite_items:

                if item1.get('type') == 'publishers' and item1.get('id') == publisher_id:
                    csl_record.setdefault('publisher', item1.get('attributes').get('title'))

            csl_json.append(csl_record)

    return {'items': csl_json}


def datacite2wtfjson(doi=''):

    wtf = {}

    record = requests.get('https://api.datacite.org/works/%s' % doi).json()

    wtf.setdefault('id', str(uuid.uuid4()))
    timestamp = str(datetime.datetime.now())
    wtf.setdefault('created', timestamp)
    wtf.setdefault('changed', timestamp)
    wtf.setdefault('editorial_status', 'new')


# logging.debug(json.dumps(datacite2csl('10.4230/DAGREP.1.10.37', ''), indent=4))

