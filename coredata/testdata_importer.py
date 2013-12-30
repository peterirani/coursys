# do the import with fake data for development
# suggestion execution:
#   rm db.sqlite; echo "no" | ./manage.py syncdb && ./manage.py migrate && python coredata/testdata_importer.py

import sys, os
sys.path.append(".")
#sys.path.append("courses")
os.environ['DJANGO_SETTINGS_MODULE'] = 'courses.settings'

import random, socket, datetime, itertools
from django.core import serializers
from importer import give_sysadmin, create_semesters, import_offerings, import_offering_members, combine_sections, past_cutoff, update_amaint_userids, fix_emplid
from demodata_importer import fake_emplid, fake_emplids, create_classes
from coredata.models import Member, Person, CourseOffering, Course, Semester, SemesterWeek, MeetingTime, Role, Unit, CAMPUSES, ComputingAccount
from dashboard.models import UserConfig
from grades.models import Activity, NumericActivity, LetterActivity, CalNumericActivity, CalLetterActivity
from submission.models.base import SubmissionComponent
from submission.models.code import CodeComponent
from submission.models.pdf import PDFComponent
#from planning.models import SemesterPlan, PlannedOffering, PlanningCourse, TeachingEquivalent, TeachingCapability, TeachingIntention
from marking.models import ActivityComponent
from groups.models import Group, GroupMember
from grad.models import GradProgram, GradStudent, GradStatus, LetterTemplate, ScholarshipType, \
        Supervisor, GradRequirement, GradFlag
from grad.forms import possible_supervisor_people
from discipline.models import DisciplineTemplate
from ta.models import CourseDescription, TAPosting, TAApplication, CoursePreference, TAContract, TACourse, TAKEN_CHOICES, EXPER_CHOICES
from ra.models import Account, RAAppointment, Project, SemesterConfig, HIRING_CATEGORY_CHOICES, HIRING_CATEGORY_DISABLED
from onlineforms.models import FormGroup, FormGroupMember, Form, Sheet, Field, FormSubmission, SheetSubmission, FieldSubmission
from courselib.testing import TEST_COURSE_SLUG

FULL_TEST_DATA = TEST_COURSE_SLUG
NEEDED_SEMESTERS = [1111,1114,1117, 1121,1124,1127, 1131,1134,1137, 1141,1144,1147, 1151,1154,1157] # at least two years in past and one in future
TEST_SEMESTER = 1141

def get_combined():
    combined_sections = [
        ]
    return combined_sections


