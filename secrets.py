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

key = ''

contact_mail = ''

BOOTSTRAP_SERVE_LOCAL = False

# To make the app run on a different path than root, set this to True and change your web server configuration accordingly.
# For nginx see e.g. https://gist.github.com/ubbochum/7b50facf1923fff61bc4
DIFFERENT_PROXY_PATH = False

orcid_sandbox_client_id = ''
orcid_sandbox_client_secret = ''

MODS_TEST_FILE = ''

SOLR_HOST = '127.0.0.1'
SOLR_PORT = '8983'
SOLR_CORE = 'hb2'
SOLR_EXPORT_FIELD = 'wtf_json'
SOLR_ROWS = '20'
SOLR_FACETS = {
    'pubtype':
        {
            'type': 'terms',
            'field': 'pubtype'
        },
    # 'subtype':
    #     {
    #         'type': 'terms',
    #         'field': 'subtype'
    #     },
    'language':
        {
            'type': 'terms',
            'field': 'language'
        },
    'fperson':
        {
            'type': 'terms',
            'field': 'fperson'
        },
    'fdate':
        {
            'type': 'terms',
            'field': 'fdate',
            'sort': 'index desc'
        },
}

TRAC_URL = ''
TRAC_USER = ''
TRAC_PW = ''

REDMINE_URL = ''
REDMINE_USER = ''
REDMINE_KEY = ''
REDMINE_PROJECT = ''