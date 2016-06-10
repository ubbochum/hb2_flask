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


from flask import Markup
from flask.ext.babel import lazy_gettext
from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, SelectMultipleField, FileField, HiddenField, FieldList, FormField, PasswordField
from wtforms.validators import DataRequired, UUID, URL, Email, Optional, Length, Regexp, ValidationError
from wtforms.widgets import TextInput
from re import IGNORECASE
import pyisbn

LICENSES = (
    ('', lazy_gettext('Select a License')),
    ('cc_zero', lazy_gettext('Creative Commons Zero - Public Domain')),
    ('cc_by', lazy_gettext('Creative Commons Attribution')),
    ('cc_by_sa', lazy_gettext('Creative Commons Attribution Share Alike')),
    ('cc_by_nd', lazy_gettext('Creative Commons Attribution No Derivatives'))
)

LANGUAGES = [
    ('', lazy_gettext('Select a Language')),
        ('eng', lazy_gettext('English')),
        ('ger', lazy_gettext('German')),
        ('fre', lazy_gettext('French')),
        ('rus', lazy_gettext('Russian')),
        ('spa', lazy_gettext('Spanish')),
        ('ita', lazy_gettext('Italian')),
        ('jpn', lazy_gettext('Japanese')),
        ('lat', lazy_gettext('Latin')),
        ('zhn', lazy_gettext('Chinese')),
        ('dut', lazy_gettext('Dutch')),
        ('tur', lazy_gettext('Turkish')),
        ('por', lazy_gettext('Portuguese')),
        ('pol', lazy_gettext('Polish')),
        ('gre', lazy_gettext('Greek')),
        ('srp', lazy_gettext('Serbian')),
        ('cat', lazy_gettext('Catalan')),
        ('dan', lazy_gettext('Danish')),
        ('cze', lazy_gettext('Czech')),
        ('kor', lazy_gettext('Korean')),
        ('ara', lazy_gettext('Arabic')),
        ('hun', lazy_gettext('Hungarian')),
        ('swe', lazy_gettext('Swedish')),
        ('ukr', lazy_gettext('Ukranian')),
        ('heb', lazy_gettext('Hebrew')),
        ('hrv', lazy_gettext('Croatian')),
        ('slo', lazy_gettext('Slovak')),
        ('nor', lazy_gettext('Norwegian')),
        ('rum', lazy_gettext('Romanian')),
        ('fin', lazy_gettext('Finnish')),
        ('geo', lazy_gettext('Georgian')),
        ('bul', lazy_gettext('Bulgarian')),
        ('grc', lazy_gettext('Ancient Greek')),
        ('ind', lazy_gettext('Indonesian Language')),
        ('gmh', lazy_gettext('Middle High German')),
        ('mon', lazy_gettext('Mongolian Language')),
        ('peo', lazy_gettext('Persian')),
        ('alb', lazy_gettext('Albanian')),
        ('bos', lazy_gettext('Bosnian')),
    ]

USER_ROLES = [
    ('', lazy_gettext('Select a Role')),
    ('aut', lazy_gettext('Author')),
    ('aui', lazy_gettext('Author of Foreword')),
    ('ive', lazy_gettext('Interviewee')),
    ('ivr', lazy_gettext('Interviewer')),
    ('trl', lazy_gettext('Translator')),
    ('ths', lazy_gettext('Thesis Advisor')),
    ('ctb', lazy_gettext('Contributor')),
    ('edt', lazy_gettext('Editor')),
    ('inv', lazy_gettext('Inventor')),
    ('prg', lazy_gettext('Programmer')),
    ('drt', lazy_gettext('Director')),
    ('spk', lazy_gettext('Speaker')),
    ('cmp', lazy_gettext('Composer')),
]

ADMIN_ROLES = USER_ROLES[:]

ADMIN_ROLES.extend([
    ('abr', lazy_gettext('Abridger')),
    ('act', lazy_gettext('Actor')),
    ('aft', lazy_gettext('Author of Afterword')),
    ('arr', lazy_gettext('Arranger')),
    ('chr', lazy_gettext('Choreographer')),
    ('cmp', lazy_gettext('Composer')),
    ('cst', lazy_gettext('Costume Designer')),
    ('cwt', lazy_gettext('Commentator for written text')),
    ('elg', lazy_gettext('Electrician')),
    ('fmk', lazy_gettext('Filmmaker')),
    ('hnr', lazy_gettext('Honoree')),
    ('ill', lazy_gettext('Illustrator')),
    ('itr', lazy_gettext('Instrumentalist')),
    ('mod', lazy_gettext('Moderator')),
    ('mus', lazy_gettext('Musician')),
    ('org', lazy_gettext('Originator')),
    ('pdr', lazy_gettext('Project Director')),
    ('pht', lazy_gettext('Photographer')),
    ('pmn', lazy_gettext('Production Manager')),
    ('pro', lazy_gettext('Producer')),
    ('red', lazy_gettext('Redaktor')),
    ('sng', lazy_gettext('Singer')),
    ('std', lazy_gettext('Set designer')),
    ('stl', lazy_gettext('Storyteller')),
    ('tcd', lazy_gettext('Technical Director')),
    ])

USER_PUBTYPES = [
    ('', lazy_gettext('Select a Publication Type')),
    ('ArticleJournal', lazy_gettext('Article in Journal')),
    ('Chapter', lazy_gettext('Chapter in...')),
    ('Collection', lazy_gettext('Collection')),
    ('MultivolumeWork', lazy_gettext('MultivolumeWork')),
    ('Monograph', lazy_gettext('Monograph')),
    ('Other', lazy_gettext('Other')),
    ('Report', lazy_gettext('Report')),
    ('Patent', lazy_gettext('Patent')),
    ('Thesis', lazy_gettext('Thesis')),
    ('Software', lazy_gettext('Software')),
    ('ResearchData', lazy_gettext('Research Data')),
]

ADMIN_PUBTYPES = USER_PUBTYPES[:]

ADMIN_PUBTYPES.extend([
    ('ArticleNewspaper', lazy_gettext('Article in Newspaper')),
    ('AudioVideoDocument', lazy_gettext('Audio or Video Document')),
    ('ChapterInLegalCommentary', lazy_gettext('Chapter in a Legal Commentary')),
    ('Conference', lazy_gettext('Conference')),
    ('Edition', lazy_gettext('Edition')),
    ('InternetDocument', lazy_gettext('Internet Document')),
    ('Journal', lazy_gettext('Journal')),
    ('Lecture', lazy_gettext('Lecture')),
    ('LegalCommentary', lazy_gettext('Legal Commentary')),
    ('Newspaper', lazy_gettext('Newspaper')),
    ('PressRelease', lazy_gettext('Press Release')),
    ('RadioTVProgram', lazy_gettext('Radio or TV program')),
    ('Series', lazy_gettext('Series')),
    ('SpecialIssue', lazy_gettext('Special Issue')),
    ('Standard', lazy_gettext('Standard')),
])

PROJECT_TYPES = [
    ('', lazy_gettext('Select a Project Type')),
    ('fp7', lazy_gettext('FP7')),
    ('h2020', lazy_gettext('Horizon 2020')),
    ('dfg', lazy_gettext('DFG')),
    ('mercur', lazy_gettext('Mercator Research Center Ruhr (MERCUR)')),
    ('other', lazy_gettext('Other')),
]

CARRIER = [
    ('', lazy_gettext('Select a Project Type')),
    ('AudioDisc', lazy_gettext('Audio disc')),
    ('Audiocassette', lazy_gettext('Audiocassette')),
    ('AudiotapeReel', lazy_gettext('Audiotape reel')),
    ('ComputerDisc', lazy_gettext('Computer disc')),
    ('OnlineRessource', lazy_gettext('Online-ressource')),
    ('Microfiche', lazy_gettext('Microfiche')),
    ('MicrofilmCassette', lazy_gettext('Microfilm cassette')),
    ('MicrofilmReel', lazy_gettext('Microfilm reel')),
    ('MicrofilmRoll', lazy_gettext('Microfilm roll')),
    ('MicroscopeSlide', lazy_gettext('Microscope slide')),
    ('FilmCassette', lazy_gettext('Film cassette')),
    ('FilmReel', lazy_gettext('Film reel')),
    ('FilmRoll', lazy_gettext('Film roll')),
    ('FilmStrip', lazy_gettext('Film strip')),
    ('Object', lazy_gettext('Object')),
    ('card', lazy_gettext('card')),
    ('Videocassette', lazy_gettext('Videocassette')),
    ('Videodisc', lazy_gettext('Videodisc')),
    ('Unspecified', lazy_gettext('Unspecified')),
]