def test_class_1(slug):
    """
    main test course: 20 students, TA, some assignments
    """
    crs = CourseOffering.objects.get(slug=slug)
    
    crs.set_labtut(True)
    crs.set_url("http://www.cs.sfu.ca/CC/165/common/")
    crs.set_taemail("cmpt-165-contact@sfu.ca")
    crs.save()
    for i in range(20):
        lab = "D1%02i" % (random.randint(1,4))
        p = Person.objects.get(userid="0aaa%i"%(i))
        if Member.objects.filter(person=p, offering=crs, role="STUD"):
            # randomly added by other student-adder: skip
            continue

        m = Member(person=p, offering=crs, role="STUD", credits=3, career="UGRD", added_reason="AUTO",
                labtut_section=lab)
        m.save()
    
    if not Member.objects.filter(person__userid='ggbaker', offering=crs, role='INST'):
        Member(person=Person.objects.get(userid='ggbaker'), offering=crs, role='INST').save()
    
    # create a TA
    p = Person(emplid=fake_emplid(), userid="0grad1", last_name="Gradstudent", first_name="Douglas", middle_name="", pref_first_name="Doug")
    p.save()
    m = Member(person=p, offering=crs, role="TA", credits=0, career="NONS", added_reason="AUTO",
            labtut_section=None)
    m.save()
    
    
    # create example activities
    crs.activity_set.all().update(deleted=True)
    a1 = NumericActivity(offering=crs, name="Assignment 1", short_name="A1", status="RLS",
        due_date=crs.semester.start + datetime.timedelta(days=60), percent=10, group=False,
        max_grade=10, position=1)
    a1.set_url("http://www.cs.sfu.ca/CC/165/common/a1")
    a1.save()
    a2 = NumericActivity(offering=crs, name="Assignment 2", short_name="A2", status="URLS",
        due_date=crs.semester.start + datetime.timedelta(days=70), percent=10, group=True,
        max_grade=20, position=2)
    a2.save()
    pr = LetterActivity(offering=crs, name="Project", short_name="Proj", status="URLS",
        due_date=crs.semester.start + datetime.timedelta(days=80), percent=40, group=True, position=3)
    pr.save()
    re = LetterActivity(offering=crs, name="Report", short_name="Rep", status="URLS",
        due_date=crs.semester.start + datetime.timedelta(days=81), percent=10, group=False, position=4)
    re.save()
    ex = NumericActivity(offering=crs, name="Final Exam", short_name="Exam", status="URLS",
        due_date=None, percent=30, group=False, max_grade=90, position=5)
    ex.save()
    to = CalNumericActivity(offering=crs, name="Final Percent", short_name="Perc", status="INVI",
        due_date=None, percent=0, group=False, max_grade=100, formula="[[activitytotal]]", position=6)
    to.save()
    to = CalLetterActivity(offering=crs, name="Letter Grade", short_name="Letter", status="INVI",
        due_date=None, percent=0, group=False, numeric_activity=to, position=6)
    to.save()
    
    # make A1 submittable and markable
    s = CodeComponent(activity=a1, title="Code File", description="The code you're submitting.",
        allowed=".py,.java")
    s.save()
    s = PDFComponent(activity=a1, title="Report", description="Report on what you did.",
        specified_filename="report.pdf")
    s.save()
    
    m = ActivityComponent(numeric_activity=a1, max_mark=5, title="Part 1", description="Part 1 was done well and seems to work.", position=1)
    m.save()
    m = ActivityComponent(numeric_activity=a1, max_mark=5, title="Part 2", description="Part 2 was done well and seems to work.", position=2)
    m.save()
    
    # create some groups
    g = Group(name="SomeGroup", courseoffering=crs, manager=Member.objects.get(offering=crs, person__userid="0aaa0", role='STUD'))
    g.save()
    for userid in ['0aaa0', '0aaa1', '0aaa5', '0aaa10']:
        gm = GroupMember(group=g, student=Member.objects.get(offering=crs, person__userid=userid), confirmed=True, activity=a2)
        gm.save()
    
    g = Group(name="AnotherGroup", courseoffering=crs, manager=Member.objects.get(offering=crs, person__userid="0aaa4"))
    g.save()
    for userid in ['0aaa4', '0aaa6', '0aaa7', '0aaa14']:
        gm = GroupMember(group=g, student=Member.objects.get(offering=crs, person__userid=userid), confirmed=True, activity=a2)
        gm.save()
        gm = GroupMember(group=g, student=Member.objects.get(offering=crs, person__userid=userid), confirmed=True, activity=pr)
        gm.save()



def create_test_classes():
    # full test data for this course
    test_class_1(FULL_TEST_DATA)
    # minimal test data for this course
    #test_class_2(MIN_TEST_DATA)


