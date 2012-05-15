"""
    Test portions of the marking app.
"""

import re
import unicodecsv as csv

from decimal import Decimal, ROUND_HALF_EVEN

from datetime import datetime

from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client

from models import ActivityComponent, CommonProblem, Group, GroupMember
from models import StudentActivityMark, GroupActivityMark
from coredata.models import CourseOffering, Member, Person
from grades.models import NumericActivity, NumericGrade, LetterActivity, LetterGrade

from views import manage_activity_components, manage_common_problems, marking_student
from views import _compose_imported_grades, _strip_email_userid

from settings import CAS_SERVER_URL

from courselib.testing import basic_page_tests, TEST_COURSE_SLUG



class BasicTest(TestCase):
    fixtures = ['test_data']    

    def setUp(self):
        self.c_slug = TEST_COURSE_SLUG
    
    def test_add_activity_components(self):
        
        c = CourseOffering.objects.get(slug = self.c_slug)
       
        #add a numeric activity and its components
        a = NumericActivity(offering = c, name = 'test_assignment_1', \
                            short_name = 'ta1', status = 'RLS', \
                            due_date = datetime.now(), max_grade = 100, position = 0)
        a.save()
      
        co1 = ActivityComponent(numeric_activity = a, title = 'part1', max_mark = 20, position = 0)
        co2 = ActivityComponent(numeric_activity = a, title = 'part2', max_mark = 30, position = 1)
        co3 = ActivityComponent(numeric_activity = a, title = 'part3', max_mark = 50, position = 2)
        
        co1.save()
        co2.save()
        co3.save()
        
        self.client.login(ticket = 'ggbaker', service=CAS_SERVER_URL)

        response = basic_page_tests(self, self.client, reverse(manage_activity_components, args=(self.c_slug,a.slug)))
          
        forms = response.context['formset'].forms
        self.assertEquals(forms[0].instance.title, 'part1')
        self.assertEquals(forms[1].instance.title, 'part2')
        self.assertEquals(forms[2].instance.title, 'part3') 
        
    def test_add_common_problems(self):
        c = CourseOffering.objects.get(slug = self.c_slug)
        a = NumericActivity(offering = c, name = 'test_assignment_1', \
                            short_name = 'ta1', status = 'RLS', \
                            due_date = datetime.now(), max_grade = 100, position = 0)
        a.save()        
        co1 = ActivityComponent(numeric_activity = a, title = 'part1', max_mark = 50, position = 0)
        co2 = ActivityComponent(numeric_activity = a, title = 'part2', max_mark = 50, position = 1) 
        co1.save()
        co2.save()
        
        #add some common problems
        cp1 = CommonProblem(activity_component = co1, title = 'cp1', penalty="0")
        cp2 = CommonProblem(activity_component = co1, title = 'cp2', penalty="1.12")        
        cp3 = CommonProblem(activity_component = co2, title = 'cp3', penalty="-2.3")
        
        cp1.save()
        cp2.save()
        cp3.save()
        
        self.client.login(ticket = 'ggbaker', service=CAS_SERVER_URL)        

        response = basic_page_tests(self, self.client, reverse(manage_common_problems, args=(self.c_slug,a.slug)))
        
        forms = response.context['formset'].forms
 
        ins0 = forms[0].instance
        ins1 = forms[1].instance
        ins2 = forms[2].instance
        
        self.assertEquals(ins0.title, 'cp1')
        self.assertEquals(ins0.activity_component, co1)
        self.assertEquals(ins1.title, 'cp2')
        self.assertEquals(ins1.activity_component, co1)
        self.assertEquals(ins2.title, 'cp3')
        self.assertEquals(ins2.activity_component, co2)
        
        #test the marking page as well        
        url = reverse(marking_student, args=(self.c_slug, a.slug, '0aaa0'))
        response = basic_page_tests(self, self.client, url)
        
        mark_components = response.context['component_data']
        com1 = mark_components[0]
        com2 = mark_components[1]
        
        self.assertEquals(com1['component'], co1)
        self.assertEquals(len(com1['common_problems']), 2)
        self.assertEquals(com2['component'], co2)
        self.assertEquals(len(com2['common_problems']), 1)
       
    def test_post_activity_components(self):
        c = CourseOffering.objects.get(slug = self.c_slug)
       
        #add a numeric activity and its components
        a = NumericActivity(offering = c, name = 'test_assignment_1', \
                            short_name = 'ta1', status = 'RLS', \
                            due_date = datetime.now(), max_grade = 100, position = 0)
        a.save()
                                    
        self.client.login(ticket = 'ggbaker', service=CAS_SERVER_URL)

        url = reverse(manage_activity_components, args=(self.c_slug, a.slug))

        # 2 forms for the first 2 components to add
        post_data = {'form-0-id' : ['', ''], 'form-1-id' : ['', ''],
                     'form-0-title': ['part1'], 'form-1-title': ['part2'], 
                     'form-0-max_mark' : ['20'], 'form-1-max_mark': ['20'],                    
                     'form-0-description' : ['basic1'], 'form-1-description': ['basic2'],
                     'form-TOTAL_FORMS' : ['3'], 'form-INITIAL_FORMS':['0']}
        
        response = self.client.post(url, post_data, follow = True)
        self.assertEquals(response.status_code, 200)
        
        cps = ActivityComponent.objects.filter(numeric_activity = a, deleted = False)
        self.assertEquals(len(cps), 2)
        self.assertEquals(cps[0].title, 'part1')        
        self.assertEquals(cps[1].title, 'part2')
        
        # keep the first 2 components, and add 2 more new components
        post_data2 = {'form-2-id' : ['', ''], 'form-3-id' : ['', ''],
                     'form-2-title': ['part3'], 'form-3-title': ['part4'], 
                     'form-2-max_mark' : ['30'], 'form-3-max_mark': ['30'],                    
                     'form-2-description' : ['advanced1'], 'form-3-description': ['advanced2'],
                     }
        post_data.update(post_data2)
       
        post_data['form-0-id'] = [str(cps[0].id), str(cps[0].id)]
        post_data['form-1-id'] = [str(cps[1].id), str(cps[1].id)]        
        post_data['form-INITIAL_FORMS'] = ['2']
        
        post_data['form-TOTAL_FORMS'] = ['5']
                
        response = self.client.post(url, post_data, follow = True)
        self.assertEquals(response.status_code, 200)
        cps = ActivityComponent.objects.filter(numeric_activity = a, deleted = False)
        self.assertEquals(len(cps), 4)
        self.assertEquals(cps[2].title, 'part3')        
        self.assertEquals(cps[3].title, 'part4')
    
    def test_group_setMark(self):
        c = CourseOffering.objects.get(slug = self.c_slug)
       
        #add a numeric activity
        a = NumericActivity(offering = c, name = 'test_assignment_1', \
                            short_name = 'ta1', status = 'RLS', \
                            due_date = datetime.now(), max_grade = 100, position = 0)
        a.save()
        
        #take 2 students to make a group       
        stud1 = Member.objects.get(person = Person.objects.get(userid = '0aaa0'), offering = c)
        stud2 = Member.objects.get(person = Person.objects.get(userid = '0aaa1'), offering = c)
                
        group = Group.objects.create(courseoffering = c, name = 'hello', manager = stud1)
        member1 = GroupMember.objects.create(group = group, student = stud1, confirmed = True, activity=a)
        member2 = GroupMember.objects.create(group = group, student = stud2, confirmed = True, activity=a)
        
        MARK = 30
        group_mark = GroupActivityMark(group = group, numeric_activity = a)
        group_mark.setMark(MARK)
        group_mark.save()
        
        num_grades = NumericGrade.objects.filter(activity = a).order_by('member__person__userid')
        self.assertEquals(len(num_grades), 2)
        self.assertEquals(num_grades[0].member, stud1)        
        self.assertEquals(num_grades[0].value, MARK)     
        self.assertEquals(num_grades[0].flag, 'GRAD')
        self.assertEquals(num_grades[1].member, stud2) 
        self.assertEquals(num_grades[1].value, MARK) 
        self.assertEquals(num_grades[1].flag, 'GRAD')
    
    def test_mark_history(self):
        c = CourseOffering.objects.get(slug = self.c_slug)
       
        #add a numeric activity
        a = NumericActivity(offering = c, name = 'test_assignment_1', \
                            short_name = 'ta1', status = 'RLS', \
                            due_date = datetime.now(), max_grade = 100, position = 0)
        a.save()
        
        #take 2 students to make a group       
        stud1 = Member.objects.get(person = Person.objects.get(userid = '0aaa0'), offering = c)
        stud2 = Member.objects.get(person = Person.objects.get(userid = '0aaa1'), offering = c)
                
        group = Group.objects.create(courseoffering = c, name = 'hello', manager = stud1)
        member1 = GroupMember.objects.create(group = group, student = stud1, confirmed = True, activity=a)
        member2 = GroupMember.objects.create(group = group, student = stud2, confirmed = True, activity=a)
        
        ngrade = NumericGrade(activity = a, member = stud2)                  
        ngrade.save()
        
                 
        #assign mark to 0aaa1 individually twice and via the group twice, make some interval between saves     
        std_mark = StudentActivityMark(numeric_grade = ngrade, created_by = 'ggbaker')           
        std_mark.setMark(20)
        std_mark.save()  
               
        group_mark = GroupActivityMark(group = group, numeric_activity = a, created_by = 'ggbaker')  
        group_mark.setMark(30)
        group_mark.save()
        
        std_mark = StudentActivityMark(numeric_grade = ngrade, created_by = 'ggbaker')
        std_mark.setMark(40)
        std_mark.save()   
        
        group_mark = GroupActivityMark(group = group, numeric_activity = a,  created_by = 'ggbaker')
        group_mark.setMark(50)               
        group_mark.save()
        
        self.client.login(ticket = 'ggbaker', service=CAS_SERVER_URL)

        response = self.client.get(reverse('marking.views.mark_history_student', args=(self.c_slug, a.slug, '0aaa1')))
        self.assertEquals(response.status_code, 200)
        
        latest_act_mark = response.context['current_mark']
        self.assertEquals(len(response.context['marks_individual']), 2)
        self.assertEquals(len(response.context['marks_via_group']), 2)
        self.assertEquals(group_mark, latest_act_mark)

        
    def test_frontend(self):
        client = Client()
        client.login(ticket='ggbaker', service=CAS_SERVER_URL)
        
        # set up a course
        c = CourseOffering.objects.get(slug = self.c_slug)
        a1 = NumericActivity(offering = c, name = 'test_assignment_1', \
                            short_name = 'ta1', status = 'RLS', \
                            due_date = datetime.now(), max_grade = 100, position = 0, group=True)
        a1.save()
        a2 = NumericActivity(offering = c, name = 'test_assignment_1', \
                            short_name = 'ta1', status = 'RLS', \
                            due_date = datetime.now(), max_grade = 100, position = 0, group=False)
        a2.save()
        
        stud1 = Member.objects.get(person = Person.objects.get(userid = '0aaa0'), offering = c)
        stud2 = Member.objects.get(person = Person.objects.get(userid = '0aaa1'), offering = c)
        instr = Member.objects.get(person = Person.objects.get(userid = 'ggbaker'), offering = c)
        group = Group.objects.create(courseoffering = c, name = 'hello', manager = stud1)
        member1 = GroupMember.objects.create(group = group, student = stud1, confirmed = True, activity=a1)
        member2 = GroupMember.objects.create(group = group, student = stud2, confirmed = True, activity=a1)
        
        # marking form (student)
        url = reverse('marking.views.marking_student', kwargs={'course_slug':c.slug, 'activity_slug':a2.slug, 'userid':stud1.person.userid})

        response = basic_page_tests(self, client, url)
        
        ac = ActivityComponent(numeric_activity=a2, max_mark=5, title="AC Title", description="AC Description", position=1, deleted=False)
        ac.save()
        ac = ActivityComponent(numeric_activity=a2, max_mark=5, title="AC Title2", description="AC Description2", position=2, deleted=False)
        ac.save()
        cp = CommonProblem(activity_component=ac, title="CP title", penalty=2, description="Cp description", deleted=False)
        cp.save()

        response = basic_page_tests(self, client, url)
        
        # submit the form and check that objects were created
        PENALTY = '12.5' # Percentage
        CMP_1_VALUE = '5.5'
        CMP_2_VALUE = '3'
        ADJ = '1.25'# Adjustments are subtracted
        TOTAL_MARK = ((Decimal(CMP_1_VALUE) + Decimal(CMP_2_VALUE) - Decimal(ADJ)) *
            (1 - (Decimal(PENALTY) / 100))).quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)

        response = client.post(url, {'cmp-1-value': float(CMP_1_VALUE), 'cmp-1-comment': 'perfect part 1',
            'cmp-2-value': float(CMP_2_VALUE), 'cmp-2-comment': 'ok', 'mark_adjustment': float(ADJ),
            'mark_adjustment_reason': 'reason', 'late_penalty': float(PENALTY),
            u'overall_comment': 'overall'})
        self.assertEquals(response.status_code, 302)
        sam = StudentActivityMark.objects.filter(activity=a2, numeric_grade__member=stud1)
        self.assertEquals(len(sam), 1)
        sam = sam[0]
        self.assertEquals(sam.mark_adjustment, Decimal(ADJ))
        self.assertEquals(sam.late_penalty, Decimal(PENALTY))
        self.assertEquals(sam.overall_comment, 'overall')
        self.assertEquals(sam.mark, TOTAL_MARK)
        acms = sam.activitycomponentmark_set.all()
        self.assertEquals(len(acms), 2)
        self.assertEquals(acms[0].value, Decimal(CMP_1_VALUE))
        self.assertEquals(acms[0].comment, 'perfect part 1')
        g = NumericGrade.objects.get(activity=a2, member=stud1)
        self.assertEquals(g.value, TOTAL_MARK)
        
        # make sure we get old data for "mark based on"
        response = basic_page_tests(self, client, url + "?base_activity_mark="+str(sam.id))
        self.assertContains(response, 'name="cmp-1-value" value="{0}"'.format(CMP_1_VALUE))
        self.assertContains(response, 'name="late_penalty" value="{0}"'.format(PENALTY))

        # look at the "view details" page
        url = reverse('marking.views.mark_summary_student', kwargs={'course_slug':c.slug, 'activity_slug':a2.slug, 'userid':stud1.person.userid})
        response = basic_page_tests(self, client, url)
        self.assertContains(response, 'perfect part 1')

        # marking form (group)
        url = reverse('marking.views.marking_student', kwargs={'course_slug':c.slug,
            'activity_slug':a1.slug, 'userid':stud1.person.userid})
        response = basic_page_tests(self, client, url)
        
        ac = ActivityComponent(numeric_activity=a1, max_mark=5, title="AC Title",
            description="AC Description", position=1, deleted=False)
        ac.save()
        ac = ActivityComponent(numeric_activity=a1, max_mark=5, title="AC Title2",
            description="AC Description2", position=2, deleted=False)
        ac.save()
        cp = CommonProblem(activity_component=ac, title="CP title", penalty=2,
            description="Cp description", deleted=False)
        cp.save()

        response = basic_page_tests(self, client, url)

        # common problem form
        url = reverse('marking.views.manage_common_problems', kwargs={'course_slug':c.slug, 'activity_slug':a2.slug})
        response = basic_page_tests(self, client, url)
        
        # mark all (student and group)
        url = reverse('marking.views.mark_all_students', kwargs={'course_slug':c.slug, 'activity_slug':a2.slug})
        response = basic_page_tests(self, client, url)
        # mark all (student and group)
        url = reverse('marking.views.mark_all_groups', kwargs={'course_slug':c.slug, 'activity_slug':a1.slug})
        response = basic_page_tests(self, client, url)