def Isbn(form, field):
    theisbn = pyisbn.Isbn(field.data.strip())
    if theisbn.validate() == False:
        raise ValidationError(lazy_gettext('Not a valid ISBN!'))
    
class CustomTextInput(TextInput):
    '''Enable both placeholder and help text descriptions.'''
    def __init__(self, **kwargs):
        self.params = kwargs
        super(CustomTextInput, self).__init__()

    def __call__(self, field, **kwargs):
        for param, value in self.params.items():
            kwargs.setdefault(param, value)
        return super(CustomTextInput, self).__call__(field, **kwargs)

class URIForm(Form):
    address = StringField(lazy_gettext('URI'), validators=[URL(), Optional()])
    label = StringField(lazy_gettext('Label'), validators=[Optional()])

class TableOfContentsForm(Form):
    uri = StringField('URI to Table of Contents', validators=[URL(), Optional()], widget=CustomTextInput(placeholder=lazy_gettext('e.g. http://d-nb.info/1035670232/04')))
    toc = TextAreaField(lazy_gettext('Table of Contents in textform'), validators=[Optional()])

class AbstractForm(URIForm):
    content = TextAreaField(lazy_gettext('Abstract'), validators=[Optional()])
    language = SelectField(lazy_gettext('Language'), validators=[Optional()], choices=LANGUAGES)
    shareable = BooleanField(lazy_gettext('Shareable'))

class PersonForm(Form):
    # salutation = SelectField(lazy_gettext('Salutation'), choices=[
    #     ('m', lazy_gettext('Mr.')),
    #     ('f', lazy_gettext('Mrs./Ms.')),
    # ])
    name = StringField(lazy_gettext('Name'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('Name, Given name')))
    #former_name = StringField(lazy_gettext('Former Name'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('Family name, given name')), description=lazy_gettext('If you have more than one former name, please separate them by semicolon.'))
    gnd = StringField(lazy_gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')], description=Markup(lazy_gettext('<a href="https://portal.d-nb.de/opac.htm?method=showOptions#top" target="_blank">Find in GND</a>')))
    orcid = StringField(lazy_gettext('ORCID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="https://orcid.org/orcid-search/search" target="_blank">Find in ORCID</a>')))
    role = SelectMultipleField(lazy_gettext('Role'))
    corresponding_author = BooleanField(lazy_gettext('Corresponding Author'), validators=[Optional()], description=lazy_gettext('The person handling the publication process'))
    rubi = BooleanField(lazy_gettext('RUB member'), validators=[Optional()])
    tudo = BooleanField(lazy_gettext('TUDO member'), validators=[Optional()])

    #admin_only = ['gnd']

