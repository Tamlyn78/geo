from os.path import join, splitext
from uuid import uuid4
import datetime

from django.db import models
#from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

#@python_2_unicode_compatible  # only if you need to support Python 2
class Organisation(models.Model):
    name = models.TextField(max_length = None, null = True)
    abbreviation = models.TextField(max_length = None, null = True)
    address = models.TextField(max_length = None, blank = True, null = True)
    notes = models.TextField(max_length = None, blank = True, null = True)
    old_id = models.IntegerField(default = 0)

    class Meta:
        ordering = ('abbreviation',)
    
    def __str__(self):
        output = self.abbreviation if self.abbreviation else self.organisation
        return(str(output))

#@python_2_unicode_compatible  # only if you need to support Python 2
class Client(models.Model):
    organisation = models.ForeignKey(Organisation, to_field = 'id', on_delete = models.CASCADE, null = True)
    firstname = models.TextField(max_length = None, null = True)
    lastname = models.TextField(max_length = None, null = True)
    status = models.BooleanField(default=1)
    notes = models.TextField(max_length = None, blank = True, null = True)
    old_id = models.IntegerField(default = 0)

    class Meta:
        ordering = ('firstname',)
    
    def __str__(self):
        fullname = str(self.firstname) + ' ' + str(self.lastname)
        if self.organisation:
            fullname += ' at ' + str(self.organisation)
        return(fullname)
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class Location(models.Model):
    description = models.TextField(max_length = None)
    notes = models.TextField(max_length = None, blank = True, null = True)
    old_id = models.IntegerField(default = 0)
    
    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return(self.description)

#@python_2_unicode_compatible  # only if you need to support Python 2
class Job(models.Model):
    location = models.ForeignKey(Location, to_field = 'id', on_delete = models.CASCADE, blank = True, null = True)
    client = models.ForeignKey(Client, to_field = 'id', on_delete = models.CASCADE)
    description = models.TextField(max_length = None)
    open = models.DateField()
    notes = models.TextField(max_length = None, blank = True, null = True)
    old_id = models.IntegerField(default = 0)

    class Meta:
        ordering = ('-open',)
    
    def __str__(self):
        output = str(self.id) + ' ' + str(self.client) + ' ' + str(self.description)
        return(output)
        
    def get_absolute_url(self):
        return reverse('old:job_detail', args=[self.id])
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class JobStatus(models.Model):
    job = models.ForeignKey(Job, to_field = 'id', on_delete = models.CASCADE)
    date = models.DateField()
    status = models.BooleanField()
    notes = models.TextField(max_length = None, blank = True, null = True)
    
    class Meta:
        ordering = ('-date',)
    
    def __str__(self):
        output = str(job.id)
        return(output)
        
#@python_2_unicode_compatible
#class Manager(models.Model):
#    job = models.ForeignKey(Job, to_field = 'id', on_delete = models.CASCADE)
#    person = models.ForeignKey(User, to_field = 'id', on_delete = models.CASCADE, blank = True, null = True, related_name='person')
#    notes = models.TextField(max_length = None, blank = True, null = True)
#    
#    class Meta:
#        ordering = ('-job',)
#    
#    def __str__(self):
#        output = str(self.person)
#        return(output)
        
#@python_2_unicode_compatible
class Closure(models.Model):
    """All closed jobs"""
    job = models.ForeignKey(Job, to_field = 'id', on_delete = models.CASCADE)
    date = models.DateField(null = True, max_length = None, blank = True)
    notes = models.TextField(max_length = None, blank = True, null = True)
    
    class Meta:
        ordering = ('-date',)
    
    def __str__(self):
        output = str(self.job)
        return(output)
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class Invoice(models.Model):
    job = models.ForeignKey(Job, to_field = 'id', on_delete = models.CASCADE)
    date = models.DateField(null = True, max_length = None, blank = True)
    value = models.DecimalField(decimal_places=2, max_digits=13)
    payment_date = models.DateField(null = True, max_length = None, blank = True)
    notes = models.TextField(max_length = None, blank = True, null = True)
    
    class Meta:
        ordering = ('-id',)
    
    def __str__(self):
        output = str(self.id) + ' ' + str(self.date)
        return(output)
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class Quote(models.Model):
    job = models.ForeignKey(Job, to_field = 'id', on_delete = models.CASCADE, blank = True, null = True)
    date = models.DateField(null = True, max_length = None, blank = True)
    description = models.TextField(max_length = None, blank = True, null = True)
    status = models.NullBooleanField(default = None, blank = True, null = True)
    notes = models.TextField(max_length = None, blank = True, null = True)
    
    class Meta:
        ordering = ('-id',)
    
    def __str__(self):
        output = str(self.id) + ' ' + str(self.date)
        return(output)
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class Factor(models.Model):
    job = models.ForeignKey(Job, to_field = 'id', on_delete = models.CASCADE)
    label = models.TextField(max_length = None)
    notes = models.TextField(null = True, max_length = None, blank = True)
    
    class Meta:
        ordering = ('-id',)
    
    def __str__(self):
        output = str(self.job) + ' ' + str(self.label)
        output = str(self.label)
        return(output)
        