class TestImportFunctionsNumeric(TestCase):
    fixtures = ['test_data']    

    def setUp(self):
        self.c_slug = TEST_COURSE_SLUG
        self.c = CourseOffering.objects.get(slug = self.c_slug)
        self.a1 = NumericActivity(offering = self.c, name = 'test_assignment_1', 
                            short_name = 'ta1', status = 'RLS', 
                            due_date = datetime.now(), max_grade = 100,
                            position = 0)
        self.a1.save()
        self.students = self.c.members.filter(person__role='STUD')
        self.userids = [p.userid for p in self.students]
        self.emplids = [p.emplid for p in self.students]

    def get_test_file(self, name):
        with open(name, 'r') as inp:
            r = csv.reader(inp)
            self.values = []
            for line in r:
                self.values.append(line)

    def compare_grade_lists(self, data_returned):
        for sname, grade in self.values:
            sname = _strip_email_userid(sname)
            self.assertIn(sname, data_returned.keys())
            self.assertEqual(data_returned[sname], grade)
        

    def test_import_grades_old_format(self):
        inName = 'marking/testfiles/oldformat_noprob.csv'
        self.get_test_file(inName)
        data_to_return = {}
        with open(inName, 'r') as inp:
	    err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, None)
        self.assertEqual(len(data_to_return), len(self.values))
        self.compare_grade_lists(data_to_return)

    def test_import_grades_old_format_unknown_userid(self):
        inName = 'marking/testfiles/oldformat_unk_uid.csv'
        self.get_test_file(inName)
        bad_id = [n for n,_ in self.values if n not in self.userids] [0]
        data_to_return = {}
        with open(inName, 'r') as inp:
	    err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, 'Error found in the file (row 2): Unmatched student number '
            'or user-id ({0}).'. format(bad_id))
        self.assertEqual(len(data_to_return), 0)

    def test_import_grades_old_format_unknown_emplid(self):
        inName = 'marking/testfiles/oldformat_unk_emplid.csv'
        self.get_test_file(inName)
        bad_emplid = [e for e,_ in self.values if int(e) not in self.emplids] [0]
        data_to_return = {}
        with open(inName, 'r') as inp:
	    err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, 'Error found in the file (row 1): Unmatched student number '
            'or user-id ({0}).'. format(bad_emplid))
        self.assertEqual(len(data_to_return), 0)

    def test_import_grades_new_format(self):
        inName = 'marking/testfiles/newformat_noprob_userid.csv'
        self.get_test_file(inName)
        del self.values[0] # Delete header row
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, None)
        self.assertEqual(len(data_to_return), len(self.values))
        self.compare_grade_lists(data_to_return)

    def test_import_grades_short_row(self):
        inName = 'marking/testfiles/newformat_shortrow_userid.csv'
        self.get_test_file(inName)
        del self.values[0] # Delete header row
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, None)
        self.assertEqual(len(data_to_return), len(self.values)-1)

    def test_import_grades_new_format_junk_cols(self):
        inName = 'marking/testfiles/newformat_noprob_junk_cols.csv'
        self.get_test_file(inName)
        del self.values[0] # Delete header row
        for i, row in enumerate(self.values):
            self.values[i] = [self.values[i][3], self.values[i][1]]
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, None)
        self.assertEqual(len(data_to_return), len(self.values))
        self.compare_grade_lists(data_to_return)

    def test_import_grades_new_format_missing_uid_col(self):
        '''
            Judgement call on the design:  If the import file lacks a field
            named 'Userid', we treat it as an old-format file and get an 
            error on the first line.  This unfortunate outcome is required
            if we are to avoid misinterpreting a short assignment name that
            matches a student id and thereby misinterpreting an old-style
            file as though it were a defective (i.e., no 'Userid' column)
            new-style file.
        '''
        inName = 'marking/testfiles/newformat_missing_uid_col.csv'
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, 'Error found in the file (row 1): Unmatched student number or user-id (Junk1).')
        self.assertEqual(len(data_to_return), 0)

    def test_import_grades_new_format_missing_act_col(self):
        inName = 'marking/testfiles/newformat_missing_act_col.csv'
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, 'Error in file header line:  No '
            'column labelled for activity {0}.'.format(self.a1.short_name))
        self.assertEqual(len(data_to_return), 0)

    def test_import_grades_new_format_dup_act_col(self):
        inName = 'marking/testfiles/newformat_dup_act_col.csv'
        data_to_return = {}
        with open(inName, 'r') as inp:
            err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, 'Error in file header line:  Two columns '
            'labelled {0}.'.format(self.a1.short_name))
        self.assertEqual(len(data_to_return), 0)

    def test_import_grades_new_format_missing_values(self):
        ''' OK for students to have no grade assigned. '''
        inName = 'marking/testfiles/newformat_missing_student_grade.csv'
        self.get_test_file(inName)
        del self.values[0] # Delete header row
        for i, row in enumerate(self.values):
            self.values[i] = [self.values[i][6], self.values[i][1]]
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, None)
        self.assertEqual(len(data_to_return), len(self.values))
        self.compare_grade_lists(data_to_return)

    def test_import_grades_new_format_bad_utf8(self):
        inName = 'marking/testfiles/newformat_bad_utf8.csv'
        data_to_return = {}
        with open(inName, 'r') as inp:
            err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err,
            'File cannot be decoded as UTF-8 data: make sure it has been saved as UTF-8 text.')
        self.assertEqual(len(data_to_return), 0)


