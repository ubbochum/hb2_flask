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
import uuid

def convert(record, owner):
    csl = {}
    metadata = {}
    MODS = 'http://www.loc.gov/mods/v3'
    MODS_NS = '{%s}' % MODS
    NSDICT = {'m': MODS}
    theid = str(uuid.uuid4())
    csl.setdefault('ITEM%s' % theid, {}).setdefault('type', 'book')
    csl_title = ''
    metadata.setdefault('id', theid)
    metadata.setdefault('owner', owner)
    #logging.info(etree.tostring(record))
    if record.xpath('//m:mods/m:titleInfo/m:nonSort', namespaces=NSDICT):
        metadata.setdefault('nonSort', record.xpath('//m:mods/m:titleInfo/m:nonSort', namespaces=NSDICT)[0].text)
        csl_title = metadata.get('nonSort') + ' '
    metadata.setdefault('title', record.xpath('//m:mods/m:titleInfo/m:title', namespaces=NSDICT)[0].text)
    csl_title += '%s' % metadata.get('title')
    if record.xpath('//m:mods/m:titleInfo/m:subTitle', namespaces=NSDICT):
        metadata.setdefault('subtitle', record.xpath('//m:mods/m:titleInfo/m:subTitle', namespaces=NSDICT)[0].text)
        csl_title += ' : %s' % metadata.get('subtitle')
    csl.setdefault('ITEM%s' % theid, {}).setdefault('title', csl_title)
    names = []
    if record.xpath('//m:mods/m:name[@type="personal"]', namespaces=NSDICT):
        for name in record.xpath('//m:mods/m:name[@type="personal"]', namespaces=NSDICT):
            tmp = {}
            csl_tmp = {}
            if name.get('valueURI'):
                tmp.setdefault('uri', name.get('valueURI'))
            tmp.setdefault('family', name.xpath('./m:namePart[@type="family"]', namespaces=NSDICT)[0].text)
            csl_tmp.setdefault('family', tmp.get('family'))
            tmp.setdefault('given', name.xpath('./m:namePart[@type="given"]', namespaces=NSDICT)[0].text)
            csl_tmp.setdefault('given', tmp.get('given'))
            names.append(tmp)
            csl.setdefault('ITEM%s' % theid, {}).setdefault('author', []).append(csl_tmp)
    metadata.setdefault('name', names)
    if record.xpath('//m:mods/m:originInfo/m:place/m:placeTerm[@type="text"]', namespaces=NSDICT):
        metadata.setdefault('place', record.xpath('//m:mods/m:originInfo/m:place/m:placeTerm[@type="text"]', namespaces=NSDICT)[0].text)
        csl.setdefault('ITEM%s' % theid, {}).setdefault('publisher-place', metadata.get('place'))
    if record.xpath('//m:mods/m:originInfo/m:publisher', namespaces=NSDICT):
        metadata.setdefault('publisher', record.xpath('//m:mods/m:originInfo/m:publisher', namespaces=NSDICT)[0].text)
        csl.setdefault('ITEM%s' % theid, {}).setdefault('publisher', metadata.get('publisher'))
    if record.xpath('//m:mods/m:originInfo/m:dateIssued', namespaces=NSDICT):
        metadata.setdefault('issued', record.xpath('//m:mods/m:originInfo/m:dateIssued', namespaces=NSDICT)[0].text)
        csl.setdefault('ITEM%s' % theid, {}).setdefault('issued', {}).setdefault('date-parts', [[metadata.get('issued')]])
    if record.xpath('//m:mods/m:language/m:languageTerm', namespaces=NSDICT):
        metadata.setdefault('language', record.xpath('//m:mods/m:language/m:languageTerm', namespaces=NSDICT)[0].text)
        csl.setdefault('ITEM%s' % theid, {}).setdefault('language', record.xpath('//m:mods/m:language/m:languageTerm', namespaces=NSDICT)[0].text)
    if record.xpath('//m:mods/m:physicalDescription/m:form', namespaces=NSDICT):
        metadata.setdefault('form', record.xpath('//m:mods/m:physicalDescription/m:form', namespaces=NSDICT)[0].text)
    if record.xpath('//m:mods/m:physicalDescription/m:extent', namespaces=NSDICT):
        metadata.setdefault('pages', record.xpath('//m:mods/m:physicalDescription/m:extent', namespaces=NSDICT)[0].text)
        csl.setdefault('ITEM%s' % theid, {}).setdefault('page', record.xpath('//m:mods/m:physicalDescription/m:extent', namespaces=NSDICT)[0].text)
    if record.xpath('//m:mods/m:abstract', namespaces=NSDICT):
        metadata.setdefault('abstract', record.xpath('//m:mods/m:abstract', namespaces=NSDICT)[0].text)
        csl.setdefault('ITEM%s' % theid, {}).setdefault('abstract', record.xpath('//m:mods/m:abstract', namespaces=NSDICT)[0].text)
    if record.xpath('//m:mods/m:note', namespaces=NSDICT):
        notes = record.xpath('//m:mods/m:note', namespaces=NSDICT)
        for note in notes:
            metadata.setdefault('note', []).append(note.text)
    if record.xpath('//m:mods/m:subject', namespaces=NSDICT):
        subj_list = []
        subjects = record.xpath('//m:mods/m:subject', namespaces=NSDICT)
        for subject in subjects:
            tmp = {}
            if subject.get('authority'):
                tmp.setdefault('authority', subject.get('authority'))
            for cat in subject:
                tmp.setdefault(cat.tag.replace('{http://www.loc.gov/mods/v3}', ''), []).append(cat.text)
            metadata.setdefault('subject', []).append(tmp)
    if record.xpath('//m:mods/m:classification', namespaces=NSDICT):
        classifications = record.xpath('//m:mods/m:classification', namespaces=NSDICT)
        for classification in classifications:
            tmp = {}
            if classification.get('authority'):
                tmp.setdefault('authority', classification.get('authority'))
            tmp.setdefault('label', classification.text)
            metadata.setdefault('classification', []).append(tmp)
    if record.xpath('//m:mods/m:relatedItem', namespaces=NSDICT):
        items = record.xpath('//m:mods/m:relatedItem', namespaces=NSDICT)
        for item in items:
            tmp = {}
            for subitem in item:
                if subitem.tag == '{http://www.loc.gov/mods/v3}titleInfo':
                    tmp.setdefault(item.get('type') + '_title', subitem[0].text)
            metadata.setdefault('relatedItem', []).append(tmp)
    if record.xpath('//m:mods/m:identifier[@type]', namespaces=NSDICT):
        ids = record.xpath('//m:mods/m:identifier[@type]', namespaces=NSDICT)
        for myid in ids:
            metadata.setdefault(myid.get('type'), []).append(myid.text)
    if record.xpath('//m:mods/m:tableOfContents', namespaces=NSDICT):
        tocs = record.xpath('//m:mods/m:tableOfContents', namespaces=NSDICT)
        for toc in tocs:
            metadata.setdefault(toc, []).append(toc.text)
    #csl_wrapper.setdefault('items', csl)
    #citation = requests.post('https://api.ub.rub.de/citeproc/mla/html/de-DE', json.dumps(csl_wrapper))
    return metadata