class OpenAccessForm(Form):
    project_identifier = StringField(lazy_gettext('Project Identifier'), validators=[URL(), Optional()], widget=CustomTextInput(placeholder=lazy_gettext('e.g. http://purl.org/info:eu-repo/grantAgreement/EC/FP7/12345P')))
    project_type = SelectField(lazy_gettext('Project Type'), choices=PROJECT_TYPES, validators=[Optional()])
    publication_version = SelectField(lazy_gettext('Publication Version'), choices=[
        ('', lazy_gettext('Select a Publication Version')),
        ('accepted', lazy_gettext('Accepted')),
        ('draft', lazy_gettext('Draft')),
        ('forthcoming', lazy_gettext('Forthcoming')),
        ('legal', lazy_gettext('Legal')),
        ('non_peer_reviewed', lazy_gettext('Non Peer Reviewed')),
        ('peer-reviewed', lazy_gettext('Peer Reviewed')),
        ('published', lazy_gettext('Published')),
        ('rejected', lazy_gettext('Rejected')),
        ('unpublished', lazy_gettext('Unpublished')),
    ], validators=[Optional()])
    fee = BooleanField(lazy_gettext('Author Pays'))
    #license_condition = StringField(lazy_gettext('License Condition'), validators=[URL(), Optional()], widget=CustomTextInput(placeholder=lazy_gettext('e.g. https://creativecommons.org/licenses/by/4.0/')))
    access_level = SelectField(lazy_gettext('Access Level'), choices=[
        ('', lazy_gettext('Select an Access Level')),
        ('closed', lazy_gettext('Closed Access')),
        ('embargoed', lazy_gettext('Embargoed Access')),
        ('restricted', lazy_gettext('Restricted Access')),
        ('open', lazy_gettext('Open Access')),
    ], validators=[Optional()])
    embargo_end_date = StringField(lazy_gettext('Embargo End Date'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    mime_type = SelectField(lazy_gettext('MIME-type'), choices=[
        ('pdf', lazy_gettext('application/pdf')),
        ('msword', lazy_gettext('application/msword')),
        ('x-latex', lazy_gettext('application/x-latex')),
        ('plain', lazy_gettext('text/plain')),
    ], validators=[Optional()])

class SEDForm(Form):
    start = StringField(lazy_gettext('Start Date'), validators=[Optional(), Regexp('[12]\d{3}(?:-[01]\d)?(?:-[0123]\d)?')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')))
    end = StringField(lazy_gettext('End Date'), validators=[Optional(), Regexp('[12]\d{3}(?:-[01]\d)?(?:-[0123]\d)?')],
                        widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')))
    label = StringField(lazy_gettext('Label'), validators=[Optional()])
# TODO: Brauchen wir eine ID, und wenn ja, wohin?

class IDLForm(Form):
    id = StringField(lazy_gettext('ID'), validators=[Optional()])
    label = StringField(lazy_gettext('Label'), validators=[Optional()])

class IssueForm(SEDForm):
    pass


class AwardForm(SEDForm):
    pass


class CVForm(SEDForm):
    pass


class MembershipForm(SEDForm):
    pass


class ReviewerForm(SEDForm):
    ISSN = StringField(lazy_gettext('ISSN'), validators=[Optional()])
    ZDBID = StringField(lazy_gettext('ZDBID'), validators=[Optional()])


class EditorForm(ReviewerForm):
    start_volume = StringField(lazy_gettext('First Volume'), validators=[Optional()])
    end_volume = StringField(lazy_gettext('Last Volume'), validators=[Optional()])
    start_issue = StringField(lazy_gettext('First Issue'), validators=[Optional()])
    end_issue = StringField(lazy_gettext('Last Issue'), validators=[Optional()])


class ProjectForm(SEDForm):
    project_id = StringField(lazy_gettext('Project ID'), validators=[Optional()])
    project_type = SelectField('Project Type', choices=PROJECT_TYPES, validators=[Optional()])

class AffiliationForm(SEDForm):
    #organisation_id = StringField(lazy_gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')])
    organisation_id = StringField(lazy_gettext('ID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="https://portal.d-nb.de/opac.htm?method=showOptions#top" target="_blank">Find in GND</a>')))

class GroupForm(SEDForm):
    #organisation_id = StringField(lazy_gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')])
    group_id = StringField(lazy_gettext('ID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="https://portal.d-nb.de/opac.htm?method=showOptions#top" target="_blank">Find in GND</a>')))

class ThesisProfileForm(Form):
    title = StringField(lazy_gettext('Title'), validators=[Optional()])
    year = StringField(lazy_gettext('Year'), validators=[Optional()])
    thesis_type = SelectField(lazy_gettext('Type'), choices=[
        ('', lazy_gettext('Select a Thesis Type')),
        ('m', lazy_gettext('M.A. Thesis')),
        ('d', lazy_gettext('M.Sc. Thesis')),
        ('p', lazy_gettext('Doctoral Thesis')),
        ('h', lazy_gettext('Professorial Dissertation')),
    ])


class URLProfileForm(Form):
    #url = FieldList(StringField(lazy_gettext('URL'), validators=[URL(), Optional()]), min_entries=1)
    url = StringField(lazy_gettext('URL'), validators=[URL(), Optional()])
    label = SelectField(lazy_gettext('Label'), choices=[
        ('', lazy_gettext('Select a Label for the URL')),
        ('hp', lazy_gettext('Homepage')),
        ('rg', lazy_gettext('ResearchGate')),
        ('ri', lazy_gettext('ResearcherID')),
        ('an', lazy_gettext('AcademiaNet')),
        ('ae', lazy_gettext('Academia.edu')),
        ('wp', lazy_gettext('Wikipedia')),
        ('xi', lazy_gettext('Xing')),
        ('li', lazy_gettext('LinkedIn')),
        ('bl', lazy_gettext('Blog')),
        ('fb', lazy_gettext('Facebook')),
        ('tw', lazy_gettext('Twitter')),
        ('ic', lazy_gettext('identi.ca')),
        ('zt', lazy_gettext('Zotero')),
        ('md', lazy_gettext('Mendeley')),
        ('mi', lazy_gettext('Other')),
    ])

class PersonAdminForm(Form):
    salutation = SelectField(lazy_gettext('Salutation'), choices=[
        ('', lazy_gettext('Select a Salutation')),
        ('m', lazy_gettext('Mr.')),
        ('f', lazy_gettext('Mrs./Ms.')),
    ])
    name = StringField(lazy_gettext('Name'), widget=CustomTextInput(placeholder=lazy_gettext('Family Name, Given Name')))
    former_name = StringField(lazy_gettext('Former Name'), validators=[Optional()],
                              widget=CustomTextInput(placeholder=lazy_gettext('Family Name Only')),
                              description=lazy_gettext(
                                  'If you have more than one former names, please separate them by semicolon.'))
    email = StringField(lazy_gettext('E-Mail'), validators=[Optional()],
                        widget=CustomTextInput(placeholder=lazy_gettext('Your e-mail address')))
    account = FieldList(StringField(lazy_gettext('Account'), validators=[Optional(), Length(min=7, max=7)], widget=CustomTextInput(placeholder=lazy_gettext('Your 7-digit account number'))))
    dwid = StringField(lazy_gettext('Verwaltungs-ID'), validators=[Optional()])
    affiliation = FieldList(FormField(AffiliationForm), min_entries=1)
    group = FieldList(FormField(GroupForm), min_entries=1)
    url = FieldList(FormField(URLProfileForm), min_entries=1)
    # entfernt nach Diskussion mit Datenschutzbeauftragten: thesis = FieldList(FormField(ThesisProfileForm), min_entries=1)
    #image = FileField(lazy_gettext('Image'))

    #membership = FieldList(FormField(MembershipForm), validators=[Optional()], min_entries=1)
    #award = FieldList(FormField(AwardForm), validators=[Optional()], min_entries=1)
    #cv = FieldList(FormField(CVForm), validators=[Optional()], min_entries=1)
    #project = FieldList(FormField(ProjectForm), validators=[Optional()], min_entries=1)
    #reviewer = FieldList(FormField(ReviewerForm), validators=[Optional()], min_entries=1)
    #editor = FieldList(FormField(EditorForm), validators=[Optional()], min_entries=1)

    gnd = StringField(lazy_gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')], description=Markup(lazy_gettext('<a href="https://portal.d-nb.de/opac.htm?method=showOptions#top" target="_blank">Find in GND</a>')))
    orcid = StringField(lazy_gettext('ORCID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="https://orcid.org/orcid-search/search" target="_blank">Find in ORCID</a>')))
    viaf = StringField(lazy_gettext('VIAF'), validators=[Optional()], description=Markup(lazy_gettext('<a href="http://www.viaf.org" target="_blank">Find in VIAF</a>')))
    isni = StringField(lazy_gettext('ISNI'), validators=[Optional()], description=Markup(lazy_gettext('<a href="http://www.isni.org" target="_blank">Find in ISNI</a>')))
    researcher_id = StringField(lazy_gettext('Researcher ID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="http://www.researcherid.com/ViewProfileSearch.action" target="_blank">Find in Researcher ID</a>')))
    #scopus_id = StringField(lazy_gettext('Scopus Author ID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="https://www.scopus.com/search/form/authorFreeLookup.uri" target="_blank">Find in Scopus Author ID</a>')))
    scopus_id = FieldList(StringField(lazy_gettext('Scopus Author ID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="https://www.scopus.com/search/form/authorFreeLookup.uri" target="_blank">Find in Scopus Author ID</a>'))), min_entries=1)
    arxiv_id = StringField(lazy_gettext('ArXiv Author ID'), validators=[Optional()], description=Markup(lazy_gettext('<a href="http://arxiv.org/find" target="_blank">Find in ArXiv Author ID</a>')))
    research_interest = FieldList(StringField(lazy_gettext('Research Interest')), validators=[Optional()], min_entries=1)

    status = SelectMultipleField(lazy_gettext('Status'), choices=[
        ('', lazy_gettext('Select a Status')),
        ('alumnus', lazy_gettext('Alumnus')),
        ('assistant_lecturer', lazy_gettext('Assistant Lecturer')),
        ('ranking', lazy_gettext('Relevant for Ranking')),
        ('external', lazy_gettext('External Staff')),
        ('manually_added', lazy_gettext('Manually added')),
        ('official', lazy_gettext('Official')),
        ('official_ns', lazy_gettext('Official, Non-Scientific')),
        ('research_school', lazy_gettext('Doctoral Candidate')),
        ('principal_investigator', lazy_gettext('Principal Investigator')),
        ('professor', lazy_gettext('Professor')),
        ('emeritus', lazy_gettext('Emeritus')),
        ('teaching_assistant', lazy_gettext('Teaching Assistant')),
        ('tech_admin', lazy_gettext('Technical and Administrative Staff')),
    ], description=lazy_gettext('Choose one or more Status'))

    note = TextAreaField(lazy_gettext('Note'), validators=[Optional()],
                             description=lazy_gettext('Commentary on the person'))
    data_supplied = StringField(lazy_gettext('Data Supplied'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')],
                              description=lazy_gettext('The date of the latest data delivery'),
                                widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')))

    editorial_status = SelectField(lazy_gettext('Editorial Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select an Editorial Status')),
        ('new', lazy_gettext('New')),
        ('in_process', lazy_gettext('In Process')),
        ('processed', lazy_gettext('Processed')),
        ('final_editing', lazy_gettext('Final Editing')),
        ('finalized', lazy_gettext('Finalized')),
        ('imported', lazy_gettext('Imported')),
        ('deleted', lazy_gettext('Deleted')),
    ], default='new')
    #catalog = FieldList(StringField(lazy_gettext('Data Catalog'), validators=[DataRequired()]), min_entries=1)
    catalog = SelectMultipleField(lazy_gettext('Data Catalog'), validators=[DataRequired()], choices=[
        ('Ruhr-Universität Bochum', lazy_gettext('Ruhr-Universität Bochum')),
        ('Technische Universität Dortmund', lazy_gettext('Technische Universität Dortmund')),
        ('Temporäre Daten', lazy_gettext('Temporäre Daten')),
    ], description=lazy_gettext('Choose one or more DataCatalog'))
    created = StringField(lazy_gettext('Record Creation Date'), widget=CustomTextInput(readonly='readonly'))
    changed = StringField(lazy_gettext('Record Change Date'), widget=CustomTextInput(readonly='readonly'))
    id = StringField(lazy_gettext('ID'), widget=CustomTextInput(readonly='readonly'))
    owner = FieldList(StringField(lazy_gettext('Owner'), validators=[DataRequired()]), min_entries=1)
    deskman = StringField(lazy_gettext('Deskman'), validators=[Optional()], widget=CustomTextInput(admin_only='admin_only'))

    admin_only = ['status', 'data_supplied', 'dwid', 'account', 'owner', 'deskman']

    def groups(self):
        yield [
            {'group': [self.salutation, self.name, self.former_name, self.account, self.email, self.status, self.research_interest, self.url], 'label': lazy_gettext('Basic')},
            {'group': [self.gnd, self.orcid, self.dwid, self.viaf, self.isni, self.researcher_id, self.scopus_id, self.arxiv_id], 'label': lazy_gettext('IDs')},
            {'group': [self.affiliation, self.group], 'label': lazy_gettext('Affiliation')},
            {'group': [self.note, self.data_supplied], 'label': lazy_gettext('Notes')},
            #{'group': [self.editor], 'label': lazy_gettext('Editor')},
            #{'group': [self.cv], 'label': lazy_gettext('CV') + ' (P)'},
            #{'group': [self.thesis], 'label': lazy_gettext('Thesis')},
            #{'group': [self.membership], 'label': lazy_gettext('Membership') + ' (P)'},
            #{'group': [self.award], 'label': lazy_gettext('Award') + ' (P)'},
            #{'group': [self.project], 'label': lazy_gettext('Project') + ' (P)'},
            #{'group': [self.reviewer], 'label': lazy_gettext('Reviewer') + ' (P)'},
            {'group': [self.id, self.created, self.changed, self.editorial_status, self.catalog, self.owner, self.deskman], 'label': lazy_gettext('Administrative')},
        ]

class DestatisForm(IDLForm):
    pass

class AccountForm(IDLForm):
    pass

class OrgaAdminForm(Form):
    pref_label = StringField(lazy_gettext('Label'))
    #alt_label = FieldList(StringField(lazy_gettext('Alternative Label')), min_entries=1)
    #account = StringField(lazy_gettext('Account'))
    id = StringField(lazy_gettext('Organisation ID'), description=lazy_gettext('An Organisation ID such as GND, ISNI, Ringgold or a URI'), validators=[DataRequired()])
    # Die folgende Zeile erzeugt btgl. des Solr-Schemas nicht konsistente Daten!
    #account = FieldList(FormField(AccountForm), min_entries=1)
    dwid = StringField(lazy_gettext('Verwaltungs-ID'), validators=[Optional()])
    parent_id = StringField(lazy_gettext('Parent ID'))
    parent_label = StringField(lazy_gettext('Parent Label'))
    start_date = StringField(lazy_gettext('Start Date'))
    end_date = StringField(lazy_gettext('End Date'))
    correction_request = StringField(lazy_gettext('Correction Request'))
    owner = FieldList(StringField(lazy_gettext('Owner')), min_entries=1)
    editorial_status = SelectField(lazy_gettext('Editorial Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select an Editorial Status')),
        ('new', lazy_gettext('New')),
        ('in_process', lazy_gettext('In Process')),
        ('processed', lazy_gettext('Processed')),
        ('final_editing', lazy_gettext('Final Editing')),
        ('finalized', lazy_gettext('Finalized')),
        ('imported', lazy_gettext('Imported')),
        ('deleted', lazy_gettext('Deleted')),
    ], default='new')
    #catalog = FieldList(StringField(lazy_gettext('Data Catalog'), validators=[DataRequired()]), min_entries=1)
    catalog = SelectMultipleField(lazy_gettext('Data Catalog'), validators=[DataRequired()], choices=[
        ('Ruhr-Universität Bochum', lazy_gettext('Ruhr-Universität Bochum')),
        ('Technische Universität Dortmund', lazy_gettext('Technische Universität Dortmund')),
        ('Temporäre Daten', lazy_gettext('Temporäre Daten')),
    ], description=lazy_gettext('Choose one or more DataCatalog'))
    created = StringField(lazy_gettext('Record Creation Date'), widget=CustomTextInput(readonly='readonly'))
    changed = StringField(lazy_gettext('Record Change Date'), widget=CustomTextInput(readonly='readonly'))
    destatis = FieldList(FormField(DestatisForm), min_entries=1)
    # child_id = StringField(lazy_gettext('Child ID'))
    # child_label = StringField(lazy_gettext('Child Label'))