class TestImportFunctionsLetter(TestCase):
    fixtures = ['test_data']    

    def setUp(self):
        self.c_slug = TEST_COURSE_SLUG
        self.c = CourseOffering.objects.get(slug = self.c_slug)
        self.a1 = LetterActivity(offering = self.c, name = 'test_assignment_let_1', 
                            short_name = 'tal1', status = 'RLS', 
                            due_date = datetime.now(),
                            position = 0)
        self.a1.save()
        self.students = self.c.members.filter(person__role='STUD')
        self.userids = [p.userid for p in self.students]
        self.emplids = [p.emplid for p in self.students]

    def get_test_file(self, name):
        with open(name, 'r') as inp:
            r = csv.reader(inp)
            self.values = []
            for line in r:
                self.values.append(line)

    def compare_grade_lists(self, data_returned):
        for sname, grade in self.values:
            self.assertIn(sname, data_returned.keys())
            self.assertEqual(data_returned[sname], grade)
        
    def test_import_grades_new_format_l(self):
        inName = 'marking/testfiles/newformat_noprob_userid_let.csv'
        self.get_test_file(inName)
        del self.values[0] # Delete header row
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, None)
        self.assertEqual(len(data_to_return), len(self.values))
        self.compare_grade_lists(data_to_return)
        
    def test_import_grades_old_format_l(self):
        inName = 'marking/testfiles/oldformat_noprob_let.csv'
        self.get_test_file(inName)
        data_to_return = {}
        with open(inName, 'r') as inp:
             err = _compose_imported_grades(inp, self.students, data_to_return, self.a1)
        self.assertEqual(err, None)
        self.assertEqual(len(data_to_return), len(self.values))
        self.compare_grade_lists(data_to_return)