def create_others():
    """
    Create other users for the test data set
    """
    p = Person(emplid=fake_emplid(), first_name="Susan", last_name="Kindersley", pref_first_name="sumo", userid="sumo")
    p.save()
    r = Role(person=p, role="GRAD", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    p = Person(emplid=fake_emplid(), first_name="Danyu", last_name="Zhao", pref_first_name="Danyu", userid="dzhao")
    p.save()
    r = Role(person=p, role="ADVS", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=Person.objects.get(userid='dixon'), role="PLAN", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=Person.objects.get(userid='ggbaker'), role="FAC", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=Person.objects.get(userid='dixon'), role="FAC", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=Person.objects.get(userid='diana'), role="FAC", unit=Unit.objects.get(slug='cmpt'))
    r.save()

    p = Person.objects.get(userid='ggbaker')
    r = Role(person=p, role="GRAD", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=p, role="ADMN", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=p, role="TAAD", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=p, role="FUND", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=Person.objects.get(userid='popowich'), role="GRPD", unit=Unit.objects.get(slug='cmpt'))
    r.save()


def create_grads():
    """
    Put the grad students created before into GradStudent records.
    """
    gp = GradProgram(unit=Unit.objects.get(slug='cmpt'), label='MSc Project', description='MSc Project option')
    gp.save()
    req = GradRequirement(program=gp, description='Formed Committee')
    req.save()
    gp = GradProgram(unit=Unit.objects.get(slug='cmpt'), label='MSc Thesis', description='MSc Thesis option')
    gp.save()
    req = GradRequirement(program=gp, description='Formed Committee')
    req.save()
    gp = GradProgram(unit=Unit.objects.get(slug='cmpt'), label='PhD', description='PhD')
    gp.save()
    req = GradRequirement(program=gp, description='Defended Thesis')
    req.save()
    req = GradRequirement(program=gp, description='Formed Committee')
    req.save()
    gp = GradProgram(unit=Unit.objects.get(slug='ensc'), label='MEng', description='Masters in Engineering')
    gp.save()
    gp = GradProgram(unit=Unit.objects.get(slug='ensc'), label='PhD', description='PhD')
    gp.save()
    st = ScholarshipType(unit=Unit.objects.get(slug='cmpt'), name="Some Scholarship")
    st.save()
    gf = GradFlag(unit=Unit.objects.get(slug='cmpt'), label='Special Specialist Program')
    gf.save()
    
    programs = list(GradProgram.objects.all())
    supervisors = list(set([m.person for m in Member.objects.filter(offering__owner__slug='cmpt', role='INST')]))
    for p in Person.objects.filter(userid__endswith='grad'):
        gp = random.choice(programs)
        campus = random.choice(list(CAMPUSES))
        gs = GradStudent(person=p, program=gp, campus=campus)
        gs.save()

        startsem = random.choice(list(Semester.objects.filter(name__lt=Semester.current().name)))
        st = GradStatus(student=gs, status='COMP', start=startsem)
        st.save()
        st = GradStatus(student=gs, status=random.choice(['ACTI', 'ACTI', 'LEAV']), start=startsem.next_semester())
        st.save()
        if random.random() > 0.5:
            st = GradStatus(student=gs, status=random.choice(['GRAD', 'GRAD', 'WIDR']), start=startsem.next_semester().next_semester().next_semester())
            st.save()
        
        if random.random() > 0.25:
            sup = Supervisor(student=gs, supervisor=random.choice(supervisors), supervisor_type='SEN')
            sup.save()
            sup = Supervisor(student=gs, supervisor=random.choice(supervisors), supervisor_type='COM')
            sup.save()
            if random.random() > 0.5:
                sup = Supervisor(student=gs, supervisor=random.choice(supervisors), supervisor_type='COM')
                sup.save()
            else:
                sup = Supervisor(student=gs, external="Some External Supervisor", supervisor_type='COM', config={'email': 'external@example.com'})
                sup.save()
        # TODO: completed requirements, letter templates and letters 

def create_grad_templ():
    templates = [
                 {"unit": Unit.objects.get(slug='cmpt'),
                  "label": "offer",
                  "content": "Congratulations, {{first_name}}, we would like to offer you admission to the {{program}} program in Computing Science at SFU.\r\n\r\nThis is good news. Really."
                  },
                 {"unit": Unit.objects.get(slug='cmpt'),
                  "label": "visa",
                  "content": "This is to confirm that {{title}} {{first_name}} {{last_name}} is currently enrolled as a full time student in the {{program}} in the School of Computing Science at SFU."
                  },
                 {"unit": Unit.objects.get(slug='cmpt'),
                  "label": "Funding",
                  "content": "This is to confirm that {{title}} {{first_name}} {{last_name}} is a student in the School of Computing Science's {{program}} program. {{He_She}} has been employed as follows:\r\n\r\n{% if tafunding %}Teaching assistant responsibilities include providing tutorials, office hours and marking assignments. {{title}} {{last_name}}'s assignments have been:\r\n\r\n{{ tafunding }}{% endif %}\r\n{% if rafunding %}Research assistants assist/provide research services to faculty. {{title}} {{last_name}}'s assignments have been:\r\n\r\n{{ rafunding }}{% endif %}\r\n{% if scholarships %}{{title}} {{last_name}} has received the following scholarships:\r\n\r\n{{ scholarships }}{% endif %}\r\n\r\n{{title}} {{last_name}} is making satisfactory progress."
                  },
                 ]
    for data in templates:
        t = LetterTemplate(**data)
        t.save()

def create_ta_data():
    unit = Unit.objects.get(slug='cmpt')
    s = Semester.objects.get(name=TEST_SEMESTER).next_semester()
    admin = Person.objects.get(userid='dixon')
    CourseDescription(unit=unit, description="Office/Marking", labtut=False).save()
    CourseDescription(unit=unit, description="Office/Marking/Lab", labtut=True).save()

    post = TAPosting(semester=s, unit=unit)
    post.opens = s.start - datetime.timedelta(100)
    post.closes = s.start - datetime.timedelta(20)
    post.set_salary([972,972,972,972])
    post.set_scholarship([135,340,0,0])
    post.set_accounts([Account.objects.get(account_number=12345).id, Account.objects.get(account_number=12346).id, Account.objects.get(account_number=12347).id, Account.objects.get(account_number=12348).id])
    post.set_start(s.start)
    post.set_end(s.end)
    post.set_deadline(s.start - datetime.timedelta(10))
    post.set_payperiods(7.5)
    post.set_contact(admin.id)
    post.set_offer_text("This is **your** TA offer.\n\nThere are various conditions that are too numerous to list here.")
    post.save()
    offerings = list(post.selectable_offerings())

    for p in Person.objects.filter(userid__endswith='grad'):
        app = TAApplication(posting=post, person=p, category=random.choice(['GTA1','GTA2']), current_program='CMPT', sin='123456789',
                            base_units=random.choice([3,4,5]))
        app.save()
        will_ta = []
        for i,o in enumerate(random.sample(offerings, 5)):
            t = random.choice(TAKEN_CHOICES)[0]
            e = random.choice(EXPER_CHOICES)[0]
            cp = CoursePreference(app=app, course=o.course, rank=i+1, taken=t, exper=e)
            cp.save()

            if random.random() < 0.07*(5-i):
                will_ta.append(o)

        if will_ta and random.random() < 0.75:
            c = TAContract(status=random.choice(['NEW','OPN','ACC']))
            c.first_assign(app, post)
            c.save()
            for o in will_ta:
                tac = TACourse(course=o, contract=c, bu=app.base_units)
                tac.description = tac.default_description()
                tac.save()

def create_ra_data():
    unit = Unit.objects.get(slug='cmpt')
    s = Semester.objects.get(name=TEST_SEMESTER)
    superv = list(possible_supervisor_people([unit]))
    empl = list(itertools.chain(Person.objects.filter(userid__endswith='grad'), random.sample(Person.objects.filter(last_name='Student'), 10)))
    cats = [c for c,d in HIRING_CATEGORY_CHOICES if c not in HIRING_CATEGORY_DISABLED]
    config = SemesterConfig.get_config([unit], s)

    acct = Account(account_number=12349, position_number=12349, title='NSERC RA', unit=unit)
    acct.save()
    proj1 = Project(project_number=987654, fund_number=31, unit=unit)
    proj1.save()
    proj2 = Project(project_number=876543, fund_number=13, unit=unit)
    proj2.save()

    for i in range(30):
        p = random.choice(empl)
        s = random.choice(superv)
        c = random.choice(cats)
        freq = random.choice(['B', 'L'])
        if freq == 'B':
            payargs = {'lump_sum_pay': 10000, 'biweekly_pay': 1250, 'pay_periods': 8, 'hourly_pay': 31, 'hours': 40}
        else:
            payargs = {'lump_sum_pay': 4000, 'biweekly_pay': 0, 'pay_periods': 8, 'hourly_pay': 0, 'hours': 0}
        ra = RAAppointment(person=p, sin=123456789, hiring_faculty=s, unit=unit, hiring_category=c,
                           project=random.choice([proj1,proj2]), account=acct, pay_frequency=freq,
                           start_date=config.start_date(), end_date=config.end_date(),
                           **payargs)
        ra.set_use_hourly(random.choice([True, False]))
        ra.save()



def create_more_data():
    """
    More data for the unit tests and general usabilty of a test system 
    """
    templates = [
                 {"field": "contact_email_text", 
                  "label": "generic", 
                  "text": "DESCRIPTION OF INCIDENT. This does not usually occur unless there is a violation of SFU's Code of Academic Integrity and Good Conduct, Policy S10.01. I take academic honesty very seriously and intend to pursue this apparent violation of SFU's standards for academic honesty.\r\n\r\nAs required by SFU Policy S10.02, Principles and Procedures for Academic Discipline, I am offering you the opportunity to meet with me to discuss this incident. You are not required to accept this offer. If you would like to meet, please contact me to make an appointment outside of my regular office hours.\r\n\r\nYou may wish to refer to SFU's policies and procedures on academic integrity,\r\n  http://www.sfu.ca/policies/Students/index.html .\r\nYou can also contact the Office of the Ombudsperson for assistance in navigating University procedures.\r\n"},
                 {"field": "contact_email_text", 
                  "label": "not your work", 
                  "text": "Your submission for {{ACTIVITIES}} contains work that does not appear to be your own. This indicates that there is a violation of SFU's Code of Academic Integrity and Good Conduct, Policy S10.01. I take academic honesty very seriously and intend to pursue this apparent violation of SFU's standards for academic honesty.\r\n\r\nAs required by SFU Policy S10.02, Principles and Procedures for Academic Discipline, I am offering you the opportunity to meet with me to discuss this incident. You are not required to accept this offer. If you would like to meet, please contact me to make an appointment outside of my regular office hours.\r\n\r\nYou may wish to refer to SFU's policies and procedures on academic integrity,\r\n  http://www.sfu.ca/policies/Students/index.html .\r\nYou can also contact the Office of the Ombudsperson for assistance in navigating University procedures.\r\n"},
                 {"field": "facts", 
                  "label": "attachment", 
                  "text": "See details in attached file facts.pdf."},
                 {"field": "contact_email_text", 
                  "label": "simiar work (group)", 
                  "text": "You and other students submitted very similar work on {{ACTIVITIES}}. This level of similarity does not usually occur unless collaboration exceeds the limits allowed by SFU's Code of Academic Integrity and Good Conduct, Policy S10.01. I take academic honesty very seriously and intend to pursue this apparent violation of SFU's standards for academic honesty.\r\n\r\nAs required by SFU Policy S10.02, Principles and Procedures for Academic Discipline, I am offering you the opportunity to meet with me to discuss this incident. You are not required to accept this offer. If you would like to meet, please contact me to make an appointment outside of my regular office hours.\r\n\r\nYou may wish to refer to SFU's policies and procedures on academic integrity,\r\n  http://www.sfu.ca/policies/Students/index.html .\r\nYou can also contact the Office of the Ombudsperson for assistance in navigating University procedures.\r\n"},
                 {"field": "facts", 
                  "label": "copied (other knew)", 
                  "text": "{{FNAME}} was given a solution to {{ACTIVITIES}} by another student. The other student seems to have completed the work independently. Both students submitted the work as their own."},
                 {"field": "facts", 
                  "label": "copied (without knowledge)", 
                  "text": "{{FNAME}} copied the work of another student on {{ACTIVITIES}} without his/her knowledge.  Both students submitted the work as their own."},
                 {"field": "meeting_summary", 
                  "label": "admitted", 
                  "text": u"The student admitted academic dishonesty as described below in \u201cfacts of the case\u201d."},
                 {"field": "meeting_summary", 
                  "label": "quote email", 
                  "text": "The student explained the situation in his/her email:\r\n\r\nbq. PASTE QUOTE HERE"},
                 {"field": "meeting_summary", 
                  "label": "explained", 
                  "text": "{{FNAME}} explained that..."},
                 ]
    for data in templates:
        t = DisciplineTemplate(**data)
        t.save()

    cmpt = Unit.objects.get(slug='cmpt')
    a = Account(account_number=12345, position_number=12345, title='MSc TA', unit=cmpt)
    a.save()
    a = Account(account_number=12346, position_number=12346, title='PhD TA', unit=cmpt)
    a.save()
    a = Account(account_number=12347, position_number=12347, title='External TA', unit=cmpt)
    a.save()
    a = Account(account_number=12348, position_number=12348, title='Undergrad TA', unit=cmpt)
    a.save()
    
    uc = UserConfig(user=Person.objects.get(userid='dzhao'), key='advisor-token', value={'token': '30378700c0091f34412ec9a082dca267'})
    uc.save()
    uc = UserConfig(user=Person.objects.get(userid='ggbaker'), key='advisor-token', value={'token': '082dca26730378700c0091f34412ec9a'})
    uc.save()
    p = Person(userid='probadmn', emplid='200002387', first_name='Problem', last_name='Admin')
    p.save()
    uc = UserConfig(user=p, key='problems-token', value={'token': '30378700c0091f34412ec9a082dca268'})
    uc.save()
    
    p = Person(userid='teachadm', emplid='200002388', first_name='Teaching', last_name='Admin')
    p.save()
    r = Role(person=p, role="TADM", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    #sp = SemesterPlan(semester=Semester.objects.get(name=TEST_SEMESTER), name='Test Plan', unit=Unit.objects.get(slug='cmpt'), slug='test-plan')
    #sp.save()
    #o = PlannedOffering(plan=sp, course=Course.objects.get(slug='cmpt-102'), section='D100', campus='BRNBY', enrl_cap=100)
    #o.save()
    #PlanningCourse.create_for_unit(Unit.objects.get(slug='cmpt'))
    #te = TeachingEquivalent(pk=1, instructor=Person.objects.get(userid='ggbaker'), semester=Semester.objects.get(name=TEST_SEMESTER), credits_numerator=1, credits_denominator=1, summary="Foo", status='UNCO')
    #te.save()
    #ti = TeachingIntention(instructor=Person.objects.get(userid='ggbaker'), semester=Semester.objects.get(name=TEST_SEMESTER), count=2)
    #ti.save()
    #tc = TeachingCapability(instructor=Person.objects.get(userid='ggbaker'), course=Course.objects.get(slug='cmpt-102'), note='foo')
    #tc.save()

    p = Person(userid='classam', emplid='200002389', first_name='Curtis', last_name='Lassam')
    p.save()
    r = Role(person=p, role="TECH", unit=Unit.objects.get(slug='cmpt'))
    r.save()
    r = Role(person=p, role="SYSA", unit=Unit.objects.get(slug='cmpt'))
    r.save()


def create_form_data():
    unit = Unit.objects.get(slug='cmpt')
    fg = FormGroup(name="Admins", unit=unit)
    fg.save()
    FormGroupMember(formgroup=fg, person=Person.objects.get(userid='ggbaker')).save()
    FormGroupMember(formgroup=fg, person=Person.objects.get(userid='classam')).save()

    f1 = Form(title="Simple Form", owner=fg, unit=fg.unit, description="Simple test form.", initiators='ANY')
    f1.save()
    s1 = Sheet(form=f1, title="Initial sheet")
    s1.save()
    fld1 = Field(label='Favorite Color', sheet=s1, fieldtype='SMTX', config={"min_length": 1, "required": True, "max_length": "100", 'label': 'Favorite Color', "help_text":''})
    fld1.save()
    fld2 = Field(label='Reason', sheet=s1, fieldtype='MDTX', config={"min_length": 10, "required": True, "max_length": "400", 'label': 'Reason', "help_text":'Why?'})
    fld2.save()
    fld3 = Field(label='Second Favorite Color', sheet=s1, fieldtype='SMTX', config={"min_length": 1, "required": False, "max_length": "100", 'label': 'Second Favorite Color', "help_text":''})
    fld3.save()

    f2 = Form(title="Appeal Form", owner=fg, unit=fg.unit, description="An all-purpose appeal form to appeal things with", initiators='LOG', advisor_visible=True)
    f2.save()
    s2 = Sheet(form=f2, title="Student Appeal")
    s2.save()
    fld4 = Field(label='Appeal', sheet=s2, fieldtype='SMTX', config={"min_length": 1, "required": True, "max_length": "100", 'label': 'Appeal', "help_text":'What do you want to appeal?'})
    fld4.save()
    fld4 = Field(label='Reasons', sheet=s2, fieldtype='LGTX', config={"min_length": 1, "required": True, "max_length": "1000", 'label': 'Reasons', "help_text":'Why do you think you deserve it?'})
    fld4.save()
    fld5 = Field(label='Prediction', sheet=s2, fieldtype='RADI', config={ "required": False, 'label': 'Prediction', "help_text":"Do you think it's likely this will be approved?", "choice_1": "Yes", "choice_2": "No", "choice_3": "Huh?"})
    fld5.save()
    s3 = Sheet(form=f2, title="Decision", can_view="ALL")
    s3.save()
    fld5 = Field(label='Decision', sheet=s3, fieldtype='RADI', config={ "required": True, 'label': 'Decision', "help_text":"Do you approve this appeal?", "choice_1": "Yes", "choice_2": "No", "choice_3": "See comments"})
    fld5.save()
    fld6 = Field(label='Comments', sheet=s3, fieldtype='MDTX', config={"min_length": 1, "required": False, "max_length": "1000", 'label': 'Comments', "help_text":'Any additional comments'})
    fld6.save()




def serialize(filename):
    """
    output JSON of everything we created
    """
    objs = itertools.chain(
            Semester.objects.all(),
            SemesterWeek.objects.all(),
            CourseOffering.objects.all(),
            Course.objects.all(),
            MeetingTime.objects.all(),
            Person.objects.all(),
            Member.objects.all(),
            Activity.objects.all(),
            NumericActivity.objects.all(),
            LetterActivity.objects.all(),
            CalNumericActivity.objects.all(),
            CalLetterActivity.objects.all(),
            SubmissionComponent.objects.all(),
            CodeComponent.objects.all(),
            PDFComponent.objects.all(),
            ActivityComponent.objects.all(),
            Group.objects.all(),
            GroupMember.objects.all(),
            Role.objects.all(),
            Unit.objects.all(),
            GradProgram.objects.all(),
            GradStudent.objects.all(),
            GradStatus.objects.all(),
            GradRequirement.objects.all(),
            GradFlag.objects.all(),
            Supervisor.objects.all(),
            ScholarshipType.objects.all(),
            DisciplineTemplate.objects.all(),
            LetterTemplate.objects.all(),
            Account.objects.all(),
            UserConfig.objects.all(),
            #SemesterPlan.objects.all(),
            #PlannedOffering.objects.all(),
            #PlanningCourse.objects.all(),
            #TeachingEquivalent.objects.all(),
            #TeachingIntention.objects.all(),
            #TeachingCapability.objects.all(),
            FormGroup.objects.all(),
            FormGroupMember.objects.all(),
            Form.objects.all(),
            Sheet.objects.all(),
            Field.objects.all(),
            FormSubmission.objects.all(),
            SheetSubmission.objects.all(),
            FieldSubmission.objects.all(),
            TAPosting.objects.all(),
            TAApplication.objects.all(),
            CoursePreference.objects.all(),
            CourseDescription.objects.all(),
            TAContract.objects.all(),
            TACourse.objects.all(),
            RAAppointment.objects.all(),
            Project.objects.all(),
            SemesterConfig.objects.all(),
            )
    
    data = serializers.serialize("json", objs, sort_keys=True, indent=1)
    fh = open(filename, "w")
    fh.write(data)
    fh.close()

def import_semesters():
    """
    What semesters should we actually import? (returns tuple of strm values)
    """
    sems = Semester.objects.filter(end__gte=past_cutoff)
    return tuple(s.name for s in sems)

def create_fake_semester(strm):
    """
    Create a close-enough Semester object for testing
    """
    strm = str(strm)
    s = Semester(name=strm)
    yr = int(strm[0:3]) + 1900
    if strm[3] == '1':
        mo = 1
    elif strm[3] == '4':
        mo = 5
    elif strm[3] == '7':
        mo = 9

    s.start = datetime.date(yr,mo,5)
    s.end = datetime.date(yr,mo+3,1)
    s.save()

    sw = SemesterWeek(semester=s, week=1)
    mon = s.start
    while mon.weekday() != 0:
        mon -= datetime.timedelta(days=1)
    sw.monday = mon
    sw.save()

def create_units():
    univ = Unit.objects.get(label='UNIV')
    fas = Unit(label='FAS', name='Faculty of Applied Sciences', parent=univ).save()
    ensc = Unit(label='ENSC', name='School of Engineering Science', parent=fas, acad_org='ENG SCI').save()
    cmpt = Unit(label='CMPT', name='School of Computing Science', parent=fas, acad_org='COMP SCI')
    cmpt.set_address(['9971 Applied Sciences Building', '8888 University Drive, Burnaby, BC', 'Canada V5A 1S6'])
    cmpt.set_email('csdept@sfu.ca')
    cmpt.set_web('http://www.cs.sfu.ca/')
    cmpt.set_tel('778-782-4277')
    cmpt.set_fax('778-782-3045')
    cmpt.set_informal_name('Computing Science')
    cmpt.config['sessional_pay'] = 10000
    cmpt.set_deptid('12345')
    cmpt.save()

def main():
    for strm in NEEDED_SEMESTERS:
        create_fake_semester(strm)
    create_units()

    print "getting emplid/userid mapping"
    update_amaint_userids()

    print "importing course offerings"
    # get very few courses here so there isn't excess data hanging around
    offerings = import_offerings(import_semesters=import_semesters, extra_where=
        #"(subject='CMPT' AND (catalog_nbr LIKE '%%165%%')) "
        #"OR (subject='ENSC' AND (catalog_nbr LIKE '%% 100%%')) "
        "(subject='CMPT' AND (catalog_nbr LIKE '%% 1%%' OR catalog_nbr LIKE '%% 2%%')) "
        "OR (subject='ENSC' AND (catalog_nbr LIKE '%% 2_5%%')) "
        )
    offerings = list(offerings)
    offerings.sort()
    
    print "importing course members"
    for o in offerings:
        import_offering_members(o, students=False)

    # should now have all the "real" people: fake their emplids
    fake_emplids()
    ComputingAccount.objects.all().delete()

    # make sure these people are here, since we need them
    if not Person.objects.filter(userid='ggbaker'):
        Person(userid='ggbaker', first_name='Gregory', last_name='Baker', emplid='000001233').save()
    if not Person.objects.filter(userid='dixon'):
        Person(userid='dixon', first_name='Tony', last_name='Dixon', emplid='000001234').save()
    if not Person.objects.filter(userid='diana'):
        Person(userid='diana', first_name='Diana', last_name='Cukierman', emplid='000001235').save()
    if not Person.objects.filter(userid='popowich'):
        Person(userid='popowich', first_name='Fred', last_name='Popowich', emplid='000001236').save()

    print "creating fake classess"
    create_classes()
    create_test_classes()

    print "creating other data"
    create_others()
    create_grad_templ()
    create_more_data()
    create_form_data()
    combine_sections(get_combined())
    
    print "creating grad students"
    create_grads()
    create_ta_data()
    create_ra_data()

    print "giving sysadmin permissions"
    give_sysadmin(['ggbaker', 'sumo'])
    
    serialize("new-test.json")




if __name__ == "__main__":
    hostname = socket.gethostname()
    if hostname == 'courses':
        raise NotImplementedError, "Don't do that."
    main()

