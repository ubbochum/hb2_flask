#!/usr/bin/env python
# encoding: utf-8

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

from lxml import etree
import logging
import pprint
import simplejson as json

try:
    import site_secrets as secrets
except ImportError:
    import secrets

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-4s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
)

MODS_NAMESPACE = 'http://www.loc.gov/mods/v3'
OAI_DC_NAMESPACE = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
DC_NAMESPACE = 'http://purl.org/dc/elements/1.1/'
DCTERMS_NAMESPACE = 'http://purl.org/dc/terms'
XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'
MODS = '{%s}' % MODS_NAMESPACE
OAI_DC = '{%s}' % OAI_DC_NAMESPACE
DC = '{%s}' % DC_NAMESPACE
DCTERMS = '{%s}' % DCTERMS_NAMESPACE
XLINK = '{%s}' % XLINK_NAMESPACE
#<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd"><dc:type>info:eu-repo/semantics/article</dc:type>

NSMAP = {'m': MODS_NAMESPACE,
    'dcterms': DCTERMS_NAMESPACE,
    'xlink': XLINK_NAMESPACE
}

OAI_MAP = {
    'oai_dc': OAI_DC_NAMESPACE,
    'dc': DC_NAMESPACE
}

FREQUENCY_MAP = {
    'Completely Irregular': 'completely_irregular',
    'Annual': 'annual',
    'Quarterly': 'quarterly',
    'Semiannual': 'semiannual',
    'Monthly': 'monthly',
    'Bimonthly': 'bimonthly',
    'Three Times a Year': 'three_times_a_year',
    'Semimonthly': 'semimonthly',
    'Biannial': 'biennial',
    '15 issues a year': 'fifteen_issues_a_year',
    'Continuously Updated': 'continuously_updated',
    'Daily': 'daily',
    'Semiweekly': 'semiweekly',
    'Three Times a Week': 'three_times_a_week',
    'Weekly': 'weekly',
    'Biweekly': 'biweekly',
    'Three Times a Month': 'three_times_a_month',
    'Triennial': 'triennial',
}

SUBJECT_MAPS = {}
with open('mesh_map.json') as mesh_map:
    SUBJECT_MAPS.setdefault('mesh', json.load(mesh_map))

with open('mesh_map.json') as stw_map:
    SUBJECT_MAPS.setdefault('stw', json.load(stw_map))

mc = etree.iterparse(secrets.MODS_TEST_FILE, tag='%smods' % MODS)

def oai_elements(name, values):
    if values:
        tmp = []
        for value in values:
            elm = etree.Element('%s%s' % (DC, name), nsmap=OAI_MAP)
            elm.text = value.text
            tmp.append(elm)
        return tmp

def oai_valueURI(name, values):
    if values:
        tmp = []
        for value in values:
            elm = etree.Element('%s%s' % (DC, name), nsmap=OAI_MAP)
            elm.text = value.get('valueURI')
            tmp.append(elm)
        return tmp

def get_names(twig):
    names = []
    for name in twig:
        realname = ''
        family = ''
        first = ''
        nametype = ''
        namerole = ''
        nametype = name.attrib['type']
        pnd = ''

        try:
            pnd = name.attrib.get('valueURI').replace('http://d-nb.info/gnd/', '')
        except AttributeError:
            #logging.debug(twig.attrib.get('valueURI'))
            pass
        for part in name:
            if part.tag == '%snamePart' % MODS:
                if nametype == 'corporate':
                    realname = part.text
                if part.get('type') == 'family':
                    family = part.text
                if part.get('type') == 'given':
                    first = part.text

                if first != '':
                    realname = '%s, %s' % (family, first)
                else:
                    realname = family
                if nametype == 'corporate':
                    realname = part.text
            if part.tag == '%srole' % MODS:
                for role in part:
                    if role.tag == '%sroleTerm' % MODS:
                        namerole = role.text
        #logging.info([family, first, realname, nametype, namerole, pnd])
        names.append({'family': family, 'first': first, 'realname': realname, 'namerole': namerole, 'pnd': pnd, 'nametype': nametype})
    return names

def get_wtf_names(elems):
    wtf_pnames = []
    wtf_cnames = []
    for name in get_names(elems):
        if name.get('nametype') == 'personal':
            wtf_pnames.append({'name': name.get('realname'), 'gnd': name.get('pnd'), 'orcid': '', 'role': name.get('namerole'), 'corresponding_author': False})
        else:
            wtf_cnames.append(
                {'name': name.get('realname'), 'gnd': name.get('pnd'), 'role': name.get('namerole'), 'isni': ''})

    return {'person': wtf_pnames}, {'corporation': wtf_cnames}