class TestImportViews(TestCase):
    fixtures = ['test_data']

    def setUp(self):
        self.c_slug = TEST_COURSE_SLUG
        self.c = CourseOffering.objects.get(slug = self.c_slug)
        self.a1 = NumericActivity(offering = self.c, name = 'test_assignment_1', 
                            short_name = 'ta1', status = 'RLS', 
                            due_date = datetime.now(), max_grade = 100,
                            position = 0)
        self.a1.save()

    def check_student_db_grade(self, grade, s, g):
        self.assertEquals(grade.member, s)
        self.assertEquals(grade.value, Decimal(g))
        self.assertEquals(grade.flag, 'GRAD')

    def test_import_view(self):
        self.client.login(ticket='ggbaker', service=CAS_SERVER_URL)

        # Import the file, check that resulting HTML has correct entries in fields for two affected students
        url = reverse('marking.views.mark_all_students', kwargs={'course_slug':self.c_slug, 'activity_slug':self.a1.slug})
        with open('marking/testfiles/newformat_noprob_userid.csv') as file:
            post_data = {'import-file-file':[file]}
            response = self.client.post(url+"?import=true", post_data, follow=True)
        self.assertEquals(response.status_code, 200)
        stud1 = Member.objects.get(person = Person.objects.get(userid = '0aaa0'), offering = self.c)
        stud2 = Member.objects.get(person = Person.objects.get(userid = '0aaa1'), offering = self.c)
        STUD1_GRADE = '88'
        STUD2_GRADE = '15'
        self.assertTrue(re.search(STUD1_GRADE, response.content))
        self.assertTrue(re.search(STUD2_GRADE, response.content))

        # Submit the grades, check that they were added to DB
	post_data={'0aaa0-value':STUD1_GRADE, '0aaa1-value':STUD2_GRADE}
        response = self.client.post(url, post_data, follow=True)
        self.assertEquals(response.status_code, 200)
        num_grades = NumericGrade.objects.filter(activity = self.a1).order_by('member__person__userid')
        self.assertEquals(len(num_grades), 2)
        self.check_student_db_grade(num_grades[0], stud1, STUD1_GRADE)
        self.check_student_db_grade(num_grades[1], stud2, STUD2_GRADE)

