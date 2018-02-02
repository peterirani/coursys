# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-18 17:09
from __future__ import unicode_literals

import autoslug.fields
import bitfield.models
import courselib.json_fields
import datetime
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import faculty.event_types.awards
import faculty.event_types.career
import faculty.event_types.info
import faculty.event_types.position
import faculty.event_types.teaching
import faculty.models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0016_shorten_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='careerevent',
            name='config',
            field=courselib.json_fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='careerevent',
            name='event_type',
            field=models.CharField(choices=[('ADMINPOS', faculty.event_types.position.AdminPositionEventHandler), ('APPOINT', faculty.event_types.career.AppointmentEventHandler), ('AWARD', faculty.event_types.awards.AwardEventHandler), ('COMMITTEE', faculty.event_types.info.CommitteeMemberHandler), ('EXTERN_AFF', faculty.event_types.info.ExternalAffiliationHandler), ('EXTSERVICE', faculty.event_types.info.ExternalServiceHandler), ('FELLOW', faculty.event_types.awards.FellowshipEventHandler), ('GRANTAPP', faculty.event_types.awards.GrantApplicationEventHandler), ('NORM_TEACH', faculty.event_types.teaching.NormalTeachingLoadHandler), ('LEAVE', faculty.event_types.career.OnLeaveEventHandler), ('ONE_NINE', faculty.event_types.teaching.OneInNineHandler), ('OTHER_NOTE', faculty.event_types.info.OtherEventHandler), ('LABMEMB', faculty.event_types.info.ResearchMembershipHandler), ('SALARY', faculty.event_types.career.SalaryBaseEventHandler), ('STIPEND', faculty.event_types.career.SalaryModificationEventHandler), ('SPCL_DEAL', faculty.event_types.info.SpecialDealHandler), ('STUDYLEAVE', faculty.event_types.career.StudyLeaveEventHandler), ('TEACHING', faculty.event_types.awards.TeachingCreditEventHandler), ('TENUREAPP', faculty.event_types.career.TenureApplicationEventHandler), ('ACCRED', faculty.event_types.career.AccreditationFlagEventHandler), ('PROMOTION', faculty.event_types.career.PromotionApplicationEventHandler), ('SALARYREV', faculty.event_types.career.SalaryReviewEventHandler), ('CONTRACTRV', faculty.event_types.career.ContractReviewEventHandler), ('RESUME', faculty.event_types.info.ResumeEventHandler)], max_length=10),
        ),
        migrations.AlterField(
            model_name='careerevent',
            name='flags',
            field=bitfield.models.BitField(['affects_teaching', 'affects_salary'], default=0),
        ),
        migrations.AlterField(
            model_name='careerevent',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='career_events', to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='careerevent',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='slug_string', unique_with=('person',)),
        ),
        migrations.AlterField(
            model_name='careerevent',
            name='status',
            field=models.CharField(choices=[('NA', 'Needs Approval'), ('A', 'Approved'), ('D', 'Deleted')], default='', max_length=2),
        ),
        migrations.AlterField(
            model_name='careerevent',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='documentattachment',
            name='career_event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attachments', to='faculty.CareerEvent'),
        ),
        migrations.AlterField(
            model_name='documentattachment',
            name='contents',
            field=models.FileField(max_length=500, storage=django.core.files.storage.FileSystemStorage(base_url=None, location='submitted_files'), upload_to=faculty.models.attachment_upload_to),
        ),
        migrations.AlterField(
            model_name='documentattachment',
            name='created_by',
            field=models.ForeignKey(help_text='Document attachment created by.', on_delete=django.db.models.deletion.PROTECT, to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='documentattachment',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='title', unique_with=('career_event',)),
        ),
        migrations.AlterField(
            model_name='eventconfig',
            name='config',
            field=courselib.json_fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='eventconfig',
            name='event_type',
            field=models.CharField(choices=[('ADMINPOS', faculty.event_types.position.AdminPositionEventHandler), ('APPOINT', faculty.event_types.career.AppointmentEventHandler), ('AWARD', faculty.event_types.awards.AwardEventHandler), ('COMMITTEE', faculty.event_types.info.CommitteeMemberHandler), ('EXTERN_AFF', faculty.event_types.info.ExternalAffiliationHandler), ('EXTSERVICE', faculty.event_types.info.ExternalServiceHandler), ('FELLOW', faculty.event_types.awards.FellowshipEventHandler), ('GRANTAPP', faculty.event_types.awards.GrantApplicationEventHandler), ('NORM_TEACH', faculty.event_types.teaching.NormalTeachingLoadHandler), ('LEAVE', faculty.event_types.career.OnLeaveEventHandler), ('ONE_NINE', faculty.event_types.teaching.OneInNineHandler), ('OTHER_NOTE', faculty.event_types.info.OtherEventHandler), ('LABMEMB', faculty.event_types.info.ResearchMembershipHandler), ('SALARY', faculty.event_types.career.SalaryBaseEventHandler), ('STIPEND', faculty.event_types.career.SalaryModificationEventHandler), ('SPCL_DEAL', faculty.event_types.info.SpecialDealHandler), ('STUDYLEAVE', faculty.event_types.career.StudyLeaveEventHandler), ('TEACHING', faculty.event_types.awards.TeachingCreditEventHandler), ('TENUREAPP', faculty.event_types.career.TenureApplicationEventHandler), ('ACCRED', faculty.event_types.career.AccreditationFlagEventHandler), ('PROMOTION', faculty.event_types.career.PromotionApplicationEventHandler), ('SALARYREV', faculty.event_types.career.SalaryReviewEventHandler), ('CONTRACTRV', faculty.event_types.career.ContractReviewEventHandler), ('RESUME', faculty.event_types.info.ResumeEventHandler)], max_length=10),
        ),
        migrations.AlterField(
            model_name='eventconfig',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='facultymemberinfo',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='Birthdate'),
        ),
        migrations.AlterField(
            model_name='facultymemberinfo',
            name='config',
            field=courselib.json_fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='facultymemberinfo',
            name='emergency_contact',
            field=models.TextField(blank=True, verbose_name='Emergency Contact Information'),
        ),
        migrations.AlterField(
            model_name='facultymemberinfo',
            name='office_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Office'),
        ),
        migrations.AlterField(
            model_name='facultymemberinfo',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='facultymemberinfo',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Local Phone Number'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='config',
            field=courselib.json_fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='grant',
            name='import_key',
            field=models.CharField(blank=True, help_text="e.g. 'nserc-43517b4fd422423382baab1e916e7f63'", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='grant',
            name='initial',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Initial balance'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='label',
            field=models.CharField(db_index=True, help_text='for identification from FAST import', max_length=150),
        ),
        migrations.AlterField(
            model_name='grant',
            name='overhead',
            field=models.DecimalField(decimal_places=2, help_text='Annual overhead returned to Faculty budget', max_digits=12, verbose_name='Annual overhead'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='owners',
            field=models.ManyToManyField(help_text='Who owns/controls this grant?', through='faculty.GrantOwner', to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='project_code',
            field=models.CharField(db_index=True, help_text="The fund and project code, like '13-123456'", max_length=32),
        ),
        migrations.AlterField(
            model_name='grant',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='title', unique_with=('unit',)),
        ),
        migrations.AlterField(
            model_name='grant',
            name='status',
            field=models.CharField(choices=[('A', 'Active'), ('D', 'Deleted')], default='A', max_length=2),
        ),
        migrations.AlterField(
            model_name='grant',
            name='title',
            field=models.CharField(help_text='Label for the grant within this system', max_length=64),
        ),
        migrations.AlterField(
            model_name='grant',
            name='unit',
            field=models.ForeignKey(help_text='Unit who owns the grant', on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='grantbalance',
            name='actual',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='YTD actual'),
        ),
        migrations.AlterField(
            model_name='grantbalance',
            name='balance',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='grant balance'),
        ),
        migrations.AlterField(
            model_name='grantbalance',
            name='config',
            field=courselib.json_fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='grantbalance',
            name='grant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='faculty.Grant'),
        ),
        migrations.AlterField(
            model_name='grantbalance',
            name='month',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='current month'),
        ),
        migrations.AlterField(
            model_name='grantowner',
            name='config',
            field=courselib.json_fields.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='grantowner',
            name='grant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='faculty.Grant'),
        ),
        migrations.AlterField(
            model_name='grantowner',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='career_event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='faculty.CareerEvent'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='cc_lines',
            field=models.TextField(blank=True, help_text='Additional recipients of the memo', null=True, verbose_name='CC lines'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='config',
            field=courselib.json_fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='memo',
            name='created_by',
            field=models.ForeignKey(help_text='Letter generation requested by.', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='from_lines',
            field=models.TextField(help_text='Name (and title) of the sender, e.g. "John Smith, Applied Sciences, Dean"', verbose_name='From'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='from_person',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='is_letter',
            field=models.BooleanField(default=False, help_text='Make it a letter with correct letterhead instead of a memo.', verbose_name='Make it a letter'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='memo_text',
            field=models.TextField(help_text="I.e. 'Congratulations on ... '"),
        ),
        migrations.AlterField(
            model_name='memo',
            name='sent_date',
            field=models.DateField(default=datetime.date.today, help_text='The sending date of the letter'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique_with=('career_event',)),
        ),
        migrations.AlterField(
            model_name='memo',
            name='subject',
            field=models.TextField(help_text='The subject of the memo (lines will be formatted separately in the memo header). This will be ignored for letters'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='faculty.MemoTemplate'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='to_lines',
            field=models.TextField(blank=True, help_text='Recipient of the memo', null=True, verbose_name='Attention'),
        ),
        migrations.AlterField(
            model_name='memo',
            name='unit',
            field=models.ForeignKey(help_text='The unit producing the memo: will determine the letterhead used for the memo.', on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='created_by',
            field=models.ForeignKey(help_text='Memo template created by.', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='default_from',
            field=models.CharField(blank=True, help_text='The default sender of the memo', max_length=255, verbose_name='Default From'),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='event_type',
            field=models.CharField(choices=[('ADMINPOS', faculty.event_types.position.AdminPositionEventHandler), ('APPOINT', faculty.event_types.career.AppointmentEventHandler), ('AWARD', faculty.event_types.awards.AwardEventHandler), ('COMMITTEE', faculty.event_types.info.CommitteeMemberHandler), ('EXTERN_AFF', faculty.event_types.info.ExternalAffiliationHandler), ('EXTSERVICE', faculty.event_types.info.ExternalServiceHandler), ('FELLOW', faculty.event_types.awards.FellowshipEventHandler), ('GRANTAPP', faculty.event_types.awards.GrantApplicationEventHandler), ('NORM_TEACH', faculty.event_types.teaching.NormalTeachingLoadHandler), ('LEAVE', faculty.event_types.career.OnLeaveEventHandler), ('ONE_NINE', faculty.event_types.teaching.OneInNineHandler), ('OTHER_NOTE', faculty.event_types.info.OtherEventHandler), ('LABMEMB', faculty.event_types.info.ResearchMembershipHandler), ('SALARY', faculty.event_types.career.SalaryBaseEventHandler), ('STIPEND', faculty.event_types.career.SalaryModificationEventHandler), ('SPCL_DEAL', faculty.event_types.info.SpecialDealHandler), ('STUDYLEAVE', faculty.event_types.career.StudyLeaveEventHandler), ('TEACHING', faculty.event_types.awards.TeachingCreditEventHandler), ('TENUREAPP', faculty.event_types.career.TenureApplicationEventHandler), ('ACCRED', faculty.event_types.career.AccreditationFlagEventHandler), ('PROMOTION', faculty.event_types.career.PromotionApplicationEventHandler), ('SALARYREV', faculty.event_types.career.SalaryReviewEventHandler), ('CONTRACTRV', faculty.event_types.career.ContractReviewEventHandler), ('RESUME', faculty.event_types.info.ResumeEventHandler)], help_text='The type of event that this memo applies to', max_length=10),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='is_letter',
            field=models.BooleanField(default=False, help_text='Should this be a letter by default', verbose_name='Make it a letter'),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='label',
            field=models.CharField(help_text='The name for this template (that you select it by when using it)', max_length=150, verbose_name='Template Name'),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique=True),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='subject',
            field=models.CharField(help_text='The default subject of the memo. Will be ignored for letters', max_length=255, verbose_name='Default Subject'),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='template_text',
            field=models.TextField(help_text="The template for the memo. It may be edited when creating each memo. (i.e. 'Congratulations {{first_name}} on ... ')"),
        ),
        migrations.AlterField(
            model_name='memotemplate',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='position',
            name='degree1',
            field=models.CharField(default='', max_length=12),
        ),
        migrations.AlterField(
            model_name='position',
            name='degree2',
            field=models.CharField(default='', max_length=12),
        ),
        migrations.AlterField(
            model_name='position',
            name='degree3',
            field=models.CharField(default='', max_length=12),
        ),
        migrations.AlterField(
            model_name='position',
            name='institution1',
            field=models.CharField(default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='position',
            name='institution2',
            field=models.CharField(default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='position',
            name='institution3',
            field=models.CharField(default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='position',
            name='location1',
            field=models.CharField(default='', max_length=23),
        ),
        migrations.AlterField(
            model_name='position',
            name='location2',
            field=models.CharField(default='', max_length=23),
        ),
        migrations.AlterField(
            model_name='position',
            name='location3',
            field=models.CharField(default='', max_length=23),
        ),
        migrations.AlterField(
            model_name='position',
            name='percentage',
            field=models.DecimalField(blank=True, decimal_places=2, default=100, help_text='Percentage of this position in the given unit', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='projected_start_date',
            field=models.DateField(default=faculty.models.timezone_today, verbose_name='Projected Start Date'),
        ),
        migrations.AlterField(
            model_name='position',
            name='rank',
            field=models.CharField(blank=True, choices=[('LLEC', 'Limited-Term Lecturer'), ('LABI', 'Laboratory Instructor'), ('LECT', 'Lecturer'), ('SLEC', 'Senior Lecturer'), ('INST', 'Instructor'), ('ASSI', 'Assistant Professor'), ('ASSO', 'Associate Professor'), ('FULL', 'Full Professor'), ('URAS', 'University Research Associate'), ('ADJC', 'Adjunct Professor')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='position',
            name='year1',
            field=models.CharField(default='', max_length=5),
        ),
        migrations.AlterField(
            model_name='position',
            name='year2',
            field=models.CharField(default='', max_length=5),
        ),
        migrations.AlterField(
            model_name='position',
            name='year3',
            field=models.CharField(default='', max_length=5),
        ),
        migrations.AlterField(
            model_name='positiondocumentattachment',
            name='contents',
            field=models.FileField(max_length=500, storage=django.core.files.storage.FileSystemStorage(base_url=None, location='submitted_files'), upload_to=faculty.models.position_attachment_upload_to),
        ),
        migrations.AlterField(
            model_name='positiondocumentattachment',
            name='created_by',
            field=models.ForeignKey(help_text='Document attachment created by.', on_delete=django.db.models.deletion.PROTECT, to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='positiondocumentattachment',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attachments', to='faculty.Position'),
        ),
        migrations.AlterField(
            model_name='positiondocumentattachment',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='title', unique_with=('position',)),
        ),
        migrations.AlterField(
            model_name='tempgrant',
            name='config',
            field=courselib.json_fields.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='tempgrant',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='coredata.Person'),
        ),
        migrations.AlterField(
            model_name='tempgrant',
            name='import_key',
            field=models.CharField(blank=True, help_text="e.g. 'nserc-43517b4fd422423382baab1e916e7f63'", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tempgrant',
            name='initial',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='initial balance'),
        ),
        migrations.AlterField(
            model_name='tempgrant',
            name='label',
            field=models.CharField(help_text='for identification from FAST import', max_length=150),
        ),
        migrations.AlterField(
            model_name='tempgrant',
            name='project_code',
            field=models.CharField(help_text="The fund and project code, like '13-123456'", max_length=32),
        ),
    ]