def get_csl_names(elems):
    csl_names = []
    for name in get_names(elems):
        csl_names.append({'given': name.get('first'), 'family': name.get('family')})

    return {'author': csl_names}

def get_wtf_tocs(elems):
    wtf_tocs = []
    for toc in elems:
        tmp = {}
        tmp.setdefault('toc', toc.text)
        tmp.setdefault('uri', toc.get('%shref' % XLINK))
        wtf_tocs.append(tmp)

    return {'table_of_contents': wtf_tocs}

def get_wtf_subject(elems):
    wtf_subject = []
    authority = elems[0].get('authority')
    for subject in elems:
        tmp = {}
        tmp.setdefault('id', subject[0].text)
        tmp.setdefault('label', SUBJECT_MAPS.get(authority).get(subject[0].text))
        wtf_subject.append(tmp)

    return {'%s_subject' % authority: wtf_subject}

def get_wtf_abstract(elems):
    wtf_abstracts = []
    for abstract in elems:
        tmp = {}
        tmp.setdefault('content', abstract.text)
        tmp.setdefault('address', abstract.get('%shref' % XLINK))
        tmp.setdefault('label', '')
        tmp.setdefault('language', abstract.get('lang'))
        if abstract.get('shareable') == 'no':
            tmp.setdefault('shareable', False)
        else:
            tmp.setdefault('shareable', True)

        wtf_abstracts.append(tmp)

    return {'abstract': wtf_abstracts}

def doi2index(elems):
    doi = elems[0]
    solr_doi = {}

    solr_doi.setdefault('doi', doi)

    # TODO: Handle all cases in which the DOI is the source for enrichment

    return solr_doi

