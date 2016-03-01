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
from flask.ext.babel import gettext
from flask.ext.wtf import Form, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, SelectMultipleField, FileField, HiddenField, FieldList, FormField, PasswordField
from wtforms.validators import DataRequired, UUID, URL, Email, Optional, Length, Regexp, ValidationError
from wtforms.widgets import TextInput
from re import IGNORECASE
import pyisbn

LICENSES = (
    ('', gettext('Select a License')),
    ('cc_zero', gettext('Creative Commons Zero - Public Domain')),
    ('cc_by', gettext('Creative Commons Attribution')),
    ('cc_by_sa', gettext('Creative Commons Attribution Share Alike')),
    ('cc_by_nd', gettext('Creative Commons Attribution No Derivatives'))
)

LANGUAGES = [
    ('', gettext('Select a Language')),
        ('eng', gettext('English')),
        ('ger', gettext('German')),
        ('fre', gettext('French')),
        ('rus', gettext('Russian')),
        ('spa', gettext('Spanish')),
        ('ita', gettext('Italian')),
        ('jap', gettext('Japanese')),
        ('lat', gettext('Latin')),
        ('zhn', gettext('Chinese')),
        ('dut', gettext('Dutch')),
        ('tur', gettext('Turkish')),
        ('por', gettext('Portuguese')),
        ('pol', gettext('Polish')),
        ('gre', gettext('Greek')),
        ('srp', gettext('Serbian')),
        ('cat', gettext('Catalan')),
        ('dan', gettext('Danish')),
        ('cze', gettext('Czech')),
        ('kor', gettext('Korean')),
        ('ara', gettext('Arabic')),
        ('hun', gettext('Hungarian')),
        ('swe', gettext('Swedish')),
        ('ukr', gettext(('Ukranian'))),
        ('heb', gettext('Hebrew')),
        ('hrv', gettext('Croatian')),
        ('slo', gettext('Slovak')),
        ('nor', gettext('Norwegian')),
        ('rum', gettext('Romanian')),
        ('fin', gettext('Finnish')),
        ('geo', gettext('Georgian')),
        ('bul', gettext('Bulgarian')),
        ('grc', gettext('Ancient Greek')),
        ('ind', gettext('Indonesian Language')),
        ('gmh', gettext('Middle High German')),
        ('mon', gettext('Mongolian Language')),
        ('peo', gettext('Persian')),
        ('alb', gettext('Albanian')),
        ('bos', gettext('Bosnian')),
    ]

USER_ROLES = [
    ('', gettext('Select a Role')),
    ('aut', gettext('Author')),
    ('aui', gettext('Author of Introduction')),
    ('ive', gettext('Interviewee')),
    ('ivr', gettext('Interviewer')),
    ('trl', gettext('Translator')),
    ('ths', gettext('Thesis Advisor')),
    ('ctb', gettext('Contributor')),
    ('edt', gettext('Editor')),
    ('inv', gettext('Inventor')),
    ('prg', gettext('Programmer')),
    ('drt', gettext('Director')),
    ('spk', gettext('Speaker')),
    ('cmp', gettext('Composer')),
]

ADMIN_ROLES = USER_ROLES[:]

ADMIN_ROLES.extend([
    ('abr', gettext('Abridger')),
    ('act', gettext('Actor')),
    ('aft', gettext('Author of Afterword')),
    ('arr', gettext('Arranger')),
    ('chr', gettext('Choreographer')),
    ('cmp', gettext('Composer')),
    ('cst', gettext('Costume Designer')),
    ('cwt', gettext('Commentator for written text')),
    ('elg', gettext('Electrician')),
    ('fmk', gettext('Filmmaker')),
    ('hnr', gettext('Honoree')),
    ('ill', gettext('Illustrator')),
    ('itr', gettext('Instrumentalist')),
    ('mod', gettext('Moderator')),
    ('mus', gettext('Musician')),
    ('org', gettext('Originator')),
    ('pdr', gettext('Project Director')),
    ('pht', gettext('Photographer')),
    ('pmn', gettext('Production Manager')),
    ('pro', gettext('Producer')),
    ('red', gettext('Redaktor')),
    ('sng', gettext('Singer')),
    ('std', gettext('Set designer')),
    ('stl', gettext('Storyteller')),
    ('tcd', gettext('Technical Director')),
    ])

USER_PUBTYPES = [
    ('', gettext('Select a Publication Type')),
    ('ArticleJournal', gettext('Article in Journal')),
    ('Chapter', gettext('Chapter in...')),
    ('Collection', gettext('Collection')),
    ('Monograph', gettext('Monograph')),
    ('Other', gettext('Other')),
    ('Patent', gettext('Patent')),
    ('Thesis', gettext('Thesis')),
]

ADMIN_PUBTYPES = USER_PUBTYPES[:]

ADMIN_PUBTYPES.extend([
    ('ArticleNewspaper', gettext('Article in Newspaper')),
    ('AudioBook', gettext('Audio Book')),
    ('AudioVideoDocument', gettext('Audio or Video Document')),
    ('ChapterInLegalCommentary', gettext('Chapter in a Legal Commentary')),
    ('ChapterInMonograph', gettext('Chapter in a Monograph')),
    ('Conference', gettext('Conference')),
    ('Edition', gettext('Edition')),
    ('InternetDocument', gettext('Internet Document')),
    ('Journal', gettext('Journal')),
    ('Lecture', gettext('Lecture')),
    ('LegalCommentary', gettext('Legal Commentary')),
    ('Newspaper', gettext('Newspaper')),
    ('PressRelease', gettext('Press Release')),
    ('RadioTVProgram', gettext('Radio or TV program')),
    ('Series', gettext('Series')),
    ('Software', gettext('Software')),
    ('SpecialIssue', gettext('Special Issue')),
    ('Standard', gettext('Standard')),
])