class GroupAdminForm(Form):
    pref_label = StringField(lazy_gettext('Label'))
    #alt_label = FieldList(StringField(lazy_gettext('Alternative Label')), min_entries=1)
    #account = StringField(lazy_gettext('Account'))
    id = StringField(lazy_gettext('Working Group ID'), description=lazy_gettext('An Working Group ID such as GND, ISNI or a URI'), validators=[DataRequired()])
    # Die folgende Zeile erzeugt btgl. des Solr-Schemas nicht konsistente Daten!
    #account = FieldList(FormField(AccountForm), min_entries=1)
    #dwid = StringField(lazy_gettext('Verwaltungs-ID'), validators=[Optional()])
    parent_id = StringField(lazy_gettext('Parent ID'))
    parent_label = StringField(lazy_gettext('Parent Label'))
    start_date = StringField(lazy_gettext('Start Date'))
    end_date = StringField(lazy_gettext('End Date'))
    correction_request = StringField(lazy_gettext('Correction Request'))
    owner = FieldList(StringField(lazy_gettext('Owner')), min_entries=1)
    editorial_status = SelectField(lazy_gettext('Editorial Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select an Editorial Status')),
        ('new', lazy_gettext('New')),
        ('in_process', lazy_gettext('In Process')),
        ('processed', lazy_gettext('Processed')),
        ('final_editing', lazy_gettext('Final Editing')),
        ('finalized', lazy_gettext('Finalized')),
        ('imported', lazy_gettext('Imported')),
        ('deleted', lazy_gettext('Deleted')),
    ], default='new')
    #catalog = FieldList(StringField(lazy_gettext('Data Catalog'), validators=[DataRequired()]), min_entries=1)
    catalog = SelectMultipleField(lazy_gettext('Data Catalog'), validators=[DataRequired()], choices=[
        ('Ruhr-Universität Bochum', lazy_gettext('Ruhr-Universität Bochum')),
        ('Technische Universität Dortmund', lazy_gettext('Technische Universität Dortmund')),
        ('Temporäre Daten', lazy_gettext('Temporäre Daten')),
    ], description=lazy_gettext('Choose one or more DataCatalog'))
    created = StringField(lazy_gettext('Record Creation Date'), widget=CustomTextInput(readonly='readonly'))
    changed = StringField(lazy_gettext('Record Change Date'), widget=CustomTextInput(readonly='readonly'))
    destatis = FieldList(FormField(DestatisForm), min_entries=1)
    # child_id = StringField(lazy_gettext('Child ID'))
    # child_label = StringField(lazy_gettext('Child Label'))


class PersonProfileForm(PersonForm):
    image = FileField(lazy_gettext('Image'))
    url = FieldList(StringField('URL', validators=[URL(), Optional()]), min_entries=1)