try:
    CONVERTER_MAP = {
        "./m:abstract": {
            'wtf': get_wtf_abstract,
            'csl': lambda elems: {'abstract': elems[0].text},
            'solr': lambda elems: {'ro_abstract': elems[0].text},
            'oai_dc': (oai_elements, 'abstract')
        },
        # "./m:accessCondition[@type='restriction on access']": lambda elem : {'': elem.text},
        # "./m:accessCondition[@type='use and reproduction']": lambda elem : {'': elem.text},
        "./m:classification[@authority='international patent classification']": {
            'wtf': lambda elems : {'bibliographic_ipc': elems[0].text} ,
            'solr': lambda elems: {'number': elems[0].text},
        },
        # "./m:extension": lambda elem : {'': elem.text},
        # "./m:extension/dcterms:bibliographicCitation": lambda elem : {'': elem.text},
        "./m:frequency[@authority='marcfrequency']": {'wtf': lambda elems: {'frequency': FREQUENCY_MAP.get(elems[0].text)}},
        # "./m:genre": lambda elem : {'': elem.text},
        "./m:genre[@authority='dct' and @valueURI='http://purl.org/dc/dcmitype/Collection']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@authority='dct' and @valueURI='http://purl.org/dc/dcmitype/Image']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@authority='dct' and @valueURI='http://purl.org/dc/dcmitype/Software']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@authority='dct' and @valueURI='http://purl.org/dc/dcmitype/Sound']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@authority='dct' and @valueURI='http://purl.org/dc/dcmitype/Text']": {'oai_dc': (oai_valueURI, 'type')},
        # "./m:genre[@authority='local']": lambda elem : {'': elem.text},
        # "./m:genre[@authority='marcgt']": lambda elem : {'': elem.text},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/article']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/bachelorThesis']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/book']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/bookPart']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/conferencePoster']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/conferenceProceedings']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/doctoralThesis']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/lecture']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/masterThesis']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/other']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/patent']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/report']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/review']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:genre[@valueURI='http://purl.org/info:eu-repo/semantics/studentThesis']": {'oai_dc': (oai_valueURI, 'type')},
        "./m:identifier[@displayLabel='Anmeldenummer']": {
            'wtf': lambda elems: {'application_number': [elem.text for elem in elems]},
            'solr': lambda elems: {'number': [elem.text for elem in elems]},
        },
        "./m:identifier[@displayLabel='Veröffentlichungs-Nr.']": {
            'wtf': lambda elems: {'patent_number': elems[0].text},
            'solr': lambda elems: {'number': elems[0].text},
        },
        "./m:identifier[@type='doi']": {
            'wtf': lambda elems: {'DOI': elems[0].text},
            'csl': lambda elems: {'DOI': elems[0].text},
            'solr': doi2index,
            'oai_dc': (oai_elements, 'identifier')
        },
        "./m:identifier[@type='isbn']": {
            'wtf': lambda elems: {'ISBN': [elem.text for elem in elems]},
            'csl': lambda elems: {'isbn': [elem.text for elem in elems]},
            'solr': lambda elems: {'isbn': [elem.text for elem in elems], 'isxn': [elem.text for elem in elems]},
            'oai_dc': (oai_elements, 'identifier')
        },
        # "./m:identifier[@type='isi']": lambda elem : {'': elem.text},
        "./m:identifier[@type='issn']": {
            'wtf': lambda elems: {'ISSN': [elem.text for elem in elems]},
            'csl': lambda elems: {'issn': [elem.text for elem in elems]},
            'solr': lambda elems: {'issn': [elem.text for elem in elems],'isxn': [elem.text for elem in elems]},
            'oai_dc': (oai_elements, 'identifier')
        },
        "./m:identifier[@type='local' and @displayLabel='HT-ID']": {
            'wtf': lambda elems: {'hbz_id': elems[0].text},
            'solr': lambda elems: {'hbz_id': elems[0].text},
        },
        "./m:identifier[@type='pm']": {
            'wtf': lambda elems: {'PMID': elems[0].text},
            'solr': lambda elems: {'pmid': elems[0].text},
        },
        "./m:identifier[@type='standard number']": {
            'wtf': lambda elems: {'number': elems[0].text},
            'solr': lambda elems: {'number': elems[0].text},
        },
        "./m:identifier[@type='urn']": {
            'wtf': lambda elems: {'urn': elems[0].text},
            'solr': lambda elems: {'urn': elems[0].text},
            'oai_dc': (oai_elements, 'identifier')
        },
        "./m:identifier[@type='zdb']": {
            'wtf': lambda elems: {'ZDBID': elems[0].text},
            'solr': lambda elems: {'zdbid': elems[0].text},
        },
        "./m:language/m:languageTerm[@type='code' and @authority='iso639-2b']": {
            'wtf': lambda elems : {'language': [elem.text for elem in elems]},
            'csl': lambda elems : {'language': [elem.text for elem in elems]},
            'solr': lambda elems : {'language': [elem.text for elem in elems]},
            'oai_dc': (oai_elements, 'language')
        },
        # "./m:location": lambda elem : {'': elem.text},
        # "./m:location/physicalLocation": lambda elem : {'': elem.text},
        # "./m:location/shelfLocator": lambda elem : {'': elem.text},
        "./m:location/url": {
            'wtf': lambda elems: {'uri': elems[0].text},
            'csl': lambda elems: {'url': elems[0].text},
            #'solr': lambda elems: {'publisher': elems[0].text},
            'oai_dc': (oai_elements, 'identifier')
        },
        # "./m:location/url[@displayLabel='Adresse im Internet']": lambda elem : {'': elem.text},
        # "./m:location/url[@displayLabel='Beigabe im Internet' and @dateLastAccessed]/@dateLastAccessed": lambda elem : {'': elem.text},
        # "./m:location/url[@displayLabel='Online-Adresse' and @dateLastAccessed]/@dateLastAccessed": lambda elem : {'': elem.text},
        # "./m:location/url[@displayLabel='URL im E-Periodical' and @dateLastAccessed]/@dateLastAccessed": lambda elem : {'': elem.text},
        "./m:name": {
            'wtf': get_wtf_names,
            'csl': get_csl_names,
        },
        # "./m:note": lambda elem : {'': elem.text},
        # u"./m:note[@displayLabel='Ansprüche']": lambda elem : {'': elem.text},
        # "./m:note[@displayLabel='Art der Schrift']": lambda elem : {'': elem.text},
        # "./m:note[@displayLabel='Notiz']": lambda elem : {'': elem.text},
        # "./m:note[@displayLabel='Preis']": lambda elem : {'': elem.text},
        # u"./m:note[@displayLabel='Prioritätsdaten']": lambda elem : {'': elem.text},
        # "./m:note[@displayLabel='Tagungsort']": lambda elem : {'': elem.text},
        # u"./m:note[@displayLabel='Titelzusätze']": lambda elem : {'': elem.text},
        # "./m:note[@displayLabel='Veranstaltungsdatum']": lambda elem : {'': elem.text},
        # "./m:note[@type='publication status']": lambda elem : {'': elem.text},
        # "./m:originInfo/dateIssued[@encoding='iso8601']": lambda elem : {'': elem.text},
        # "./m:originInfo/dateIssued[@point='start' and @encoding='iso8601']": lambda elem : {'': elem.text},
        # "./m:originInfo/dateOther[@encoding='iso8601']": lambda elem : {'': elem.text},
        # "./m:originInfo/edition": lambda elem : {'': elem.text},
        "./m:originInfo/m:place/m:placeTerm[@type='text']": {
            'wtf': lambda elems: {'publisher_place': elems[0].text},
            'csl': lambda elems: {'publisher_place': elems[0].text},
            'solr': lambda elems: {'place': elems[0].text},
            #'oai_dc': (oai_elements, 'publisher_place')
        },
        "./m:originInfo/m:publisher": {
            'wtf': lambda elems: {'publisher': elems[0].text},
            'csl': lambda elems: {'publisher': elems[0].text},
            'solr': lambda elems: {'publisher': elems[0].text},
            'oai_dc': (oai_elements, 'publisher')
        },

        # "./m:originInfo[@displayLabel='embargoEnd']": lambda elem : {'': elem.text},
        "./m:physicalDescription/extent": {
            'wtf': lambda elems: {'number_of_pages': elems[0].text},
            'csl': lambda elems: {'number-of-pages': elems[0].text},
        },
        # "./m:physicalDescription/form": lambda elem : {'': elem.text},
        "./m:physicalDescription/internetMediaType": {
            'wtf': lambda elems: {'mime_type': elems[0].text},
        },
        "./m:physicalDescription/note": {
            'wtf': lambda elems: {'note': elems[0].text},
            'solr': lambda elems: {'note': elems[0].text},
        },
        "./m:recordInfo/m:recordChangeDate[@encoding='iso8601']": {
            'wtf': lambda elems: {'changed': elems[0].text},
            'solr': lambda elems: {'changed': '%sT00:00:00Z' % elems[0].text},
        },
        "./m:recordInfo/m:recordCreationDate[@encoding='iso8601']": {
            'wtf': lambda elems: {'created': elems[0].text},
            'solr': lambda elems: {'created': '%sT00:00:00Z' % elems[0].text},
        },
        "./m:recordInfo/m:recordIdentifier": {
            'wtf': lambda elems: {'id': elems[0].text},
            'csl': lambda elems: {'id': elems[0].text},
            'solr': lambda elems: {'id': elems[0].text},
            'oai_dc': (oai_elements, 'identifier')
        },
        # "./m:relatedItem": lambda elem : {'': elem.text},
        # "./m:relatedItem/genre[@authority='local']": lambda elem : {'': elem.text},
        # "./m:relatedItem/identifier[@type='isbn']": lambda elem : {'': elem.text},
        # "./m:relatedItem/identifier[@type='issn']": lambda elem : {'': elem.text},
        # "./m:relatedItem/identifier[@type='local' and @displayLabel='HT-ID']": lambda elem : {'': elem.text},
        # "./m:relatedItem/identifier[@type='zdb']": lambda elem : {'': elem.text},
        # "./m:relatedItem/identifier[@valueURI]/@valueURI": lambda elem : {'': elem.text},
        # "./m:relatedItem/name/namePart[@type='family']": lambda elem : {'': elem.text},
        # "./m:relatedItem/name/namePart[@type='given']": lambda elem : {'': elem.text},
        # "./m:relatedItem/name/role": lambda elem : {'': elem.text},
        # "./m:relatedItem/name/role/roleTerm[@type='code' and @authorityURI='http://www.loc.gov/marc/relators/']": lambda elem : {'': elem.text},
        # "./m:relatedItem/name[@type='personal' and starts-with(@valueURI, 'http://d-nb.info/gnd/') and @authority='gnd']/@valueURI": lambda elem : {'': elem.text},
        # "./m:relatedItem/name[@type='personal']": lambda elem : {'': elem.text},
        # u"./m:relatedItem/note[@displayLabel='Nachträge']": lambda elem : {'': elem.text},
        # u"./m:relatedItem/note[@displayLabel='Titelzusätze']": lambda elem : {'': elem.text},
        # "./m:relatedItem/originInfo": lambda elem : {'': elem.text},
        # "./m:relatedItem/originInfo/dateIssued[@encoding='iso8601']": lambda elem : {'': elem.text},
        # "./m:relatedItem/originInfo/edition": lambda elem : {'': elem.text},
        # "./m:relatedItem/originInfo/place": lambda elem : {'': elem.text},
        # "./m:relatedItem/originInfo/place/placeTerm[@type='text']": lambda elem : {'': elem.text},
        # "./m:relatedItem/originInfo/publisher": lambda elem : {'': elem.text},
        # "./m:relatedItem/part": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/date[@encoding='iso8601']": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/detail/number": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/detail[@type='delivery complement']": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/detail[@type='issue']": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/detail[@type='number']": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/detail[@type='volume']": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/extent/list": lambda elem : {'': elem.text},
        # "./m:relatedItem/part/extent[@unit='pages']": lambda elem : {'': elem.text},
        # "./m:relatedItem/physicalDescription": lambda elem : {'': elem.text},
        # u"./m:relatedItem/physicalDescription/note[@displayLabel='Anzahl Bände']": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/identifier[@type='issn']": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/part": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/part/detail/number": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/part/detail[@type='issue']": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/part/detail[@type='volume']": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/part/extent/list": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/part/extent[@unit='pages']": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/titleInfo": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem/titleInfo/title": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem[@type='host']": lambda elem : {'': elem.text},
        # "./m:relatedItem/relatedItem[@type='series']": lambda elem : {'': elem.text},
        # "./m:relatedItem/titleInfo/subTitle": lambda elem : {'': elem.text},
        # "./m:relatedItem/titleInfo/title": lambda elem : {'': elem.text},
        # "./m:relatedItem/titleInfo[@type='abbreviated']": lambda elem : {'': elem.text},
        # "./m:relatedItem/titleInfo[@type='translated']": lambda elem : {'': elem.text},
        # "./m:relatedItem[@type='host']": lambda elem : {'': elem.text},
        # "./m:relatedItem[@type='isReferencedBy']": lambda elem : {'': elem.text},
        # "./m:relatedItem[@type='otherVersion']": lambda elem : {'': elem.text},
        # "./m:relatedItem[@type='preceding']": lambda elem : {'': elem.text},
        # "./m:relatedItem[@type='references']": lambda elem : {'': elem.text},
        # "./m:relatedItem[@type='series']": lambda elem : {'': elem.text},
        "./m:subject[not(@authority)]/m:topic":  {
            'wtf': lambda elems: {'keyword': [elem.text for elem in elems]},
            'solr': lambda elems: {'subject': [elem.text for elem in elems]},
            'oai_dc': (oai_elements, 'subject')
        },
        "./m:subject[@authority='mesh']": {
            'wtf': get_wtf_subject,
            'solr': lambda elems: {'mesh_terms': [SUBJECT_MAPS.get('mesh').get(elem.text) for elem in elems]},
            'oai_dc': (oai_elements, 'subject')
        },
        "./m:subject[@authority='stw']": {
            'wtf': get_wtf_subject,
            'solr': lambda elems: {'stwterm_de': [SUBJECT_MAPS.get('stw').get(elem.text) for elem in elems]},
            'oai_dc': (oai_elements, 'subject')
        },
        # "./m:subject[@authority='thesoz']": lambda elem : {'': elem.text},
        "./m:tableOfContents": {
            'wtf': get_wtf_tocs,
            'solr': lambda elems: {'toc_text': [elem.text for elem in elems]},
        },
        # "./m:tableOfContents[@xlink:href]/@xlink:href": lambda elem : {'table_of_contents': elem},
        "./m:titleInfo[not(@type)]/m:title": {
            'wtf': lambda elems: {'title': elems[0].text},
            'csl': lambda elems: {'title': elems[0].text} if not record.xpath("./m:titleInfo/m:subTitle", namespaces=NSMAP) else
                                {'title': '%s : %s' % (elems[0].text, record.xpath("./m:titleInfo/m:subTitle", namespaces=NSMAP)[0].text)},
            'solr': lambda elems: {'title': elems[0].text, 'exacttitle': elems[0].text, 'sorttitle': elems[0].text},
            'oai_dc': (oai_elements, 'title') # TODO: Elegant solution for dealing with subtitles...
        },
        "./m:titleInfo/m:subTitle": {
            'wtf': lambda elems: {'subtitle': elems[0].text},
            'solr': lambda elems: {'subtitle': elems[0].text},
        },
        # "./m:titleInfo[@displayLabel='Paragraph(en)']": lambda elem : {'': elem.text},
        "./m:titleInfo[@type='translated']/m:title": {
            'wtf': lambda elems: {'title_translated': elems[0].text},
            'solr': lambda elems: {'title_translated': elems[0].text},
        },
        # "./m:titleInfo[@type='uniform']": lambda elem : {'': elem.text},
        # "./m:typeOfResource": lambda elem : {'': elem.text},
    }