class TestImportViewsLet(TestCase):
    fixtures = ['test_data']

    def setUp(self):
        self.c_slug = TEST_COURSE_SLUG
        self.c = CourseOffering.objects.get(slug = self.c_slug)
        self.a1 = LetterActivity(offering = self.c, name = 'test_assignment_1_let', 
                            short_name = 'tal1', status = 'RLS', 
                            due_date = datetime.now(),
                            position = 0)
        self.a1.save()

    def check_student_db_grade(self, grade, s, g):
        self.assertEquals(grade.member, s)
        self.assertEquals(grade.letter_grade, g)
        self.assertEquals(grade.flag, 'GRAD')

    def test_import_view_let(self):
        self.client.login(ticket='ggbaker', service=CAS_SERVER_URL)

        # Import the file, check that resulting HTML has correct entries in fields for two affected students
        url = reverse('marking.views.mark_all_students', kwargs={'course_slug':self.c_slug, 'activity_slug':self.a1.slug})
        with open('marking/testfiles/newformat_noprob_userid_let.csv') as file:
            post_data = {'import-file-file':[file]}
            response = self.client.post(url+"?import=true", post_data, follow=True)
        self.assertEquals(response.status_code, 200)
        stud1 = Member.objects.get(person = Person.objects.get(userid = '0aaa0'), offering = self.c)
        stud2 = Member.objects.get(person = Person.objects.get(userid = '0aaa1'), offering = self.c)
        STUD1_GRADE = 'A'
        STUD2_GRADE = 'C-'
        self.assertTrue(re.search(STUD1_GRADE, response.content))
        self.assertTrue(re.search(STUD2_GRADE, response.content))

        # Submit the grades, check that they were added to DB
	post_data={'0aaa0-value':STUD1_GRADE, '0aaa1-value':STUD2_GRADE}
        response = self.client.post(url, post_data, follow=True)
        self.assertEquals(response.status_code, 200)
        let_grades = LetterGrade.objects.filter(activity = self.a1).order_by('member__person__userid')
        self.assertEquals(len(let_grades), 2)
        self.check_student_db_grade(let_grades[0], stud1, STUD1_GRADE)
        self.check_student_db_grade(let_grades[1], stud2, STUD2_GRADE)



