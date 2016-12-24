import datetime
import uuid
import logging
import simplejson as json
import rdflib

try:
    import site_secrets as secrets
except ImportError:
    import secrets

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-4s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )


def persons(filename=''):
    if filename != '':
        fr = open(filename, 'r', encoding="utf8")
        thedata = json.loads(fr.read())
        fr.close()
        print('%s records' % len(thedata))

        newdata = []
        for person in thedata:
            also_known_as = []
            if len(person.get('former_name')) > 0:
                # print(person.get('name'))
                # print(person.get('former_name'))
                also_known_as = [person.get('former_name')]
            person['also_known_as'] = also_known_as
            del person['former_name']
            # print(json.dumps(person, indent=4))
            newdata.append(person)

        fo = open('../../new_person.json', 'w')
        fo.write(json.dumps(newdata, indent=4))
        fo.close()


def works(filename=''):
    if filename != '':
        fr = open(filename, 'r', encoding="utf8")
        thedata = json.loads(fr.read())
        fr.close()
        print('%s records' % len(thedata))

        newdata = []
        for work in thedata:
            zdbid = []
            if work.get('ZDBID') and len(work.get('ZDBID')) > 0:
                zdbid = work.get('ZDBID').strip().strip().split(', ')
            work['ZDBID'] = zdbid

            doi = []
            if work.get('DOI') and len(work.get('DOI')) > 0:
                doi = work.get('DOI').strip().strip().split(', ')
            work['DOI'] = doi

            hbzid = []
            if work.get('hbz_id') and len(work.get('hbz_id')) > 0:
                hbzid = work.get('hbz_id').strip().split(', ')
            work['hbz_id'] = hbzid

            # TODO event migration
            events = []
            event = {}
            if work.get('event_name') is not None:
                if len(work.get('event_name')) > 0:
                    event.setdefault('event_name', work.get('event_name'))
                del work['event_name']
            if work.get('event_place') is not None:
                if len(work.get('event_place')) > 0:
                    event.setdefault('event_place', work.get('event_place'))
                del work['event_place']
            if work.get('place') is not None:
                if len(work.get('place')) > 0:
                    event.setdefault('event_place', work.get('place'))
            if work.get('numbering') is not None:
                if len(work.get('numbering')) > 0:
                    event.setdefault('event_numbering', work.get('numbering'))
                del work['numbering']
            if work.get('startdate_conference') is not None:
                if len(work.get('startdate_conference')) > 0:
                    event.setdefault('event_startdate', work.get('startdate_conference'))
                del work['startdate_conference']
            if work.get('enddate_conference') is not None:
                if len(work.get('enddate_conference')) > 0:
                    event.setdefault('event_enddate', work.get('enddate_conference'))
                del work['enddate_conference']
            if len(event) > 0:
                events.append(event)

            work['event'] = events

            # print(json.dumps(work, indent=4))

            newdata.append(work)

        fo = open('../../new_works.json', 'w')
        fo.write(json.dumps(newdata, indent=4))
        fo.close()


def issued_data(filename='', data_file=''):
    if filename != '':
        fr = open(filename, 'r', encoding="utf8")
        thedata = json.loads(fr.read())
        fr.close()
        print('%s records' % len(thedata))

        # read external data
        fr = open(data_file, 'r', encoding="utf8")
        extdata = json.loads(fr.read())
        fr.close()
        print('%s records' % len(extdata))

        newdata = []
        for work in thedata:

            if not work.get('issued') or len(work.get('issued')) == 0:

                if work.get('id') in extdata:
                    work['issued'] = extdata.get(work.get('id'))
                    newdata.append(work)

        logging.info('works: %s' % len(thedata))
        logging.info('new_works: %s' % len(newdata))

        fo = open('/data/issued/new_works.json', 'w')
        fo.write(json.dumps(newdata, indent=4))
        fo.close()


def delete_issued(filename=''):
    if filename != '':
        fr = open(filename, 'r', encoding="utf8")
        thedata = json.loads(fr.read())
        fr.close()
        print('%s records' % len(thedata))

        newdata = []
        for work in thedata:

            if work.get('issued') and len(work.get('issued')) > 0:
                del work['issued']

            # print(json.dumps(work, indent=4))

            newdata.append(work)

        fo = open('../../new_works.json', 'w')
        fo.write(json.dumps(newdata, indent=4))
        fo.close()


# persons('../../person.json')
# works('../../works.json')
# issued_data('/data/backup/Samstag/2016-10-01_15-28-31_hb2.not_issued.json', '/data/issued/issuedData.json')
delete_issued('/data/backup/Montag/2016-10-03_09-39-18_hb2.pubtype_Journal.json')