except IndexError:
    pass

for event, record in mc:
    wtf = {}
    csl = {}
    solr = {}
    oai_dc = etree.Element('%smetadata' % OAI_DC, nsmap=OAI_MAP)
    #print '%s => %s' % (event, etree.tostring(record))
    for xpath_expr in CONVERTER_MAP:
        elems = record.xpath(xpath_expr, namespaces=NSMAP)
        # if len(elems) == 1:
        #     logging.info(etree.tostring(elems[0]))
        #     try:
        #         wtf.update(CONVERTER_MAP.get(xpath_expr).get('wtf')(elems[0]))
        #         logging.info('PAAP => %s' % (elems[0].text))
        #     except AttributeError:
        #         logging.info('PEEP => %s' % xpath_expr)
        #         logging.info(record.xpath("./m:recordInfo/m:recordIdentifier", namespaces=NSMAP)[0].text)
        #         raise
        #     except TypeError:
        #         logging.info('POOP => %s' % xpath_expr)
        #         #logging.info(record.xpath("./m:recordInfo/m:recordIdentifier", namespaces=NSMAP)[0].text)
        #         pass
        #     try:
        #         if any(CONVERTER_MAP.get(xpath_expr).get('csl')(elems[0]).values()):
        #             csl.update(CONVERTER_MAP.get(xpath_expr).get('csl')(elems[0]))
        #     except TypeError:
        #         #logging.info(xpath_expr)
        #         #logging.info(record.xpath("./m:recordInfo/m:recordIdentifier", namespaces=NSMAP)[0].text)
        #         #raise
        #         pass
        #     try:
        #         if any(CONVERTER_MAP.get(xpath_expr).get('solr')(elems[0]).values()):
        #             solr.update(CONVERTER_MAP.get(xpath_expr).get('solr')(elems[0]))
        #     except TypeError:
        #         pass
        # elif len(elems) > 1:
        try:
            data = CONVERTER_MAP.get(xpath_expr).get('wtf')(elems)
            if list(data.values())[0]:
                wtf.update(data)
        except TypeError:
            pass
        except IndexError:
            pass
        except AttributeError:
            if type(data) == tuple:
                for d in data:
                    wtf.update(d)
            else:
                logging.info(xpath_expr)
                logging.info(record.xpath("./m:recordInfo/m:recordIdentifier", namespaces=NSMAP)[0].text)
                for elem in elems:
                    logging.info(etree.tostring(elem))
                raise
        try:
            data = CONVERTER_MAP.get(xpath_expr).get('csl')(elems)
            if len(list(data.values())) > 0:
                csl.update(data)
        except TypeError:
            pass
        except IndexError:
            pass
        try:
            data = CONVERTER_MAP.get(xpath_expr).get('solr')(elems)
            if len(list(data.values())) > 0:
                solr.update(data)
        except TypeError:
            pass
        except IndexError:
            pass

        try:
            oai_dc.extend(CONVERTER_MAP.get(xpath_expr).get('oai_dc')[0](CONVERTER_MAP.get(xpath_expr).get('oai_dc')[1],
                                                                         elems))
        except TypeError:
            pass
        except AttributeError:
            logging.info(xpath_expr)
            logging.info(record.xpath("./m:recordInfo/m:recordIdentifier", namespaces=NSMAP)[0].text)
            raise

    #logging.info('WTF %s' % wtf)
    pprint.pprint(wtf)
    #logging.info('OAI_DC %s' % etree.tostring(oai_dc))
    #logging.info('CSL %s' % csl)
    #logging.info('SOLR %s' % solr)
    pprint.pprint(solr)
    #logging.info('####################################################################################################')