class TestMarkingImport(TestCase):
    fixtures = ['test_data']
    
    def setUp(self):
        self.crs = CourseOffering.objects.get(slug=TEST_COURSE_SLUG)
        self.act = self.crs.activity_set.get(slug="a1")
    
    def test_import(self):
        self.client.login(ticket='ggbaker', service=CAS_SERVER_URL)
        url = reverse('marking.views.import_marks', kwargs={'course_slug':self.crs.slug, 'activity_slug':self.act.slug})
        response = basic_page_tests(self, self.client, url)
        
        # post first file
        with open('marking/testfiles/marking_import1.json') as file:
            post_data = {'file':[file]}
            response = self.client.post(url, post_data)
        
        self.assertEquals(response.status_code, 302)
        
        # check that the parts are there
        marks = StudentActivityMark.objects.filter(activity=self.act)
        m = marks.get(numeric_grade__member__person__userid="0aaa12")
        self.assertEquals(m.numeric_grade.value, Decimal('3'))
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-1")
        self.assertEquals(mc.value, Decimal('3'))
        self.assertEquals(mc.comment, "0aaa12 1")
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-2")
        self.assertEquals(mc.value, Decimal('0'))
        self.assertEquals(mc.comment, "")

        m = marks.get(numeric_grade__member__person__userid="0aaa8")
        self.assertAlmostEquals(float(m.numeric_grade.value), 3.6)
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-1")
        self.assertEquals(mc.value, Decimal('4'))
        self.assertEquals(mc.comment, "0aaa8 1a")
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-2")
        self.assertEquals(mc.value, Decimal('0'))
        self.assertEquals(mc.comment, "")
        
        
        # post second file: should be combined with first.
        with open('marking/testfiles/marking_import2.json') as file:
            post_data = {'file':[file]}
            response = self.client.post(url, post_data)
        self.assertEquals(response.status_code, 302)
        
        marks = StudentActivityMark.objects.filter(activity=self.act)
        m = marks.filter(numeric_grade__member__person__userid="0aaa12").latest('created_at')
        self.assertAlmostEquals(float(m.numeric_grade.value), 3.2)
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-1")
        self.assertEquals(mc.value, Decimal('3'))
        self.assertEquals(mc.comment, "0aaa12 1")
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-2")
        self.assertEquals(mc.value, Decimal('1'))
        self.assertEquals(mc.comment, "0aaa12 2")

        m = marks.filter(numeric_grade__member__person__userid="0aaa8").latest('created_at')
        self.assertAlmostEquals(float(m.numeric_grade.value), 6.3)
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-1")
        self.assertEquals(mc.value, Decimal('5'))
        self.assertEquals(mc.comment, "0aaa8 1b")
        mc = m.activitycomponentmark_set.get(activity_component__slug="part-2")
        self.assertEquals(mc.value, Decimal('2'))
        self.assertEquals(mc.comment, "0aaa8 2")

