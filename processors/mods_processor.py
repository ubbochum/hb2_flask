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

    csl_json = []

    MODS = 'http://www.loc.gov/mods/v3'
    MODS_NS = '{%s}' % MODS
    NSDICT = {'m': MODS}

    for mods in record.xpath('//m:mods', namespaces=NSDICT):

        csl = {}
        metadata = {}

        theid = str(uuid.uuid4())
        if mods.xpath('./m:recordInfo/m:recordIdentifier', namespaces=NSDICT):
            theid = mods.xpath('./m:recordInfo/m:recordIdentifier', namespaces=NSDICT)[0].text

        csl.setdefault('type', 'book')
        csl_title = ''

        metadata.setdefault('id', theid)
        csl.setdefault('id', theid)

        metadata.setdefault('owner', owner)
        # logging.info(etree.tostring(record))
        if mods.xpath('./m:titleInfo/m:nonSort', namespaces=NSDICT):
            metadata.setdefault('nonSort', mods.xpath('./m:titleInfo/m:nonSort', namespaces=NSDICT)[0].text)
            csl_title = metadata.get('nonSort') + ' '
        metadata.setdefault('title', mods.xpath('./m:titleInfo/m:title', namespaces=NSDICT)[0].text)
        csl_title += '%s' % metadata.get('title')
        if mods.xpath('./m:titleInfo/m:subTitle', namespaces=NSDICT):
            metadata.setdefault('subtitle', mods.xpath('./m:titleInfo/m:subTitle', namespaces=NSDICT)[0].text)
            csl_title += ' : %s' % metadata.get('subtitle')
        csl.setdefault('title', csl_title)
        names = []
        if mods.xpath('./m:name[@type="personal"]', namespaces=NSDICT):
            for name in mods.xpath('./m:name[@type="personal"]', namespaces=NSDICT):
                tmp = {}
                csl_tmp = {}
                if name.get('valueURI'):
                    tmp.setdefault('uri', name.get('valueURI'))
                tmp.setdefault('family', name.xpath('./m:namePart[@type="family"]', namespaces=NSDICT)[0].text)
                csl_tmp.setdefault('family', tmp.get('family'))
                tmp.setdefault('given', name.xpath('./m:namePart[@type="given"]', namespaces=NSDICT)[0].text)
                csl_tmp.setdefault('given', tmp.get('given'))
                names.append(tmp)
                csl.setdefault('author', []).append(csl_tmp)
        metadata.setdefault('name', names)
        if mods.xpath('./m:originInfo/m:place/m:placeTerm[@type="text"]', namespaces=NSDICT):
            metadata.setdefault('place', mods.xpath('./m:originInfo/m:place/m:placeTerm[@type="text"]', namespaces=NSDICT)[0].text)
            csl.setdefault('publisher-place', metadata.get('place'))
        if mods.xpath('./m:originInfo/m:publisher', namespaces=NSDICT):
            metadata.setdefault('publisher', mods.xpath('./m:originInfo/m:publisher', namespaces=NSDICT)[0].text)
            csl.setdefault('publisher', metadata.get('publisher'))
        if mods.xpath('./m:originInfo/m:dateIssued', namespaces=NSDICT):
            metadata.setdefault('issued', mods.xpath('./m:originInfo/m:dateIssued', namespaces=NSDICT)[0].text)
            csl.setdefault('issued', {}).setdefault('date-parts', [[metadata.get('issued').replace('[', '').replace(']', '')]])
        if mods.xpath('./m:language/m:languageTerm', namespaces=NSDICT):
            metadata.setdefault('language', mods.xpath('./m:language/m:languageTerm', namespaces=NSDICT)[0].text)
            csl.setdefault('language', mods.xpath('./m:language/m:languageTerm', namespaces=NSDICT)[0].text)
        if mods.xpath('./m:physicalDescription/m:form', namespaces=NSDICT):
            metadata.setdefault('form', mods.xpath('./m:physicalDescription/m:form', namespaces=NSDICT)[0].text)
        if mods.xpath('./m:physicalDescription/m:extent', namespaces=NSDICT):
            metadata.setdefault('pages', mods.xpath('./m:physicalDescription/m:extent', namespaces=NSDICT)[0].text)
            csl.setdefault('page', mods.xpath('./m:physicalDescription/m:extent', namespaces=NSDICT)[0].text)
        if mods.xpath('./m:abstract', namespaces=NSDICT):
            metadata.setdefault('abstract', mods.xpath('./m:abstract', namespaces=NSDICT)[0].text)
            csl.setdefault('abstract', mods.xpath('./m:abstract', namespaces=NSDICT)[0].text)
        if mods.xpath('./m:note', namespaces=NSDICT):
            notes = mods.xpath('./m:note', namespaces=NSDICT)
            for note in notes:
                metadata.setdefault('note', []).append(note.text)
        if mods.xpath('./m:subject', namespaces=NSDICT):
            subj_list = []
            subjects = mods.xpath('./m:subject', namespaces=NSDICT)
            for subject in subjects:
                tmp = {}
                if subject.get('authority'):
                    tmp.setdefault('authority', subject.get('authority'))
                for cat in subject:
                    tmp.setdefault(cat.tag.replace('{http://www.loc.gov/mods/v3}', ''), []).append(cat.text)
                metadata.setdefault('subject', []).append(tmp)
        if mods.xpath('./m:classification', namespaces=NSDICT):
            classifications = mods.xpath('./m:classification', namespaces=NSDICT)
            for classification in classifications:
                tmp = {}
                if classification.get('authority'):
                    tmp.setdefault('authority', classification.get('authority'))
                tmp.setdefault('label', classification.text)
                metadata.setdefault('classification', []).append(tmp)
        if mods.xpath('./m:relatedItem', namespaces=NSDICT):
            items = mods.xpath('./m:relatedItem', namespaces=NSDICT)
            for item in items:
                tmp = {}
                for subitem in item:
                    if subitem.tag == '{http://www.loc.gov/mods/v3}titleInfo':
                        tmp.setdefault(item.get('type') + '_title', subitem[0].text)
                metadata.setdefault('relatedItem', []).append(tmp)
        if mods.xpath('./m:identifier[@type]', namespaces=NSDICT):
            ids = mods.xpath('./m:identifier[@type]', namespaces=NSDICT)
            for myid in ids:
                metadata.setdefault(myid.get('type'), []).append(myid.text)
        if mods.xpath('./m:tableOfContents', namespaces=NSDICT):
            tocs = mods.xpath('./m:tableOfContents', namespaces=NSDICT)
            for toc in tocs:
                metadata.setdefault(toc, []).append(toc.text)

        csl_json.append(csl)

    return {'items': csl_json}