class CorporationForm(Form):
    name = StringField(lazy_gettext('Name'))
    role = SelectMultipleField(lazy_gettext('Role'), choices=[
        ('', lazy_gettext('Select a Role')),
        ('ctb', lazy_gettext('Contributor')),
        ('edt', lazy_gettext('Editor')),
        ('his', lazy_gettext('Host institution')),
        ('dgg', lazy_gettext('Degree granting institution')),
        ('orm', lazy_gettext('Organizer')),
        ('pta', lazy_gettext('Patent applicant')),
        ('brd', lazy_gettext('Broadcaster')),
    ])

    gnd = StringField(lazy_gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')], description=Markup(lazy_gettext('<a href="https://portal.d-nb.de/opac.htm?method=showOptions#top" target="_blank">Find in GND</a>')))
    viaf = StringField(lazy_gettext('VIAF'), validators=[Optional()])
    isni = StringField(lazy_gettext('ISNI'), validators=[Optional()])

    admin_only = ['gnd', 'viaf', 'isni']

class HasPartForm(Form):
    has_part = StringField(lazy_gettext('Has Part'))

class IsPartOfForm(Form):
    is_part_of = StringField(lazy_gettext('Is Part of'))
    volume = StringField(lazy_gettext('Volume'))

class SpecialIssueRelationForm(IsPartOfForm):
    is_part_of = StringField(lazy_gettext('Is Part of'))
    volume = StringField(lazy_gettext('Volume'))
    issue = StringField(lazy_gettext('Issue'))

class OtherVersionForm(Form):
    other_version = StringField(lazy_gettext('Other Version'))
    version = SelectField(lazy_gettext('Version'), choices=[
        ('', lazy_gettext('Select a Version')),
        ('preprint', lazy_gettext('Preprint')),
        ('postprint', lazy_gettext('Postprint')),
        ('publischers_version', lazy_gettext("Publisher's Version")),
    ])

class OtherRelationForm(IsPartOfForm):
    page_first = StringField(lazy_gettext('First Page'))
    page_last = StringField(lazy_gettext('Last Page'))

class ChapterRelationForm(IsPartOfForm):
    page_first = StringField(lazy_gettext('First Page'))
    page_last = StringField(lazy_gettext('Last Page'))

class ArticleRelationForm(IsPartOfForm):
    # For reasons of ordering we don't inherit from ChapterRelationForm here...
    volume = StringField(lazy_gettext('Volume'))
    issue = StringField(lazy_gettext('Issue'))
    page_first = StringField(lazy_gettext('First Page'))
    page_last = StringField(lazy_gettext('Last Page'))

class NewspaperRelationForm(IsPartOfForm):
    # For reasons of ordering we don't inherit from ChapterRelationForm here...
    volume = StringField(lazy_gettext('Volume'))
    issue = StringField(lazy_gettext('Edition'), widget=CustomTextInput(
        placeholder=lazy_gettext('Name or number of the edition that the article was published in')))
    page_first = StringField(lazy_gettext('First Page'))
    page_last = StringField(lazy_gettext('Last Page'))

class ContainerRelationForm(IsPartOfForm):
    volume = StringField(lazy_gettext('Volume'), validators=[Optional()])

class MonographRelationForm(ContainerRelationForm):
    pass

class OtherTitleForm(Form):
    other_title = StringField(lazy_gettext('Other Title'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('translated title, parallel title or EST of the work')))
    language = SelectField(lazy_gettext('Language'), validators=[Optional()], choices=LANGUAGES)

class WorkForm(Form):
    pubtype = SelectField(lazy_gettext('Type'), validators=[Optional()])
    title = StringField(lazy_gettext('Title'), validators=[DataRequired()], widget=CustomTextInput(placeholder=lazy_gettext('The title of the work')))
    subtitle = StringField(lazy_gettext('Subtitle'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('The subtitle of the work')))
    title_supplement = StringField(lazy_gettext('Title Supplement'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('Additions to the title of the work')))
    other_title = FieldList(FormField(OtherTitleForm), min_entries=1)
    person = FieldList(FormField(PersonForm), min_entries=1)
    corporation = FieldList(FormField(CorporationForm), min_entries=1)
    uri = FieldList(StringField(lazy_gettext('URI'), validators=[URL(), Optional()]), min_entries=1, widget=CustomTextInput(placeholder=lazy_gettext('A URI, URL, or URN')))
    DOI = StringField(lazy_gettext('DOI'), validators=[Optional(), Regexp('^10\.[0-9]{4,}(?:\.[0-9]+)*\/[a-z0-9\-\._]+', IGNORECASE)])
    PMID = StringField(lazy_gettext('PubMed ID'), widget=CustomTextInput(placeholder=(lazy_gettext('e.g. 15894097'))))
    WOSID = StringField(lazy_gettext('Web of Science ID'), widget=CustomTextInput(placeholder=(lazy_gettext('e.g. 000229082300022'))))
    language = FieldList(SelectField(lazy_gettext('Language'), validators=[Optional()], choices=LANGUAGES), min_entries=1)
    # issued = DateField(lazy_gettext('Publication Date'), validators=[Optional()])
    issued = StringField(lazy_gettext('Date'), validators=[Optional(), Regexp('[12]\d{3}(?:-[01]\d)?(?:-[0123]\d)?')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')))
    accessed = StringField(lazy_gettext('Last Seen'), validators=[Optional(), Regexp('[12]\d{3}(?:-[01]\d)?(?:-[0123]\d)?')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')))
    additions = StringField(lazy_gettext('Additions'), validators=[Optional()])
    keyword = FieldList(StringField(lazy_gettext('Keyword'), validators=[Optional()]), min_entries=1)
    keyword_temporal = FieldList(StringField(lazy_gettext('Temporal'), validators=[Optional()]), min_entries=1)
    keyword_geographic = FieldList(StringField(lazy_gettext('Geographic'), validators=[Optional()]), min_entries=1)
    swd_subject = FieldList(FormField(IDLForm), min_entries=1)
    ddc_subject = FieldList(FormField(IDLForm), min_entries=1)
    mesh_subject = FieldList(FormField(IDLForm), min_entries=1)
    stw_subject = FieldList(FormField(IDLForm), min_entries=1)
    lcsh_subject = FieldList(FormField(IDLForm), min_entries=1)
    thesoz_subject = FieldList(FormField(IDLForm), min_entries=1)

    abstract = FieldList(FormField(AbstractForm), min_entries=1)
    number_of_pages = StringField(lazy_gettext('Extent'), validators=[Optional()])
    #medium = StringField(lazy_gettext('Medium'), validators=[Optional()])
    medium = SelectField(lazy_gettext('Medium'), validators=[Optional()], choices=CARRIER)
    note = TextAreaField(lazy_gettext('Notes'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('Additional information about the work')))
    # id = HiddenField(lazy_gettext('UUID'), validators=[UUID(), Optional()])
    # created = HiddenField(lazy_gettext('Record Creation Date'))
    # changed = HiddenField(lazy_gettext('Record Change Date'))

    id = StringField(lazy_gettext('UUID'), validators=[UUID(), Optional()], widget=CustomTextInput(readonly='readonly'))
    affiliation_context = FieldList(StringField(lazy_gettext('Affiliation Context'), validators=[Optional()], widget=CustomTextInput(
        placeholder=lazy_gettext('The organisational unit this publication belongs to'))), min_entries=1)
    group_context = FieldList(StringField(lazy_gettext('Working Group Context'), validators=[Optional()], widget=CustomTextInput(
        placeholder=lazy_gettext('The working group this publication belongs to'))), min_entries=1)
    created = StringField(lazy_gettext('Record Creation Date'), widget=CustomTextInput(readonly='readonly'))
    changed = StringField(lazy_gettext('Record Change Date'), widget=CustomTextInput(readonly='readonly'))
    publication_status = SelectField(lazy_gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select a Publication Status')),
        ('published', lazy_gettext('Published')),
        ('unpublished', lazy_gettext('Unpublished'))
    ], default='published')
    editorial_status = SelectField(lazy_gettext('Editorial Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select an Editorial Status')),
        ('new', lazy_gettext('New')),
        ('in_process', lazy_gettext('In Process')),
        ('processed', lazy_gettext('Processed')),
        ('final_editing', lazy_gettext('Final Editing')),
        ('finalized', lazy_gettext('Finalized')),
        ('imported', lazy_gettext('Imported')),
        ('deleted', lazy_gettext('Deleted')),
    ], default='new')
    owner = FieldList(StringField(lazy_gettext('Owner'), validators=[DataRequired()]), min_entries=1)
    #catalog = FieldList(StringField(lazy_gettext('Data Catalog'), validators=[DataRequired()]), min_entries=1)
    catalog = SelectMultipleField(lazy_gettext('Data Catalog'), validators=[DataRequired()], choices=[
        ('Ruhr-Universität Bochum', lazy_gettext('Ruhr-Universität Bochum')),
        ('Technische Universität Dortmund', lazy_gettext('Technische Universität Dortmund')),
        ('Temporäre Daten', lazy_gettext('Temporäre Daten')),
    ], description=lazy_gettext('Choose one or more DataCatalog'))
    deskman = StringField(lazy_gettext('Deskman'), validators=[Optional()])
    apparent_dup = BooleanField(lazy_gettext('Apparent Duplicate'))
    license = SelectField(lazy_gettext('License'), choices=LICENSES)
    license_text = StringField(lazy_gettext('Copyright'), description=lazy_gettext("If you have granted the exclusive use of rights to a commercial service, please enter relevant information."))
    is_part_of = FieldList(FormField(IsPartOfForm), min_entries=1)

    #multiples = ('person', 'birth_date', 'death_date', 'keyword', 'person_uri', 'keyword_uri', 'role')
    #date_fields = ('issued', 'accessed', 'birth_date', 'death_date', 'created', 'changed')

    #admin_only = ['id', 'created', 'changed', 'owner', 'deskman','apparent_dup', 'gnd', 'orcid', 'viaf', 'isni', 'researcher_id', 'scopus_id', 'arxiv_id']
    # TODO id, created und changed waren auch für user nötig, da sonst das Speichern unmöglich war
    admin_only = ['owner', 'deskman','apparent_dup', 'gnd', 'orcid', 'viaf', 'isni', 'researcher_id', 'scopus_id', 'arxiv_id']
    #user_only = ['role']

class PrintedWorkForm(WorkForm):
    publisher = StringField(lazy_gettext('Publisher'), validators=[Optional()])
    publisher_place = StringField(lazy_gettext('Place of Publication'), validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    table_of_contents = FieldList(FormField(TableOfContentsForm), min_entries=1)
    #open_access = BooleanField(lazy_gettext('Open Access'))
    has_part = FieldList(FormField(HasPartForm), min_entries=1)

class SerialForm(PrintedWorkForm):
    ISSN = FieldList(StringField(lazy_gettext('ISSN'), widget=CustomTextInput(placeholder=lazy_gettext('e.g. 1932-6203'))), min_entries=1)
    ZDBID = StringField(lazy_gettext('ZDB-ID'), widget=CustomTextInput(placeholder=lazy_gettext('e.g. 2267670-3')))
    frequency = SelectField(lazy_gettext('Frequency'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Frequency')),
        ('completely_irregular', lazy_gettext('Completely Irregular')),
        ('annual', lazy_gettext('Annual')),
        ('quarterly', lazy_gettext('Quarterly')),
        ('semiannual', lazy_gettext('Semiannual')),
        ('monthly', lazy_gettext('Monthly')),
        ('bimonthly', lazy_gettext('Bimonthly')),
        ('three_times_a_year', lazy_gettext('Three Times a Year')),
        ('semimonthly', lazy_gettext('Semimonthly')),
        ('biennial', lazy_gettext('Biannial')),
        ('fifteen_issues_a_year', lazy_gettext('Fifteen Issues a Year')),
        ('continuously_updated', lazy_gettext('Continuously Updated')),
        ('daily', lazy_gettext('Daily')),
        ('semiweekly', lazy_gettext('Semiweekly')),
        ('three_times_a_week', lazy_gettext('Three Times a Week')),
        ('weekly', lazy_gettext('Weekly')),
        ('biweekly', lazy_gettext('Biweekly')),
        ('three_times_a_month', lazy_gettext('Three Times a Month')),
        ('triennial', lazy_gettext('Triennial')),
    ])
    external = BooleanField(lazy_gettext('External'))

    user_only = ['parent_title', 'parent_subtitle']
    admin_only = ['external']

class SeriesForm(SerialForm):
    number_of_volumes = StringField(lazy_gettext('Number of Volumes'), validators=[Optional()])

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement,
                       self.other_title, self.issued, self.number_of_volumes, self.publisher, self.publisher_place,
                       self.frequency, self.number_of_pages, self.medium, self.accessed, self.additions, self.note,
                       self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.ISSN, self.ZDBID, self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of], 'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created, self.changed, self.catalog,
                       self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class JournalForm(SerialForm):
    journal_abbreviation = FieldList(StringField(lazy_gettext('Journal Abbreviation'), widget=CustomTextInput(placeholder=lazy_gettext('The Abbreviated Title of the Journal'))), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.journal_abbreviation, self.language, self.title_supplement, self.other_title,
                       self.issued, self.publisher, self.publisher_place, self.frequency, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.ISSN, self.ZDBID, self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class NewspaperForm(JournalForm):
    journal_abbreviation = FieldList(StringField(lazy_gettext('Newspaper Abbreviation'), widget=CustomTextInput(
        placeholder=lazy_gettext('The Abbreviated Title of the Newspaper'))), min_entries=1)

class ArticleForm(WorkForm):
    parent_title = StringField(lazy_gettext('Parent Title'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('The Title of the Parent Reference')))
    parent_subtitle = StringField(lazy_gettext('Parent Subtitle'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('The Subtitle of the Parent Reference')))

    user_only = ['parent_title', 'parent_subtitle']

class ArticleJournalForm(ArticleForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('abstract', lazy_gettext('Abstract')),
        ('festschrift', lazy_gettext('Festschrift')),
        ('interview', lazy_gettext('Interview')),
        ('lexicon_article', lazy_gettext('Article in Lexicon')),
        ('meeting_abstract', lazy_gettext('Meeting Abstract')),
        ('poster', lazy_gettext('Poster')),
        ('poster_abstract', lazy_gettext('Poster Abstract')),
        ('sermon', lazy_gettext('Sermon')),
        ('review', lazy_gettext('Review')),
        ('introduction', lazy_gettext('Foreword')),
    ])
    publication_status = SelectField(lazy_gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select a Publication Status')),
        ('submitted', lazy_gettext('Submitted')),
        ('accepted', lazy_gettext('Accepted')),
        ('published', lazy_gettext('Published')),
        ('unpublished', lazy_gettext('Unpublished'))
    ], default='published')
    peer_reviewed = BooleanField(lazy_gettext('Peer Reviewed'))
    open_access = FormField(OpenAccessForm)
    DFG = BooleanField(lazy_gettext('DFG Funded'), description=Markup(lazy_gettext('APCs funded by the DFG and the RUB OA Fund (<a href="https://github.com/OpenAPC/openapc-de/tree/master/data/rub">OpenAPC</a>)')))
    key_publication = BooleanField(lazy_gettext('Key Publication'), description='A very important title to be included on a special publication list.')
    is_part_of = FieldList(FormField(ArticleRelationForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    event_name = StringField(lazy_gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(lazy_gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(lazy_gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    event_place = StringField(lazy_gettext('Location of the event'), validators=[Optional()])
    numbering = StringField(lazy_gettext('Numbering of the event'), validators=[Optional()])

    user_only = ['parent_title', 'parent_subtitle', 'key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.event_name, self.numbering, self.startdate_conference, self.enddate_conference, self.event_place], 'label': lazy_gettext('Event')},
            {'group': [self.parent_title, self.parent_subtitle, self.is_part_of],
             'label': lazy_gettext('Journal')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.open_access, self.DFG], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman, self.key_publication],
             'label': lazy_gettext('Administrative')},
        ]

class ArticleNewspaperForm(ArticleForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('review', lazy_gettext('Review')),
        ('interview', lazy_gettext('Interview')),
    ])
    is_part_of = FieldList(FormField(NewspaperRelationForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['parent_title', 'parent_subtitle', 'key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement,
                       self.other_title, self.issued, self.number_of_pages, self.medium, self.accessed,
                       self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.parent_title, self.parent_subtitle, self.is_part_of],
             'label': lazy_gettext('Newspaper')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                       ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class SpecialIssueForm(JournalForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('festschrift', lazy_gettext('Festschrift')),
    ])
    ISBN = FieldList(StringField(lazy_gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    ISMN = FieldList(StringField(lazy_gettext('ISMN'), validators=[Optional()]), min_entries=1)
    is_part_of = FieldList(FormField(SpecialIssueRelationForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.journal_abbreviation, self.title_supplement, self.other_title,
                       self.issued, self.publisher, self.publisher_place, self.frequency, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.ISSN, self.ISBN, self.ISMN, self.ZDBID, self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class ContainerForm(PrintedWorkForm):
    number_of_volumes = StringField(lazy_gettext('Number of Volumes'), validators=[Optional()])
    hbz_id = StringField(lazy_gettext('HBZ-ID'), validators=[Optional()])
    #hbz_id = FieldList(StringField(lazy_gettext('HBZ-ID'), validators=[Optional(), Isbn]), min_entries=1)
    open_access = FormField(OpenAccessForm)
    external = BooleanField(lazy_gettext('External'))
    is_part_of = FieldList(FormField(ContainerRelationForm), min_entries=1)
    ISBN = FieldList(StringField(lazy_gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    ISMN = FieldList(StringField(lazy_gettext('ISMN'), validators=[Optional()]), min_entries=1)

    admin_only = ['external']

class CollectionForm(ContainerForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('festschrift', lazy_gettext('Festschrift')),
    ])
    publication_status = SelectField(lazy_gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select a Publication Status')),
        ('forthcoming', lazy_gettext('Forthcoming')),
        ('published', lazy_gettext('Published')),
        ('unpublished', lazy_gettext('Unpublished'))
    ], default='published')

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.ISMN, self.hbz_id], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class ConferenceForm(CollectionForm):
    event_name = StringField(lazy_gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(lazy_gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(lazy_gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    place = StringField(lazy_gettext('Location of the event'), validators=[Optional()])
    numbering = StringField(lazy_gettext('Numbering of the event'), validators=[Optional()])
    peer_reviewed = BooleanField(lazy_gettext('Peer Reviewed'))

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.ISMN, self.hbz_id], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.event_name, self.numbering, self.startdate_conference, self.enddate_conference, self.place], 'label': lazy_gettext('Event')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.peer_reviewed, self.apparent_dup,
                       self.editorial_status, self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class EditionForm(CollectionForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('festschrift', lazy_gettext('Festschrift')),
        ('notated_music', lazy_gettext('Notated Music')),
    ])

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.ISMN, self.hbz_id], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class LegalCommentaryForm(CollectionForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('festschrift', lazy_gettext('Festschrift')),
        ('lexicon_article', lazy_gettext('Article in Lexicon')),
    ])
    standard_abbreviation = FieldList(StringField(lazy_gettext('Standard Abbreviation'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('The standard abbreviation of the legal commentary'))), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title, self.standard_abbreviation,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.ISMN, self.hbz_id], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class ChapterForm(WorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('abstract', lazy_gettext('Abstract')),
        ('afterword', lazy_gettext('Afterword')),
        ('festschrift', lazy_gettext('Festschrift')),
        ('sermon', lazy_gettext('Sermon')),
        ('interview', lazy_gettext('Interview')),
        ('introduction', lazy_gettext('Foreword')),
        ('lexicon_article', lazy_gettext('Article in Lexicon')),
        ('meeting_abstract', lazy_gettext('Meeting Abstract')),
        ('poster', lazy_gettext('Poster')),
        ('poster_abstract', lazy_gettext('Poster Abstract')),
        ('review', lazy_gettext('Review')),
    ])
    parent_title = StringField(lazy_gettext('Parent Title'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('The Title of the Parent Reference')))
    parent_subtitle = StringField(lazy_gettext('Parent Subtitle'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('The Subtitle of the Parent Reference')))
    peer_reviewed = BooleanField(lazy_gettext('Peer Reviewed'))
    open_access = FormField(OpenAccessForm)
    DFG = BooleanField(lazy_gettext('DFG Funded'), description=Markup(lazy_gettext(
        'APCs funded by the DFG and the RUB OA Fund (<a href="https://github.com/OpenAPC/openapc-de/tree/master/data/rub">OpenAPC</a>)')))
    is_part_of = FieldList(FormField(ChapterRelationForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')
    event_name = StringField(lazy_gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(lazy_gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(lazy_gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    event_place = StringField(lazy_gettext('Location of the event'), validators=[Optional()])
    numbering = StringField(lazy_gettext('Numbering of the event'), validators=[Optional()])

    user_only = ['parent_title', 'parent_subtitle', 'key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.event_name, self.numbering, self.startdate_conference, self.enddate_conference, self.event_place], 'label': lazy_gettext('Event')},
            {'group': [self.is_part_of, self.parent_title, self.parent_subtitle],
             'label': lazy_gettext('Part of')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.open_access, self.DFG], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.peer_reviewed, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class ChapterInLegalCommentaryForm(ChapterForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('lexicon_article', lazy_gettext('Article in Lexicon')),
    ])
    supplement = StringField('Supplement', validators=[Optional()])
    date_updated = StringField(lazy_gettext('Date updated'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("The last update of the legal text. If you don't know the month and/or day please use 01"))

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title, self.supplement,
                       self.issued, self.date_updated, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of, self.parent_title, self.parent_subtitle],
             'label': lazy_gettext('Part of')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.open_access, self.DFG], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.peer_reviewed, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]


class AudioVideoDocumentForm(PrintedWorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('image_database', lazy_gettext('Image Database')),
        ('dramatic_work', lazy_gettext('Dramatic Work')),
        ('interview', lazy_gettext('Interview')),
        ('sermon', lazy_gettext('Sermon')),
        ('audio_book', lazy_gettext('Audio Book')),
    ])
    ISBN = FieldList(StringField(lazy_gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    ISMN = FieldList(StringField(lazy_gettext('ISMN'), validators=[Optional()]), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.ISMN], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]


class InternetDocumentForm(WorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('abstract', lazy_gettext('Abstract')),
        ('sermon', lazy_gettext('Sermon')),
        ('interview', lazy_gettext('Interview')),
        ('lexicon_article', lazy_gettext('Article in Lexicon')),
        ('meeting_abstract', lazy_gettext('Meeting Abstract')),
        ('poster', lazy_gettext('Poster')),
        ('poster_abstract', lazy_gettext('Poster Abstract')),
        ('review', lazy_gettext('Review')),
    ])
    uri = FieldList(StringField(lazy_gettext('URL'), validators=[URL(), Optional()]), min_entries=1)
    last_update = StringField(lazy_gettext('Last update'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD'), description=lazy_gettext("If you don't know the month and/or day please use 01")))
    place = StringField(lazy_gettext('Place'), validators=[Optional()])
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    table_of_contents = FieldList(FormField(TableOfContentsForm), min_entries=1)
    event_name = StringField(lazy_gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(lazy_gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(lazy_gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    event_place = StringField(lazy_gettext('Location of the event'), validators=[Optional()])
    numbering = StringField(lazy_gettext('Numbering of the event'), validators=[Optional()])

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.place, self.number_of_pages, self.number, self.medium, self.accessed, self.last_update, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.event_name, self.numbering, self.startdate_conference, self.enddate_conference, self.event_place], 'label': lazy_gettext('Event')},
            {'group': [self.is_part_of], 'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label':lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]


class LectureForm(WorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('abstract', lazy_gettext('Abstract')),
        ('meeting_abstract', lazy_gettext('Meeting Abstract')),
    ])
    lecture_title = StringField(lazy_gettext('Lecture Series'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('The Title of the Lecture Series')))
    event_name = StringField(lazy_gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(lazy_gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(lazy_gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    place = StringField(lazy_gettext('Location of the event'), validators=[Optional()])
    numbering = StringField(lazy_gettext('Numbering of the event'), validators=[Optional()])
    open_access = FormField(OpenAccessForm)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title, self.lecture_title,
                       self.issued, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.event_name, self.numbering, self.startdate_conference, self.enddate_conference, self.place], 'label': lazy_gettext('Event')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class MonographForm(PrintedWorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('dissertation', lazy_gettext('Dissertation')),
        ('festschrift', lazy_gettext('Festschrift')),
        ('habilitation', lazy_gettext('Habilitation')),
        ('notated_music', lazy_gettext('Notated Music')),
    ])
    publication_status = SelectField(lazy_gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select a Publication Status')),
        ('forthcoming', lazy_gettext('Forthcoming')),
        ('published', lazy_gettext('Published')),
        ('unpublished', lazy_gettext('Unpublished'))
    ], default='published')
    ISBN = FieldList(StringField(lazy_gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    ISMN = FieldList(StringField(lazy_gettext('ISMN'), validators=[Optional()]), min_entries=1)
    hbz_id = StringField(lazy_gettext('HBZ-ID'), validators=[Optional()])
    #hbz_id = FieldList(StringField(lazy_gettext('HBZ-ID'), validators=[Optional(), Isbn]), min_entries=1)
    number_of_volumes = StringField('Number of Volumes', validators=[Optional()])
    open_access = FormField(OpenAccessForm)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    is_part_of = FieldList(FormField(MonographRelationForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.ISMN, self.hbz_id], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman, self.key_publication],
             'label': lazy_gettext('Administrative')},
        ]

class MultivolumeWorkForm(PrintedWorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        #('dissertation', lazy_gettext('Dissertation')),
        #('festschrift', lazy_gettext('Festschrift')),
        #('habilitation', lazy_gettext('Habilitation')),
        #('notated_music', lazy_gettext('Notated Music')),
        ('Monograph', lazy_gettext('Monograph')),
        ('Collection', lazy_gettext('Collection')),
        ('Conference', lazy_gettext('Conference')),
        ('SpecialIssue', lazy_gettext('Special Issue')),
    ])
    publication_status = SelectField(lazy_gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', lazy_gettext('Select a Publication Status')),
        ('forthcoming', lazy_gettext('Forthcoming')),
        ('published', lazy_gettext('Published')),
        ('unpublished', lazy_gettext('Unpublished'))
    ], default='published')
    ISBN = FieldList(StringField(lazy_gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    ISMN = FieldList(StringField(lazy_gettext('ISMN'), validators=[Optional()]), min_entries=1)
    hbz_id = StringField(lazy_gettext('HBZ-ID'), validators=[Optional()])
    #hbz_id = FieldList(StringField(lazy_gettext('HBZ-ID'), validators=[Optional(), Isbn]), min_entries=1)
    number_of_volumes = StringField('Number of Volumes', validators=[Optional()])
    open_access = FormField(OpenAccessForm)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    is_part_of = FieldList(FormField(MonographRelationForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')
    issued = FormField(IssueForm)

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.ISMN, self.hbz_id], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Volume')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman, self.key_publication],
             'label': lazy_gettext('Administrative')},
        ]


class ReportForm(WorkForm):
    place = StringField(lazy_gettext('Place'), validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    is_part_of = FieldList(FormField(OtherRelationForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.place, self.number_of_pages, self.number, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]


class ResearchDataForm(WorkForm):
    place = StringField(lazy_gettext('Place'), validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    is_part_of = FieldList(FormField(OtherRelationForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.place, self.number_of_pages, self.number, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]


class OtherForm(WorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('article_lexicon', lazy_gettext('Article in Lexicon')),
        ('festschrift', lazy_gettext('Festschrift')),
        ('sermon', lazy_gettext('Sermon')),
        ('lecture_notes', lazy_gettext('Lecture Notes')),
        ('poster', lazy_gettext('Poster')),
        ('poster_abstract', lazy_gettext('Poster Abstract')),
        ('expert_opinion', lazy_gettext('Expert Opinion')),
    ])
    place = StringField(lazy_gettext('Place'), validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    is_part_of = FieldList(FormField(OtherRelationForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')
    event_name = StringField(lazy_gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(lazy_gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(lazy_gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    event_place = StringField(lazy_gettext('Location of the event'), validators=[Optional()])
    numbering = StringField(lazy_gettext('Numbering of the event'), validators=[Optional()])

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.place, self.number_of_pages, self.number, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.event_name, self.numbering, self.startdate_conference, self.enddate_conference, self.event_place], 'label': lazy_gettext('Event')},
            {'group': [self.is_part_of], 'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class PatentForm(WorkForm):
    patent_number = StringField(lazy_gettext('Patent Number'), widget=CustomTextInput(placeholder=(lazy_gettext('The publication number for a patent, e.g. DE102004031250 A1'))))
    claims = StringField(lazy_gettext('Claims'), widget=CustomTextInput(placeholder=(lazy_gettext('e.g. Eur. Pat. Appl.'))))
    applicant = FieldList(StringField(lazy_gettext('Applicant'), widget=CustomTextInput(placeholder=(lazy_gettext('The name of the person applying for the patent')))), min_entries=1)
    date_application = StringField(lazy_gettext('Application Date'), widget=CustomTextInput(placeholder=(lazy_gettext('YYYY-MM-DD'))), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')])
    place_of_application = StringField(lazy_gettext('Application Country'), widget=CustomTextInput(placeholder=(lazy_gettext('e.g. Germany'))))
    application_number = StringField(lazy_gettext('Application Number'), widget=CustomTextInput(placeholder=(lazy_gettext('e.g. PCT/US2007/066814'))))
    place = StringField(lazy_gettext('Issue Country'), widget=CustomTextInput(placeholder=(lazy_gettext('e.g. Germany'))))
    bibliographic_ipc = StringField(lazy_gettext('Bibliographic IPC'), widget=CustomTextInput(placeholder=(lazy_gettext('Number according to the International Patent Classification, e. g. A63G 29/00'))))
    priority_date = FieldList(StringField(lazy_gettext('Priority Date'), widget=CustomTextInput(placeholder=(lazy_gettext('e.g. 60/744,997, 17.04.2006, US')))), min_entries=1)
    open_access = FormField(OpenAccessForm)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.claims, self.applicant, self.date_application, self.place_of_application, self.application_number, self.place, self.bibliographic_ipc, self.priority_date], 'label': lazy_gettext('Specific')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class PressReleaseForm(WorkForm):
    place = StringField(lazy_gettext('Place'), validators=[Optional()])
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class RadioTVProgramForm(WorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('interview', lazy_gettext('Interview')),
    ])
    issued = StringField(lazy_gettext('Broadcast Date'), validators=[DataRequired(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued,self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract], 'label':lazy_gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

#class ReportForm(OtherForm): pass

class SoftwareForm(PrintedWorkForm):
    title = StringField(lazy_gettext('Program Name'), validators=[DataRequired()], widget=CustomTextInput(placeholder=lazy_gettext('The Name of the Software')))
    edition = StringField('Version', validators=[Optional()])
    operating_system = FieldList(StringField('Operating System', validators=[Optional()]), min_entries=1)
    #storage_medium = FieldList(StringField('Storage Medium', validators=[Optional()]), min_entries=1)
    open_access = FormField(OpenAccessForm)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.publisher, self.publisher_place, self.number_of_pages, self.operating_system, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class StandardForm(PrintedWorkForm):
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    number_revision = StringField('Revision Number', validators=[Optional()])
    type_of_standard = StringField('Type of Standard', validators=[Optional()])
    ICS_notation = FieldList(StringField('ICS Notation', validators=[Optional()]), min_entries=1)
    open_access = FormField(OpenAccessForm)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    ISBN = FieldList(StringField(lazy_gettext('ISBN of the Collection'), validators=[Optional(), Isbn]), min_entries=1)

    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.edition, self.publisher, self.publisher_place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.number_revision, self.type_of_standard, self.ICS_notation], 'label': lazy_gettext('Specific')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.other_version], 'label': lazy_gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

class ThesisForm(WorkForm):
    subtype = SelectField(lazy_gettext('Subtype'), validators=[Optional()], choices=[
        ('', lazy_gettext('Select a Subtype')),
        ('bachelor_thesis', lazy_gettext('Bachelor Thesis')),
        ('diploma_thesis', lazy_gettext('Diploma Thesis')),
        ('dissertation', lazy_gettext('Dissertation')),        
        ('habilitation', lazy_gettext('Habilitation')),
        ('magisterarbeit', lazy_gettext('Magisterarbeit')),
        ('masters_thesis', lazy_gettext('Master`s Thesis')),
        ('first_state_examination', lazy_gettext('1st State Examination')),
        ('second_state_examination', lazy_gettext('2nd State Examination')),
    ])
    hbz_id = StringField(lazy_gettext('HBZ-ID'), validators=[Optional()])
    issued = StringField(lazy_gettext('Date issued'), validators=[Regexp('[12]\d{3}(?:-[01]\d)?(?:-[0123]\d)?')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    day_of_oral_exam = StringField(lazy_gettext('Day of the Oral Exam'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=lazy_gettext('YYYY-MM-DD')), description=lazy_gettext("If you don't know the month and/or day please use 01"))
    place = StringField(lazy_gettext('Location of Academic Institution'), validators=[Optional()], widget=CustomTextInput(placeholder=lazy_gettext('Where the thesis was submitted')))
    open_access = FormField(OpenAccessForm)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    key_publication = BooleanField(lazy_gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')
    table_of_contents = FieldList(FormField(TableOfContentsForm), min_entries=1)

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.language, self.title_supplement, self.other_title,
                       self.issued, self.day_of_oral_exam, self.place, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': lazy_gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.hbz_id], 'label': lazy_gettext('IDs')},
            {'group': [self.person], 'label': lazy_gettext('Person')},
            {'group': [self.corporation], 'label': lazy_gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': lazy_gettext('Part of')},
            {'group': [self.has_part], 'label': lazy_gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': lazy_gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label':lazy_gettext('Content')},
            {'group': [self.open_access], 'label': lazy_gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.group_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.catalog, self.owner, self.deskman],
             'label': lazy_gettext('Administrative')},
        ]

########################################################################
class UserForm(Form):
    loginid = StringField(Markup('<i class="fa fa-user"></i> LoginID'), validators=[DataRequired(),])
    password = PasswordField('Password')
    name = StringField('Name', description='First Name Last Name')
    email = StringField('Email', validators=[Email(),])
    role = SelectField('Role', choices=[
        ('', lazy_gettext('Select a Role')),
        ('user', 'User'),
        ('admin', 'Admin')], default='user')
    recaptcha = RecaptchaField()
    submit = SubmitField(Markup('<i class="fa fa-user-plus"></i> Register'))

class IDListForm(Form):
    ids = TextAreaField(lazy_gettext('List of IDs'), 'A List of one or more Identifiers such as ISBNs, DOIs, or PubMED IDs.')
    submit = SubmitField(lazy_gettext('Search'))

class FileUploadForm(Form):
    type = SelectField(lazy_gettext('Entity Type'), choices=[
        ('', lazy_gettext('Select a Type')),
        ('publication', 'Publication'),
        ('person', 'Person'),
        ('organisation', 'Organisation'),
        ('group', 'Working Group')
    ])
    #file = FileField(lazy_gettext('Publication Data'))
    file = FileField(lazy_gettext('Data'))
    submit = SubmitField()

class SimpleSearchForm(Form):
    query = StringField(lazy_gettext('Publication Search'))
    submit = SubmitField(lazy_gettext('Search'))