class Element(models.Model):
    factor = models.ForeignKey('Factor', to_field = 'id', on_delete = models.CASCADE)
    value = models.TextField(max_length = None)
    notes = models.TextField(null = True, max_length = None, blank = True)
    
    class Meta:
        ordering = ('-id',)
    
    def __str__(self):
        return(str(self.factor) + str(self.value))
        
class Rank(models.Model):
    parent = models.ForeignKey(Element, to_field = 'id', on_delete = models.CASCADE, related_name='parent_element')
    child = models.ForeignKey(Element, to_field = 'id', on_delete = models.CASCADE, related_name='child_element')

    class Meta:
        ordering = ('-id',)
    
    def __str__(self):
        return(str(self.parent) + str(self.child))
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class ASC(models.Model):
    element = models.ForeignKey(Element, to_field = 'id', on_delete = models.CASCADE)
    label = models.TextField(max_length = None, blank = True, null = True)
    unit_order = models.IntegerField(blank = True, null = True)
    horizon_prefix = models.IntegerField(blank = True, null = True)
    horizon = models.TextField(null = True, max_length = None, blank = True)
    horizon_suffix = models.IntegerField(blank = True, null = True)
    horizon_suffix2 = models.IntegerField(blank = True, null = True)
    upper_depth = models.FloatField(blank = True, null = True)
    lower_depth = models.FloatField(blank = True, null = True)
    colour = models.TextField(null = True, max_length = None, blank = True)
    hue_dry = models.TextField(null = True, max_length = None, blank = True)
    value_dry = models.TextField(null = True, max_length = None, blank = True)
    chroma_dry = models.TextField(null = True, max_length = None, blank = True)
    hue_moist = models.TextField(null = True, max_length = None, blank = True)
    value_moist = models.TextField(null = True, max_length = None, blank = True)
    chroma_moist = models.TextField(null = True, max_length = None, blank = True)
    field_texture = models.TextField(null = True, max_length = None, blank = True)
    texture_qualifier = models.TextField(null = True, max_length = None, blank = True)
    sand_size = models.TextField(null = True, max_length = None, blank = True)
    sand_sorting = models.TextField(null = True, max_length = None, blank = True)
    moisture = models.TextField(null = True, max_length = None, blank = True)
    strength = models.TextField(null = True, max_length = None, blank = True)
    structure_type = models.TextField(null = True, max_length = None, blank = True)
    structure_grade = models.TextField(null = True, max_length = None, blank = True)
    structure_size = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags_distribution = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags_abundance = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags_size = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags_roundness = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags_sphericity = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags_type = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags2_distribution = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags2_abundance = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags2_size = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags2_roundness = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags2_sphericity = models.TextField(null = True, max_length = None, blank = True)
    coarse_frags2_type = models.TextField(null = True, max_length = None, blank = True)
    voids_cracks = models.TextField(null = True, max_length = None, blank = True)
    voids_pore_size = models.TextField(null = True, max_length = None, blank = True)
    voids_pore_abundance = models.TextField(null = True, max_length = None, blank = True)
    roots1_size = models.TextField(null = True, max_length = None, blank = True)
    roots1_abundance = models.TextField(null = True, max_length = None, blank = True)
    roots2_size = models.TextField(null = True, max_length = None, blank = True)
    roots2_abundance = models.TextField(null = True, max_length = None, blank = True)
    segregations1_colour = models.TextField(null = True, max_length = None, blank = True)
    segregations1_abundance = models.TextField(null = True, max_length = None, blank = True)
    segregations1_size = models.TextField(null = True, max_length = None, blank = True)
    segregations1_form = models.TextField(null = True, max_length = None, blank = True)
    segregations2_colour = models.TextField(null = True, max_length = None, blank = True)
    segregations2_abundance = models.TextField(null = True, max_length = None, blank = True)
    segregations2_size = models.TextField(null = True, max_length = None, blank = True)
    segregations2_form = models.TextField(null = True, max_length = None, blank = True)
    lower_bound_dist = models.TextField(null = True, max_length = None, blank = True)
    lower_bound_shape = models.TextField(null = True, max_length = None, blank = True)
    notes = models.TextField(null = True, max_length = None, blank = True)
    data_entry_notes = models.TextField(null = True, max_length = None, blank = True)
    
    def __str__(self):
        return(str(self.element))
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class Sample(models.Model):
    element = models.ForeignKey(Element, to_field = 'id', on_delete = models.CASCADE)
    # date field here which would represent prep date
    field_label = models.TextField(null = True, max_length = None, blank = True)
    x_cm = models.FloatField(null = True, default = None, blank = True)
    y_cm = models.FloatField(null = True, default = None, blank = True)
    z_cm = models.FloatField(null = True, blank = True)
    upper_depth_cm = models.FloatField(null = True, blank = True)
    lower_depth_cm = models.FloatField(null = True, blank = True)
    sample_and_vessel_g = models.FloatField(null = True, blank = True)
    vessel_g = models.FloatField(null = True, blank = True)
    gravel_g = models.FloatField(null = True, blank = True)
    notes = models.TextField(null = True, max_length = None, blank = True)
    
    def __str__(self):
        return(str(self.element))
        