PROJECT_TYPES = [
    ('', gettext('Select a Project Type')),
    ('fp7', gettext('FP7')),
    ('h2020', gettext('Horizon 2020')),
    ('dfg', gettext('DFG')),
    ('mercur', gettext('Mercator Research Center Ruhr (MERCUR)')),
    ('other', gettext('Other')),
]

def Isbn(form, field):
    theisbn = pyisbn.Isbn(field.data)
    if theisbn.validate() == False:
        raise ValidationError(gettext('Not a valid ISBN!'))
    
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
    address = StringField(gettext('URI'), validators=[URL(), Optional()])
    label = StringField(gettext('Label'), validators=[Optional()])

class TableOfContentsForm(Form):
    address = StringField('URI', validators=[URL(), Optional()], widget=CustomTextInput(placeholder=gettext('e.g. http://d-nb.info/1035670232/04')))
    label = TextAreaField(gettext('Table of Contents'), validators=[Optional()])

class AbstractForm(URIForm):
    label = TextAreaField(gettext('Abstract'), validators=[Optional()])
    language = SelectField(gettext('Language'), validators=[Optional()], choices=LANGUAGES)
    shareable = BooleanField(gettext('Shareable'))

class PersonForm(Form):
    # salutation = SelectField(gettext('Salutation'), choices=[
    #     ('m', gettext('Mr.')),
    #     ('f', gettext('Mrs./Ms.')),
    # ])
    name = StringField(gettext('Name'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('Name, Given name')))
    #former_name = StringField(gettext('Former Name'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('Family name, given name')), description=gettext('If you have more than one former name, please separate them by semicolon.'))
    gnd = StringField(gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')])
    orcid = StringField(gettext('ORCID'), validators=[Optional()])
    role = SelectField(gettext('Role'))
    corresponding_author = BooleanField(gettext('Corresponding Author'), validators=[Optional()], description=gettext('The person handling the publication process'))

    admin_only = ['gnd']

class OpenAccessForm(Form):
    project_identifier = StringField(gettext('Project Identifier'), validators=[URL(), Optional()], widget=CustomTextInput(placeholder=gettext('e.g. http://purl.org/info:eu-repo/grantAgreement/EC/FP7/12345P')))
    project_type = SelectField('Project Type', choices=PROJECT_TYPES, validators=[Optional()])
    publication_version = SelectField('Publication Version', choices=[
        ('', gettext('Select a Publication Version')),
        ('accepted', gettext('Accepted')),
        ('draft', gettext('Draft')),
        ('forthcoming', gettext('Forthcoming')),
        ('legal', gettext('Legal')),
        ('non_peer_reviewed', gettext('Non Peer Reviewed')),
        ('peer-reviewed', gettext('Peer Reviewed')),
        ('published', gettext('Published')),
        ('rejected', gettext('Rejected')),
        ('unpublished', gettext('Unpublished')),
    ])
    fee = BooleanField(gettext('Author Pays'))
    #license_condition = StringField(gettext('License Condition'), validators=[URL(), Optional()], widget=CustomTextInput(placeholder=gettext('e.g. https://creativecommons.org/licenses/by/4.0/')))
    access_level = SelectField('Access Level', choices=[
        ('', gettext('Select an Access Level')),
        ('closed', gettext('Closed Access')),
        ('embargoed', gettext('Embargoed Access')),
        ('restricted', gettext('Restricted Access')),
        ('open', gettext('Open Access')),
    ])
    embargo_end_date = StringField(gettext('Embargo End Date'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    mime_type = SelectField('MIME-type', choices=[
        ('pdf', gettext('application/pdf')),
        ('msword', gettext('application/msword')),
        ('x-latex', gettext('application/x-latex')),
        ('plain', gettext('text/plain')),
    ])

class SEDForm(Form):
    start = StringField(gettext('Start Date'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    end = StringField(gettext('End Date'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')],
                        widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')),
                        description=gettext("If you don't know the month and/or day please use 01"))
    label = StringField(gettext('Label'), validators=[Optional()])
# TODO: Brauchen wir eine ID, und wenn ja, wohin?

class IDLForm(Form):
    id = StringField(gettext('ID'), validators=[Optional()])
    label = StringField(gettext('Label'), validators=[Optional()])

class AwardForm(SEDForm):
    pass

class CVForm(SEDForm):
    pass
class MembershipForm(SEDForm):
    pass

class ReviewerForm(SEDForm):
    ISSN = StringField(gettext('ISSN'), validators=[Optional()])
    ZDBID = StringField(gettext('ZDBID'), validators=[Optional()])

class EditorForm(ReviewerForm):
    start_volume = StringField(gettext('First Volume'), validators=[Optional()])
    end_volume = StringField(gettext('Last Volume'), validators=[Optional()])
    start_issue = StringField(gettext('First Issue'), validators=[Optional()])
    end_issue = StringField(gettext('Last Issue'), validators=[Optional()])

class ProjectForm(SEDForm):
    project_id = StringField(gettext('Project ID'), validators=[Optional()])
    project_type = SelectField('Project Type', choices=PROJECT_TYPES, validators=[Optional()])

class AffiliationForm(SEDForm):
    organisation_id = StringField(gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')])

class ThesisProfileForm(Form):
    title = StringField(gettext('Title'), validators=[Optional()])
    year = StringField(gettext('Year'), validators=[Optional()])
    thesis_type = SelectField(gettext('Type'), choices=[
        ('', gettext('Select a Thesis Type')),
        ('m', gettext('M.A. Thesis')),
        ('d', gettext('M.Sc. Thesis')),
        ('p', gettext('Doctoral Thesis')),
        ('h', gettext('Professorial Dissertation')),
    ])


class URLProfileForm(Form):
    url = FieldList(StringField(gettext('URL'), validators=[URL(), Optional()]), min_entries=1)
    label = SelectField(gettext('Label'), choices=[
        ('', gettext('Select a Label for the URL')),
        ('hp', gettext('Homepage')),
        ('rg', gettext('ResearchGate')),
        ('ri', gettext('ResearcherID')),
        ('an', gettext('AcademiaNet')),
        ('ae', gettext('Academia.edu')),
        ('wp', gettext('Wikipedia')),
        ('xi', gettext('Xing')),
        ('li', gettext('LinkedIn')),
        ('bl', gettext('Blog')),
        ('fb', gettext('Facebook')),
        ('tw', gettext('Twitter')),
        ('ic', gettext('identi.ca')),
        ('zt', gettext('Zotero')),
        ('md', gettext('Mendeley')),
        ('mi', gettext('Other')),
    ])

class PersonAdminForm(Form):
    salutation = SelectField(gettext('Salutation'), choices=[
        ('', gettext('Select a Salutation')),
        ('m', gettext('Mr.')),
        ('f', gettext('Mrs./Ms.')),
    ])
    name = StringField(gettext('Name'), widget=CustomTextInput(placeholder=gettext('Family Name, Given Name')))
    former_name = StringField(gettext('Former Name'), validators=[Optional()],
                              widget=CustomTextInput(placeholder=gettext('Family Name Only')),
                              description=gettext(
                                  'If you have more than one former names, please separate them by semicolon.'))
    email = StringField(gettext('E-Mail'), validators=[Optional()],
                        widget=CustomTextInput(placeholder=gettext('Your e-mail address')))
    account = FieldList(StringField(gettext('Account'), validators=[Optional(), Length(min=7, max=7)], widget=CustomTextInput(placeholder=gettext('Your 7-digit account number'))))
    dwid = StringField(gettext('Datawarehouse ID'), validators=[Optional()])
    affiliation = FieldList(FormField(AffiliationForm), min_entries=1)
    url = FieldList(FormField(URLProfileForm), min_entries=1)
    thesis = FieldList(FormField(ThesisProfileForm), min_entries=1)
    #image = FileField(gettext('Image'))

    membership = FieldList(FormField(MembershipForm), validators=[Optional()], min_entries=1)
    award = FieldList(FormField(AwardForm), validators=[Optional()], min_entries=1)
    cv = FieldList(FormField(CVForm), validators=[Optional()], min_entries=1)
    project = FieldList(FormField(ProjectForm), validators=[Optional()], min_entries=1)
    reviewer = FieldList(FormField(ReviewerForm), validators=[Optional()], min_entries=1)
    editor = FieldList(FormField(EditorForm), validators=[Optional()], min_entries=1)

    gnd = StringField(gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')], description=Markup(gettext('<a href="https://portal.d-nb.de/opac.htm?method=showOptions#top" target="_blank">Find in GND</a>')))
    orcid = StringField(gettext('ORCID'), validators=[Optional()], description=Markup(gettext('<a href="https://orcid.org/orcid-search/search" target="_blank">Find in ORCID</a>')))
    viaf = StringField(gettext('VIAF'), validators=[Optional()], description=Markup(gettext('<a href="http://www.viaf.org" target="_blank">Find in VIAF</a>')))
    isni = StringField(gettext('ISNI'), validators=[Optional()], description=Markup(gettext('<a href="http://www.isni.org" target="_blank">Find in ISNI</a>')))
    researcher_id = StringField(gettext('Researcher ID'), validators=[Optional()], description=Markup(gettext('<a href="http://www.researcherid.com/ViewProfileSearch.action" target="_blank">Find in Researcher ID</a>')))
    scopus_id = StringField(gettext('Scopus Author ID'), validators=[Optional()], description=Markup(gettext('<a href="https://www.scopus.com/search/form/authorFreeLookup.uri" target="_blank">Find in Scopus Author ID</a>')))
    arxiv_id = StringField(gettext('ArXiv Author ID'), validators=[Optional()], description=Markup(gettext('<a href="http://arxiv.org/find" target="_blank">Find in ArXiv Author ID</a>')))
    research_interest = FieldList(StringField(gettext('Research Interest')), validators=[Optional()], min_entries=1)

    status = SelectMultipleField(gettext('Status'), choices=[
        ('', gettext('Select a Status')),
        ('alumnus', gettext('Alumnus')),
        ('assistant_lecturer', gettext('Assistant Lecturer')),
        ('ranking', gettext('Relevant for Ranking')),
        ('external', gettext('External Staff')),
        ('manually_added', gettext('Manually added')),
        ('official', gettext('Official')),
        ('official_ns', gettext('Official, Non-Scientific')),
        ('research_school', gettext('Doctoral Candidate')),
        ('principal_investigator', gettext('Principal Investigator')),
        ('professor', gettext('Professor')),
        ('emeritus', gettext('Emeritus')),
        ('teaching_assistant', gettext('Teaching Assistant')),
        ('tech_admin', gettext('Technical and Administrative Staff')),
    ], description=gettext('Choose one or more Status'))

    note = TextAreaField(gettext('Note'), validators=[Optional()],
                             description=gettext('Commentary on the person'))
    data_supplied = StringField(gettext('Data Supplied'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')],
                              description=gettext('The date of the latest data delivery'),
                                widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')))

    created = StringField(gettext('Record Creation Date'), widget=CustomTextInput(readonly='readonly'))
    changed = StringField(gettext('Record Change Date'), widget=CustomTextInput(readonly='readonly'))
    id = StringField(gettext('ID'), widget=CustomTextInput(readonly='readonly'))
    owner = FieldList(StringField(gettext('Owner'), validators=[DataRequired()]), min_entries=1)
    deskman = StringField(gettext('Deskman'), validators=[Optional()], widget=CustomTextInput(admin_only='admin_only'))

    admin_only = ['status', 'data_supplied', 'dwid', 'account', 'id', 'created', 'changed', 'id', 'owner', 'deskman']

    def groups(self):
        yield [
            {'group': [self.salutation, self.name, self.former_name, self.account, self.email, self.dwid, self.status, self.research_interest, self.url], 'label': gettext('Basic')},
            {'group': [self.gnd, self.orcid, self.viaf, self.isni, self.researcher_id, self.scopus_id, self.arxiv_id], 'label': gettext('IDs')},
            {'group': [self.affiliation], 'label': gettext('Affiliation')},
            {'group': [self.cv], 'label': gettext('CV')},
            {'group': [self.thesis], 'label': gettext('Thesis')},
            {'group': [self.membership], 'label': gettext('Membership')},
            {'group': [self.award], 'label': gettext('Award')},
            {'group': [self.project], 'label': gettext('Project')},
            {'group': [self.reviewer], 'label': gettext('Reviewer')},
            {'group': [self.editor], 'label': gettext('Editor')},
            {'group': [self.id, self.created, self.changed, self.owner, self.deskman], 'label': gettext('Administrative')},
        ]

class DestatisForm(IDLForm):
    pass

class AccountForm(IDLForm):
    pass

class OrgaAdminForm(Form):
    pref_label = StringField(gettext('Label'))
    #alt_label = FieldList(StringField(gettext('Alternative Label')), min_entries=1)
    #account = StringField(gettext('Account'))
    id = StringField(gettext('Organisation ID'), description=gettext('An Organisation ID such as GND, ISNI, Ringgold or a URI'), validators=[DataRequired()])
    account = FieldList(FormField(AccountForm), min_entries=1)
    parent_id = StringField(gettext('Parent ID'))
    parent_label = StringField(gettext('Parent Label'))
    start_date = StringField(gettext('Start Date'))
    end_date = StringField(gettext('End Date'))
    correction_request = StringField(gettext('Correction Request'))
    owner = FieldList(StringField(gettext('Owner')), min_entries=1)
    created = StringField(gettext('Record Creation Date'), widget=CustomTextInput(readonly='readonly'))
    changed = StringField(gettext('Record Change Date'), widget=CustomTextInput(readonly='readonly'))
    destatis = FieldList(FormField(DestatisForm), min_entries=1)
    # child_id = StringField(gettext('Child ID'))
    # child_label = StringField(gettext('Child Label'))


class PersonProfileForm(PersonForm):
    image = FileField(gettext('Image'))
    url = FieldList(StringField('URL', validators=[URL(), Optional()]), min_entries=1)

class CorporationForm(Form):
    name = StringField(gettext('Name'))
    role = SelectField(gettext('Role'), choices=[
        ('', gettext('Select a Role')),
        ('edt', gettext('Editor')),
        ('his', gettext('Host institution')),
        ('dgg', gettext('Degree granting institution')),
        ('orm', gettext('Organizer')),
        ('pta', gettext('Patent applicant')),
        ('brd', gettext('Broadcaster')),
    ])

    gnd = StringField(gettext('GND'), validators=[Optional(), Regexp('(1|10)\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]')])
    viaf = StringField(gettext('VIAF'), validators=[Optional()])
    isni = StringField(gettext('ISNI'), validators=[Optional()])

    admin_only = ['gnd', 'viaf', 'isni']

class HasPartForm(Form):
    has_part = StringField(gettext('Has Part'))

class IsPartOfForm(Form):
    is_part_of = StringField(gettext('Is Part of'))

class OtherVersionForm(Form):
    other_version = StringField(gettext('Other Version'))

class ChapterRelationForm(IsPartOfForm):
    page_first = StringField(gettext('First Page'))
    page_last = StringField(gettext('Last Page'))

class ArticleRelationForm(IsPartOfForm):
    # For reasons of ordering we don't inherit from ChapterRelationForm here...
    volume = StringField(gettext('Volume'))
    issue = StringField(gettext('Issue'))
    page_first = StringField(gettext('First Page'))
    page_last = StringField(gettext('Last Page'))

class NewspaperRelationForm(IsPartOfForm):
    # For reasons of ordering we don't inherit from ChapterRelationForm here...
    volume = StringField(gettext('Volume'))
    issue = StringField(gettext('Edition'), widget=CustomTextInput(
        placeholder=gettext('Name or number of the edition that the article was published in')))
    page_first = StringField(gettext('First Page'))
    page_last = StringField(gettext('Last Page'))

class ContainerRelationForm(IsPartOfForm):
    volume = StringField(gettext('Volume'), validators=[Optional()])

class MonographRelationForm(ContainerRelationForm):
    pass

class TranslatedTitleForm(Form):
    translated_title = StringField(gettext('Translated Title'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The translated title of the work')))
    language = SelectField(gettext('Language'), validators=[Optional()], choices=LANGUAGES)

class WorkForm(Form):
    pubtype = SelectField(gettext('Type'), validators=[Optional()])
    title = StringField(gettext('Title'), validators=[DataRequired()], widget=CustomTextInput(placeholder=gettext('The title of the work')))
    subtitle = StringField(gettext('Subtitle'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The subtitle of the work')))
    title_supplement = StringField(gettext('Title Supplement'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('Additions to the title of the work')))
    title_translated = FieldList(FormField(TranslatedTitleForm), min_entries=1)
    person = FieldList(FormField(PersonForm), min_entries=1)
    corporation = FieldList(FormField(CorporationForm), min_entries=1)
    uri = FieldList(StringField(gettext('URI'), validators=[URL(), Optional()]), min_entries=1, widget=CustomTextInput(placeholder=gettext('A URI, URL, or URN')))
    DOI = StringField(gettext('DOI'), validators=[Optional(), Regexp('^10\.[0-9]{4,}(?:\.[0-9]+)*\/[a-z0-9\-\._]+', IGNORECASE)])
    PMID = StringField(gettext('PubMed ID'), widget=CustomTextInput(placeholder=(gettext('e.g. 15894097'))))
    WOSID = StringField(gettext('Web of Science ID'), widget=CustomTextInput(placeholder=(gettext('e.g. 000229082300022'))))
    language = FieldList(SelectField(gettext('Language'), validators=[Optional()], choices=LANGUAGES), min_entries=1)
    # issued = DateField(gettext('Publication Date'), validators=[Optional()])
    issued = StringField(gettext('Date'), validators=[DataRequired(), Regexp('[12]\d{3}(?:-[01]\d)?(?:-[0123]\d)?')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    accessed = StringField(gettext('Last Seen'), validators=[Optional(), Regexp('[12]\d{3}(?:-[01]\d)?(?:-[0123]\d)?')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    additions = StringField(gettext('Additions'), validators=[Optional()])
    keyword = FieldList(StringField(gettext('Keyword'), validators=[Optional()]), min_entries=1)
    keyword_temporal = FieldList(StringField(gettext('Temporal'), validators=[Optional()]), min_entries=1)
    keyword_geographic = FieldList(StringField(gettext('Geographic'), validators=[Optional()]), min_entries=1)
    swd_subject = FieldList(FormField(IDLForm), min_entries=1)
    ddc_subject = FieldList(FormField(IDLForm), min_entries=1)
    mesh_subject = FieldList(FormField(IDLForm), min_entries=1)
    stw_subject = FieldList(FormField(IDLForm), min_entries=1)
    lcsh_subject = FieldList(FormField(IDLForm), min_entries=1)
    thesoz_subject = FieldList(FormField(IDLForm), min_entries=1)

    abstract = FieldList(FormField(AbstractForm), validators=[Optional()])
    number_of_pages = StringField(gettext('Extent'), validators=[Optional()])
    medium= StringField(gettext('Medium'), validators=[Optional()])
    note = TextAreaField(gettext('Notes'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('Additional information about the work')))
    # id = HiddenField(gettext('UUID'), validators=[UUID(), Optional()])
    # created = HiddenField(gettext('Record Creation Date'))
    # changed = HiddenField(gettext('Record Change Date'))

    id = StringField(gettext('UUID'), validators=[UUID(), Optional()], widget=CustomTextInput(readonly='readonly', admin_only='admin_only'))
    affiliation_context = FieldList(StringField(gettext('Affiliation Context'), validators=[Optional()], widget=CustomTextInput(
        placeholder=gettext('The subject area this publication belongs to'))), min_entries=1)
    created = StringField(gettext('Record Creation Date'), widget=CustomTextInput(readonly='readonly', admin_only='admin_only'))
    changed = StringField(gettext('Record Change Date'), widget=CustomTextInput(readonly='readonly', admin_only='admin_only'))
    publication_status = SelectField(gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', gettext('Select a Publication Status')),
        ('published', gettext('Published'))
    ], default='published')
    editorial_status = SelectField(gettext('Editorial Status'), validators=[DataRequired()], choices=[
        ('', gettext('Select an Editorial Status')),
        ('new', gettext('New')),
        ('in_process', gettext('In Process')),
        ('processed', gettext('Processed')),
        ('final_editing', gettext('Final Editing')),
        ('finalized', gettext('Finalized')),
    ], default='new')
    owner = FieldList(StringField(gettext('Owner'), validators=[DataRequired()]), min_entries=1)
    deskman = StringField(gettext('Deskman'), validators=[Optional()])
    apparent_dup = BooleanField(gettext('Apparent Duplicate'))
    license = SelectField(gettext('License'), choices=LICENSES)
    license_text = StringField(gettext('Copyright'), description=gettext("If you have granted the exclusive use of rights to a commercial service, please enter relevant information."))
    is_part_of = FieldList(FormField(IsPartOfForm), min_entries=1)

    #multiples = ('person', 'birth_date', 'death_date', 'keyword', 'person_uri', 'keyword_uri', 'role')
    #date_fields = ('issued', 'accessed', 'birth_date', 'death_date', 'created', 'changed')

    admin_only = ['id', 'created', 'changed', 'owner', 'deskman','apparent_dup', 'gnd', 'orcid', 'viaf', 'isni', 'researcher_id', 'scopus_id', 'arxiv_id']
    #user_only = ['role']

class PrintedWorkForm(WorkForm):
    publisher = StringField(gettext('Publisher'), validators=[Optional()])
    publisher_place = StringField(gettext('Place of Publication'), validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    table_of_contents = FieldList(FormField(TableOfContentsForm))
    #open_access = BooleanField(gettext('Open Access'))
    has_part = FieldList(FormField(HasPartForm), min_entries=1)

class SerialForm(PrintedWorkForm):
    ISSN = FieldList(StringField(gettext('ISSN'), widget=CustomTextInput(placeholder=gettext('e.g. 1932-6203'))), min_entries=1)
    ZDBID = StringField(gettext('ZDB-ID'), widget=CustomTextInput(placeholder=gettext('e.g. 2267670-3')))
    frequency = SelectField(gettext('Frequency'), validators=[Optional()], choices=[
        ('', gettext('Select a Frequency')),
        ('completely_irregular', gettext('Completely Irregular')),
        ('annual', gettext('Annual')),
        ('quarterly', gettext('Quarterly')),
        ('semiannual', gettext('Semiannual')),
        ('monthly', gettext('Monthly')),
        ('bimonthly', gettext('Bimonthly')),
        ('three_times_a_year', gettext('Three Times a Year')),
        ('semimonthly', gettext('Semimonthly')),
        ('biennial', gettext('Biannial')),
        ('fifteen_issues_a_year', gettext('Fifteen Issues a Year')),
        ('continuously_updated', gettext('Continuously Updated')),
        ('daily', gettext('Daily')),
        ('semiweekly', gettext('Semiweekly')),
        ('three_times_a_week', gettext('Three Times a Week')),
        ('weekly', gettext('Weekly')),
        ('biweekly', gettext('Biweekly')),
        ('three_times_a_month', gettext('Three Times a Month')),
        ('triennial', gettext('Triennial')),
    ])
    external = BooleanField(gettext('External'))

    user_only = ['parent_title', 'parent_subtitle']
    admin_only = ['external']

class SeriesForm(SerialForm):
    number_of_volumes = StringField(gettext('Number of Volumes'), validators=[Optional()])

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.title_supplement,
                       self.title_translated, self.issued, self.number_of_volumes, self.publisher, self.publisher_place,
                       self.frequency, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note,
                       self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.ISSN, self.ZDBID, self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of], 'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.external, self.apparent_dup, self.editorial_status, self.created, self.changed,
                       self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class JournalForm(SerialForm):
    journal_abbreviation = FieldList(StringField(gettext('Journal Abbreviation'), widget=CustomTextInput(placeholder=gettext('The Abbreviated Title of the Journal'))), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.journal_abbreviation, self.title_supplement, self.title_translated,
                       self.issued, self.publisher, self.publisher_place, self.frequency, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.ISSN, self.ZDBID, self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.external, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class NewspaperForm(JournalForm):
    journal_abbreviation = FieldList(StringField(gettext('Newspaper Abbreviation'), widget=CustomTextInput(
        placeholder=gettext('The Abbreviated Title of the Newspaper'))), min_entries=1)

class ArticleForm(WorkForm):
    parent_title = StringField(gettext('Parent Title'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The Title of the Parent Reference')))
    parent_subtitle = StringField(gettext('Parent Subtitle'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The Subtitle of the Parent Reference')))

    user_only = ['parent_title', 'parent_subtitle']

class ArticleJournalForm(ArticleForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('abstract', gettext('Abstract')),
        ('festschrift', gettext('Festschrift')),
        ('interview', gettext('Interview')),
        ('lexicon_article', gettext('Article in Lexicon')),
        ('meeting_abstract', gettext('Meeting Abstract')),
        ('poster', gettext('Poster')),
        ('poster_abstract', gettext('Poster Abstract')),
        ('sermon', gettext('Sermon')),
        ('review', gettext('Review')),
        ('introduction', gettext('Introduction')),
    ])
    publication_status = SelectField(gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', gettext('Select a Publication Status')),
        ('submitted', gettext('Submitted')),
        ('accepted', gettext('Accepted')),
        ('published', gettext('Published')),
    ], default='published')
    peer_reviewed = BooleanField(gettext('Peer Reviewed'))
    open_access = FormField(OpenAccessForm)
    DFG = BooleanField(gettext('DFG Funded'), description=Markup(gettext('APCs funded by the DFG and the RUB OA Fund (<a href="https://github.com/OpenAPC/openapc-de/tree/master/data/rub">OpenAPC</a>)')))
    key_publication = BooleanField(gettext('Key Publication'), description='A very important title to be included on a special publication list.')
    is_part_of = FieldList(FormField(ArticleRelationForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    user_only = ['parent_title', 'parent_subtitle', 'key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.parent_title, self.parent_subtitle, self.is_part_of],
             'label': gettext('Journal')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.open_access, self.DFG], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman, self.key_publication],
             'label': gettext('Administrative')},
        ]

class ArticleNewspaperForm(ArticleForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('review', gettext('Review')),
    ])
    is_part_of = FieldList(FormField(NewspaperRelationForm), min_entries=1)
    key_publication = BooleanField(gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['parent_title', 'parent_subtitle', 'key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement,
                       self.title_translated, self.issued, self.language, self.number_of_pages, self.medium, self.accessed,
                       self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.parent_title, self.parent_subtitle, self.is_part_of],
             'label': gettext('Newspaper')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                       ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class SpecialIssueForm(JournalForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('festschrift', gettext('Festschrift')),
    ])

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.journal_abbreviation, self.title_supplement, self.title_translated,
                       self.issued, self.publisher, self.publisher_place, self.frequency, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.ISSN, self.ZDBID, self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.external, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class ContainerForm(PrintedWorkForm):
    number_of_volumes = StringField(gettext('Number of Volumes'), validators=[Optional()])
    hbz_id = StringField(gettext('HBZ-ID'), validators=[Optional()])
    open_access = FormField(OpenAccessForm)
    external = BooleanField(gettext('External'))
    is_part_of = FieldList(FormField(ContainerRelationForm), min_entries=1)
    ISBN = FieldList(StringField(gettext('ISBN of the Collection'), validators=[Optional(), Isbn]), min_entries=1)

    admin_only = ['external']

class CollectionForm(ContainerForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('festschrift', gettext('Festschrift')),
    ])
    publication_status = SelectField(gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', gettext('Select a Publication Status')),
        ('forthcoming', gettext('Forthcoming')),
        ('published', gettext('Published')),
    ], default='published')

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.hbz_id], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.external, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class ConferenceForm(CollectionForm):
    event_name = StringField(gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    place = StringField(gettext('Location of the event'), validators=[Optional()])
    peer_reviewed = BooleanField(gettext('Peer Reviewed'))

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.hbz_id], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.event_name, self.startdate_conference, self.enddate_conference, self.place], 'label': gettext('Event')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.peer_reviewed, self.external, self.apparent_dup,
                       self.editorial_status, self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class EditionForm(CollectionForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('festschrift', gettext('Festschrift')),
        ('notated_music', gettext('Notated Music')),
    ])

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.hbz_id], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.external, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class LegalCommentaryForm(CollectionForm):
    standard_abbreviation = FieldList(StringField(gettext('Standard Abbreviation'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The standard abbreviation of the legal commentary'))), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated, self.standard_abbreviation,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.hbz_id], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.external, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class ChapterForm(WorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('abstract', gettext('Abstract')),
        ('afterword', gettext('Afterword')),
        ('festschrift', gettext('Festschrift')),
        ('sermon', gettext('Sermon')),
        ('interview', gettext('Interview')),
        ('introduction', gettext('Introduction')),
        ('lexicon_article', gettext('Article in Lexicon')),
        ('meeting_abstract', gettext('Meeting Abstract')),
        ('poster', gettext('Poster')),
        ('poster_abstract', gettext('Poster Abstract')),
        ('review', gettext('Review')),
    ])
    parent_title = StringField(gettext('Parent Title'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The Title of the Parent Reference')))
    parent_subtitle = StringField(gettext('Parent Subtitle'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The Subtitle of the Parent Reference')))
    peer_reviewed = BooleanField(gettext('Peer Reviewed'))
    open_access = FormField(OpenAccessForm)
    DFG = BooleanField(gettext('DFG Funded'), description=Markup(gettext(
        'APCs funded by the DFG and the RUB OA Fund (<a href="https://github.com/OpenAPC/openapc-de/tree/master/data/rub">OpenAPC</a>)')))
    is_part_of = FieldList(FormField(ChapterRelationForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    key_publication = BooleanField(gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['parent_title', 'parent_subtitle', 'key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of, self.parent_title, self.parent_subtitle],
             'label': gettext('Part of')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.open_access, self.DFG], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.peer_reviewed, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class ChapterInLegalCommentaryForm(ChapterForm):
    supplement = StringField('Supplement', validators=[Optional()])
    date_updated = StringField(gettext('Date updated'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("The last update of the legal text. If you don't know the month and/or day please use 01"))

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated, self.supplement,
                       self.issued, self.date_updated, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of, self.parent_title, self.parent_subtitle],
             'label': gettext('Part of')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.open_access, self.DFG], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.peer_reviewed, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class ChapterInMonographForm(ChapterForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('foreword', gettext('Foreword')),
        ('afterword', gettext('Afterword')),
    ])

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of, self.parent_title, self.parent_subtitle],
             'label': gettext('Part of')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.open_access, self.DFG], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.peer_reviewed, self.apparent_dup, self.editorial_status,
                       self.created, self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]
class AudioBookForm(PrintedWorkForm):
    ISBN = FieldList(StringField(gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class AudioVideoDocumentForm(PrintedWorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('image_database', gettext('Image Database')),
        ('dramatic_work', gettext('Dramatic Work')),
        ('interview', gettext('Interview')),
    ])
    ISBN = FieldList(StringField(gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class InternetDocumentForm(WorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('abstract', gettext('Abstract')),
        ('sermon', gettext('Sermon')),
        ('interview', gettext('Interview')),
        ('lexicon_article', gettext('Article in Lexicon')),
        ('meeting_abstract', gettext('Meeting Abstract')),
        ('poster', gettext('Poster')),
        ('poster_abstract', gettext('Poster Abstract')),
        ('review', gettext('Review')),
    ])
    uri = FieldList(StringField(gettext('URL'), validators=[URL(), Optional()]), min_entries=1)
    last_update = StringField(gettext('Last update'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD'), description=gettext("If you don't know the month and/or day please use 01")))
    place = StringField(gettext('Place'), validators=[Optional()])
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.place, self.language, self.number_of_pages, self.number, self.medium, self.accessed, self.last_update, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class LectureForm(WorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('abstract', gettext('Abstract')),
        ('meeting_abstract', gettext('Meeting Abstract')),
    ])
    lecture_title = StringField(gettext('Lecture Series'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('The Title of the Lecture Series')))
    event_name = StringField(gettext('Name of the event'), validators=[Optional()])
    startdate_conference = StringField(gettext('First day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    enddate_conference = StringField(gettext('Last day of the event'), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    place = StringField(gettext('Location of the event'), validators=[Optional()])
    open_access = FormField(OpenAccessForm)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated, self.lecture_title,
                       self.issued, self.place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.event_name, self.startdate_conference, self.enddate_conference, self.place], 'label': gettext('Event')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class MonographForm(PrintedWorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('dissertation', gettext('Dissertation')),
        ('festschrift', gettext('Festschrift')),
        ('habilitation', gettext('Habilitation')),
        ('notated_music', gettext('Notated Music')),
    ])
    publication_status = SelectField(gettext('Publication Status'), validators=[DataRequired()], choices=[
        ('', gettext('Select a Publication Status')),
        ('forthcoming', gettext('Forthcoming')),
        ('published', gettext('Published')),
    ], default='published')
    ISBN = FieldList(StringField(gettext('ISBN'), validators=[Optional(), Isbn]), min_entries=1)
    hbz_id = StringField(gettext('HBZ-ID'), validators=[Optional()])
    number_of_volumes = StringField('Number of Volumes', validators=[Optional()])
    open_access = FormField(OpenAccessForm)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    is_part_of = FieldList(FormField(MonographRelationForm), min_entries=1)
    key_publication = BooleanField(gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.number_of_volumes, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN, self.hbz_id], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class OtherForm(WorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('article_lexicon', gettext('Article in Lexicon')),
        ('festschrift', gettext('Festschrift')),
        ('sermon', gettext('Sermon')),
        ('lecture_notes', gettext('Lecture Notes')),
        ('poster', gettext('Poster')),
        ('poster_abstract', gettext('Poster Abstract')),
        ('report', gettext('Report')),
    ])
    place = StringField(gettext('Place'), validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    key_publication = BooleanField(gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.place, self.language, self.number_of_pages, self.number, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class PatentForm(WorkForm):
    patent_number = StringField(gettext('Patent Number'), widget=CustomTextInput(placeholder=(gettext('The publication number for a patent, e.g. DE102004031250 A1'))))
    claims = StringField(gettext('Claims'), widget=CustomTextInput(placeholder=(gettext('e.g. Eur. Pat. Appl.'))))
    applicant = FieldList(StringField(gettext('Applicant'), widget=CustomTextInput(placeholder=(gettext('The name of the person applying for the patent')))), min_entries=1)
    date_application = StringField(gettext('Application Date'), widget=CustomTextInput(placeholder=(gettext('YYYY-MM-DD'))), validators=[Optional(), Regexp('[12]\d{3}-[01]\d-[0123]\d')])
    place_of_application = StringField(gettext('Application Country'), widget=CustomTextInput(placeholder=(gettext('e.g. Germany'))))
    application_number = StringField(gettext('Application Number'), widget=CustomTextInput(placeholder=(gettext('e.g. PCT/US2007/066814'))))
    place = StringField(gettext('Issue Country'), widget=CustomTextInput(placeholder=(gettext('e.g. Germany'))))
    bibliographic_ipc = StringField(gettext('Bibliographic IPC'), widget=CustomTextInput(placeholder=(gettext('Number according to the International Patent Classification, e. g. A63G 29/00'))))
    priority_date = FieldList(StringField(gettext('Priority Date'), widget=CustomTextInput(placeholder=(gettext('e.g. 60/744,997, 17.04.2006, US')))), min_entries=1)
    open_access = FormField(OpenAccessForm)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    key_publication = BooleanField(gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.claims, self.applicant, self.date_application, self.place_of_application, self.application_number, self.place, self.bibliographic_ipc, self.priority_date], 'label': gettext('Specific')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class PressReleaseForm(WorkForm):
    place = StringField(gettext('Place'), validators=[Optional()])
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class RadioTVProgramForm(WorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('interview', gettext('Interview')),
    ])
    issued = StringField(gettext('Broadcast Date'), validators=[DataRequired(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

#class ReportForm(OtherForm): pass

class SoftwareForm(PrintedWorkForm):
    title = StringField(gettext('Program Name'), validators=[DataRequired()], widget=CustomTextInput(placeholder=gettext('The Name of the Software')))
    edition = StringField('Version', validators=[Optional()])
    operating_system = FieldList(StringField('Operating System', validators=[Optional()]), min_entries=1)
    #storage_medium = FieldList(StringField('Storage Medium', validators=[Optional()]), min_entries=1)
    open_access = FormField(OpenAccessForm)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.operating_system, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class StandardForm(PrintedWorkForm):
    number = FieldList(StringField('Number', validators=[Optional()]), min_entries=1)
    number_revision = StringField('Revision Number', validators=[Optional()])
    type_of_standard = StringField('Type of Standard', validators=[Optional()])
    ICS_notation = FieldList(StringField('ICS Notation', validators=[Optional()]), min_entries=1)
    open_access = FormField(OpenAccessForm)
    other_version = FieldList(FormField(OtherVersionForm), min_entries=1)
    ISBN = FieldList(StringField(gettext('ISBN of the Collection'), validators=[Optional(), Isbn]), min_entries=1)

    key_publication = BooleanField(gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.edition, self.publisher, self.publisher_place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.number_revision, self.type_of_standard, self.ICS_notation], 'label': gettext('Specific')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID, self.ISBN], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.other_version], 'label': gettext('Other Version')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract, self.table_of_contents], 'label': gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

class ThesisForm(WorkForm):
    subtype = SelectField(gettext('Subtype'), validators=[Optional()], choices=[
        ('', gettext('Select a Subtype')),
        ('bachelor_thesis', gettext('Bachelor Thesis')),
        ('diploma_thesis', gettext('Diploma Thesis')),
        ('dissertation', gettext('Dissertation')),        
        ('habilitation', gettext('Habilitation')),
        ('magisterarbeit', gettext('Magisterarbeit')),
        ('masters_thesis', gettext('Master`s Thesis')),
        ('first_state_examination', gettext('1st State Examination')),
        ('second_state_examination', gettext('2nd State Examination')),
    ])
    issued = StringField(gettext('Day of the Oral Exam'), validators=[DataRequired(), Regexp('[12]\d{3}-[01]\d-[0123]\d')], widget=CustomTextInput(placeholder=gettext('YYYY-MM-DD')), description=gettext("If you don't know the month and/or day please use 01"))
    place = StringField(gettext('Location of Academic Institution'), validators=[Optional()], widget=CustomTextInput(placeholder=gettext('Where the thesis was submitted')))
    open_access = FormField(OpenAccessForm)
    has_part = FieldList(FormField(HasPartForm), min_entries=1)
    key_publication = BooleanField(gettext('Key Publication'),
                                   description='A very important title to be included on a special publication list.')

    user_only = ['key_publication']

    def groups(self):
        yield [
            {'group': [self.pubtype, self.subtype, self.publication_status, self.title, self.subtitle, self.title_supplement, self.title_translated,
                       self.issued, self.place, self.language, self.number_of_pages, self.medium, self.accessed, self.additions, self.note, self.license, self.license_text
                       ],
             'label': gettext('Basic')},
            {'group': [self.uri, self.DOI, self.PMID, self.WOSID], 'label': gettext('ID')},
            {'group': [self.person], 'label': gettext('Person')},
            {'group': [self.corporation], 'label': gettext('Corporation')},
            {'group': [self.is_part_of],
             'label': gettext('Part of')},
            {'group': [self.has_part], 'label': gettext('Chapter')},
            {'group': [self.keyword, self.keyword_temporal, self.keyword_geographic, self.swd_subject, self.ddc_subject,
                       self.mesh_subject, self.stw_subject, self.lcsh_subject, self.thesoz_subject
                        ],
             'label': gettext('Keyword')},
            {'group': [self.abstract], 'label':gettext('Content')},
            {'group': [self.open_access], 'label': gettext('Open Access')},
            {'group': [self.id, self.affiliation_context, self.apparent_dup, self.editorial_status, self.created,
                       self.changed, self.owner, self.deskman],
             'label': gettext('Administrative')},
        ]

########################################################################
class UserForm(Form):
    loginid = StringField(Markup('<i class="fa fa-user"></i> LoginID'), validators=[DataRequired(),])
    password = PasswordField('Password')
    name = StringField('Name', description='First Name Last Name')
    email = StringField('Email', validators=[Email(),])
    role = SelectField('Role', choices=[
        ('', gettext('Select a Role')),
        ('user', 'User'),
        ('admin', 'Admin')], default='user')
    recaptcha = RecaptchaField()
    submit = SubmitField(Markup('<i class="fa fa-user-plus"></i> Register'))

class IDListForm(Form):
    ids = TextAreaField('List of IDs', 'A List of one or more Identifiers such as ISBNs, DOIs, or PubMED IDs.')
    submit = SubmitField('Search')

class FileUploadForm(Form):
    file = FileField(gettext('Publication Data'))

class SimpleSearchForm(Form):
    query = StringField('Publication Search')
    submit = SubmitField('Search')