#@python_2_unicode_compatible  # only if you need to support Python 2
class PSA(models.Model):
    lab_id = models.IntegerField()
    sample = models.ForeignKey(Sample, to_field = 'id', on_delete = models.CASCADE)
    date = models.DateField(null = True, max_length = None, blank = True)
    notes = models.TextField(null = True, max_length = None, blank = True)
    
    def __str__(self):
        return(self.sample)
        
    
def rename_receipt(instance, filename):
    Y, m, d = instance.date.isoformat().split('-')
    upload_to = Y + '/' + m + '/' + d
    infile, ext = splitext(filename)
    outfile = '{}{}'.format(uuid4().hex, ext)
    outpath = join(upload_to, outfile)
    return(outpath)

class Receipt(models.Model):
    """A ledger of receipts. Experience uploading receipts has shown that multiple documents may be relevant for a single transaction; for example, an invoice from the University of Gloucestershire for OSL dating, and, a bankwest statement documenting the transaction. This probably argues for a singular document ledger with a field linking to one or multiple documents"""
    upload = models.FileField(upload_to=rename_receipt)
    date = models.DateField()
    value = models.DecimalField(max_digits=9, decimal_places=2)
    currency = models.TextField(default='AUD')
    RECEIPT_CHOICE = (
        ("asset", "Asset"),
        ("computer_part", "Computer Part"),
        ("computer_software", "Computer Software"),
        ("equipment_hire", "Equipment Hire"),
        ("equipment_repair", "Equipment Repair"), # this should be changed to 'equipment maintenance' to include repair, maintenance, and license fees (trailer rego)
        ("field_supplies", "Field Supplies"),
        ("hardware", "Hardware"),
        ("household", "Household"), # renovation and maintenance of home office property
        ("insurance", "Insurance"),
        ("it_service", "IT Service"),
        ("laboratory_chemicals", "Laboratory Chemicals"),
        ("laboratory_hardware", "Laboratory Hardware"),
        ("laboratory_services", "Laboratory Services"),
        ("laboratory_supplies", "Laboratory Supplies"),
        ("meals_and_accommodation", "Meals and Accommodation"),
        ("office_supplies", "Office Supplies"),
        ("phone", "Phone"),
        ("post", "Post"),
        ("professional_development", "Professional Development"),
        ("reference_material", "Reference Material"),
        ("travel", "Travel"),
        ("vehicle_accessories", "Vehicle Accessories"),
        ("vehicle_fuel", "Vehicle Fuel"),
        ("vehicle_insurance", "Vehicle Insurance"),
        ("vehicle_maintenance", "Vehicle Maintenance"),
        ("vehicle_registration", "Vehicle Registration"),
        ("wages_salary", "Wages/Salary"),
    )
    category = models.TextField(choices=RECEIPT_CHOICE, max_length=None, blank=True, null=True)
    description = models.TextField(max_length=None, blank=True, null=True)
    note = models.TextField(max_length=None, blank=True, null=True)

    class Meta:
        ordering = ('-id',)
    
    def __str__(self):
        output = str(self.description)
        return(output)
    
