"""A script to first delete the contents of the new jobs module and then import data from the old jobs module"""

from os import getcwd
from importlib import import_module
import psycopg2
from datetime import datetime
import pytz
import numpy as np
import pandas as pd

old_job_ids = pd.read_csv('job_order.csv')['old_id']

con = psycopg2.connect("dbname=geo4 host=10.78.81.3 user=geo password=Hk&x:dZ=wt3bq/}#")


class Model:
    """"""
    def __init__(self, app):
        self.app = app

    def get(self, model):
        package = import_module(self.app + '.models') 
        m = getattr(package, model)
        return(m)

    def delete_content(self, model):
        for i in model.objects.all():
            i.delete()

    def reset_sequence(self, table):
        sql = """ALTER SEQUENCE %s_id_seq RESTART WITH 1"""
        cur = con.cursor()
        try:
            cur.execute(sql % table)
            con.commit()
        except Exception as e:
            print(e)
        cur.close()




class Old(Model):
    """"""
    def __init__(self):
        self.app = 'old'
        self.model = Model(self.app)

    def get_jobs(self):
        model = self.model.get('Job')
        jobs = [model.objects.get(id=i) for i in old_job_ids]
        return(jobs)
 
    def get_datetime(self, job):
        date = job.open
        y, m, d = date.year, date.month, date.day
        dt = datetime(y, m, d, 9, 0, 0, 0, tzinfo=pytz.UTC)
        return(dt)

    def old_to_new_id(self, old_id):
        o = old_job_ids
        new_id = o[o==old_id].index.values[0] + 1
        return(new_id)


class Contact(Model):
    """"""
    def __init__(self):
        self.app = 'contact'
        self.model_list = [
            'Organisation', 
            'Contact', 
            'Name',
        ]
        self.model = Model(self.app)
        self.old = Old()

    def delete(self):
        for i in self.model_list:
            m = self.model
            model = m.get(i)
            m.delete_content(model)
            self.reset(i)

    def reset(self, model_name):
        table = self.app + '_' + model_name.lower()
        self.model.reset_sequence(table)

    def populate(self):
        for i in self.old.get_jobs():
            self.new_organisation(i)
            self.new_contact(i)

    def new_organisation(self, old_job):
        o = old_job.client.organisation
        m = self.model.get('Organisation')
        abbr = o.abbreviation
        try:
            m.objects.get(abbr=abbr)
        except:
            name = o.name if o.name else abbr
            org = m(name=name, abbr=abbr, note=o.notes)
            org.save()
            dt = self.old.get_datetime(old_job)
            m.objects.filter(abbr=abbr).update(timestamp=dt)

    def new_contact(self, old_job):
        client = old_job.client
        first = client.firstname
        last = client.lastname
        note = client.notes
        cm = self.model.get('Contact')
        nm = self.model.get('Name')
        try:
            nm.objects.get(first=first, last=last)
        except:
            dt = self.old.get_datetime(old_job)
            c = cm(note=note)
            c.save()
            cm.objects.filter(id=c.id).update(timestamp=dt)
            # handle a change of name case
            if last == 'Barry':
                laressa = nm.objects.get(last='Berehowyj')
                c = cm.objects.get(id=laressa.id)
            n = nm(contact=c, first=first, last=last)
            n.save()
            nm.objects.filter(first=first, last=last).update(timestamp=dt)

            

class Element(Model):
    """"""
    def __init__(self):
        self.app = 'element'
        self.model_list = [
            'Element', 
            'Factor'
        ]
        self.model = Model(self.app)
        self.old = Old()

    def delete(self):
        for i in self.model_list:
            m = self.model
            model = m.get(i)
            m.delete_content(model)
            self.reset(i)

    def reset(self, model_name):
        table = self.app + '_' + model_name.lower()
        self.model.reset_sequence(table)

    def get_df(self):
        df = self.merge_elements()
        df['order'] = None
        for i in df.index:
            self.order_element(df, i)

        new_job_id = [self.old.old_to_new_id(i) for i in df['job']]
        df['new_job_id'] = new_job_id
        df.sort_values(['new_job_id', 'order'], inplace=True)
        df.reset_index(inplace=True, drop=True)
        df['idx'] = df.index.values + 1

        cols = df.columns.values
        corder = [10,0,9,3,4,1,5,6,2,7,8]
        df = df[cols[corder]]

        jobs = df['job']
        for i in jobs:
            try:
                if i != j:
                    group += 1
            except:
                j = jobs[0]
                group = 1
                lst = []
            j = i
            lst += [group]
        df['group'] = lst

        df.to_csv('elements.csv', index=False)
        return(df)

    def merge_elements(self):
        f = self.factors_to_df()
        e = self.elements_to_df()
        r = self.ranks_to_df()
        a = pd.merge(f, e, how='outer', left_on='id', right_on='factor')
        b = pd.merge(a, r, how='outer', left_on='id_y', right_on='child')
        cols = b.columns.values
        cols[[3,4,7]] = ['note_factor', 'element', 'note_element']
        b.columns = cols
        b.drop(['id_x', 'id', 'child'], axis=1, inplace=True)
        return(b)

    def factors_to_df(self):
        m = self.old.model.get('Factor')
        f = m.objects.all().order_by('id')
        df = pd.DataFrame([(i.id, i.job_id, i.label, i.notes) for i in f])
        df.columns = ['id', 'job', 'label', 'note']
        return(df)

    def elements_to_df(self):
        m = self.old.model.get('Element')
        e = m.objects.all().order_by('id')
        df = pd.DataFrame([(i.id, i.factor_id, i.value, i.notes) for i in e])
        df.columns = ['id', 'factor', 'value', 'note']
        return(df)

    def ranks_to_df(self):
        m = self.old.model.get('Rank')
        r = m.objects.all().order_by('id')
        df = pd.DataFrame([(i.id, i.parent_id, i.child_id) for i in r])
        df.columns = ['id', 'parent', 'child']
        return(df)

    def order_element(self, df, i):
        p = df.loc[i, 'parent']
        if pd.isnull(p):
            df.loc[i, 'order'] = 1
        else:
            order = df.loc[df['element']==int(p), 'order'] + 1
            order = order.values[0]
            # handle a single case where the child comes before parent in the list
            df.loc[i, 'order'] = 2 if pd.isnull(order) else order

    def populate(self):
        df = self.get_df()
        for n, i in df.iterrows():
            parent = df.loc[df['element']==i.parent] 
            self.create_element(n, i, parent)


    def create_element(self, idx, old_dat, parent_dat):
        o = old_dat
        m = self.model.get('Factor')
        factor = o.label
        try:
            f = m.objects.get(group=o.group, factor=o.label, note=o.note_factor)
        except:
            f = m(group=o.group, factor=o.label, note=o.note_factor)
            f.save()

        if len(parent_dat.index) == 1:
            m = self.model.get('Element')
            p_id = parent_dat.iloc[0].idx
            parent = m.objects.get(id=p_id)
        else:
            parent = None
        m = self.model.get('Element')
        e = m(factor=f, value=o.value, parent=parent, note=o.note_element)
        e.save()


class Sample(Model):
    """"""
    def __init__(self):
        self.app = 'sample'
        self.model_list = [
            'Element', 
            'Factor'
        ]
        self.model = Model(self.app)
        self.old = Old()

    def delete(self):
        for i in self.model_list:
            m = self.model
            model = m.get(i)
            m.delete_content(model)
            self.reset(i)

    def reset(self, model_name):
        table = self.app + '_' + model_name.lower()
        self.model.reset_sequence(table)

    def populate(self):
        df = self.get_factors()
        for n, i in df.iterrows():
            parent = df.loc[df['element']==i.parent] 
            self.element(n, i, parent)


class Job(Model):
    """"""
    def __init__(self):
        self.app = 'job'
        self.model_list = [
            'Job', 
            'Title', 
            'Status', 
            'Location', 
            'Contact',
            'Element',
        ]
        self.model = Model(self.app)
        self.old = Old()
        self.elements = Element().get_df()

    def delete(self):
        for i in self.model_list:
            m = self.model
            model = m.get(i)
            m.delete_content(model)
            self.reset(i)

    def reset(self, model_name):
        table = self.app + '_' + model_name.lower()
        self.model.reset_sequence(table)

    def populate(self):
        for i in self.old.get_jobs():
            j = self.job(i)
            self.title(i, j)
            self.status(i, j)
            self.location(i, j)
            self.contact(i, j)
            self.element(j)

    def job(self, old_job):
        """"""
        o = old_job
        m = self.model.get('Job')
        j = m(note=o.notes)
        j.save()
        dt = self.old.get_datetime(o)
        m.objects.filter(id=j.id).update(timestamp=dt)
        return(j)

    def title(self, old_job, new_job):
        """"""
        o, j = old_job, new_job
        m = self.model.get('Title')
        t = m(job=j, title=o.description)
        t.save()
        m.objects.filter(job_id=j.id).update(timestamp=j.timestamp)

    def status(self, old_job, new_job):
        o, j = old_job, new_job
        m = self.model.get('Status')
        s = m(job=j, status=True)
        s.save()
        m.objects.filter(job_id=j.id).update(timestamp=j.timestamp)

    def location(self, old_job, new_job):
        o, j = old_job, new_job
        location = o.location
        if location:
            m = self.model.get('Location')
            description = location.description
            note = location.notes
            l = m(job=j, location=description, note=note)
            l.save()
            m.objects.filter(job_id=j).update(timestamp=j.timestamp)

    def contact(self, old_job, new_job):
        o, j = old_job, new_job
        client = o.client
        first = client.firstname
        last = client.lastname
        abbr = client.organisation.abbreviation
        m = Contact().model.get('Name')
        name = m.objects.get(first=first, last=last)
        m = Contact().model.get('Organisation')
        org = m.objects.get(abbr=abbr)
        m = self.model.get('Contact')
        c = m(job=j, contact=name.contact, organisation=org)
        c.save()

    def element(self, new_job):
        df = self.elements
        r = df.loc[df['new_job_id']==new_job.id]
        m = self.model.get('Element')
        for n, i in r.iterrows():
            e = m(job=new_job, element_id=i.idx)
            e.save()
        

def transfer_receipts():
    df = pd.read_csv('receipt.csv')
    print(df)
    from old.models import Receipt
    #r = Receipt
    for n, i in df.iterrows():
        #print(i)
        r = Receipt(upload=i.upload, date=i.date, value=i.value, description=i.description, note=i.note, category=i.category, currency=i.currency)
        #r = Receipt(upload=i.upload)
        #print(dir(r))
        r.save()


def upload_receipts():
    """"""


#c = Contact()
#c.delete()
#c.populate()

#e = Element()
#e.delete()
#e.populate()

#s = Sample()
#s.delete()
#s.populate()

#j = Job()
#j.delete()
#j.populate()

receipts()

exit()


 
from contact.models import Organisation
from old.models import Job as OldJob, JobStatus as OldJobStatus, Location as OldLocation, Client as OldClient, Organisation as OldOrganisation

class OldModels:
    models = ['Organisation', 'Client', 'Location', 'Job', 'JobStatus', 'Closure', 'Invoice', 'Quote', 'Receipt', 'Factor', 'Element', 'Rank', 'ASC', 'Sample', 'PSA']
    d = dict(zip(models, [get_module(i, 'old.models') for i in models]))
    job_order = pd.read_csv('job_order.csv')
    old_id = job_order['old_id']
 
    def get_id(self, i):
        """"""
        m = self.d['Job']
        o = m.objects.get(id=i)
        o.datetime = self.get_datetime(o)
        return(o)

    def get_datetime(self, job):
        date = job.open
        y, m, d = date.year, date.month, date.day
        dt = datetime(y, m, d, 9, 0, 0, 0, tzinfo=pytz.UTC)
        return(dt)

    def factors_to_df(self):
        f = self.d['Factor'].objects.all().order_by('id')
        df = pd.DataFrame([(i.id, i.job_id, i.label, i.notes) for i in f])
        df.columns = ['id', 'job', 'label', 'note']
        #df.to_csv('factors.csv', index=False)
        return(df)

    def elements_to_df(self):
        e = self.d['Element'].objects.all().order_by('id')
        df = pd.DataFrame([(i.id, i.factor_id, i.value, i.notes) for i in e])
        df.columns = ['id', 'factor', 'value', 'note']
        #df.to_csv('elements.csv', index=False)
        return(df)

    def ranks_to_df(self):
        r = self.d['Rank'].objects.all().order_by('id')
        df = pd.DataFrame([(i.id, i.parent_id, i.child_id) for i in r])
        df.columns = ['id', 'parent', 'child']
        #rdf.to_csv('ranks.csv', index=False)
        return(df)

    def merge_elements(self):
        f = self.factors_to_df()
        e = self.elements_to_df()
        r = self.ranks_to_df()
        
        a = pd.merge(f, e, how='outer', left_on='id', right_on='factor')
        b = pd.merge(a, r, how='outer', left_on='id_y', right_on='child')
        #b.drop(['id_x'], axis=1, inplace=True)
        cols = b.columns.values
        cols[[3,4,7]] = ['note_factor', 'element', 'note_element']
        b.columns = cols
        b.drop(['id_x', 'id', 'child'], axis=1, inplace=True)
        return(b)

    def order_element(self, df, i):
        p = df.loc[i, 'parent']
        if pd.isnull(p):
            df.loc[i, 'order'] = 1
        else:
            order = df.loc[df['element']==int(p), 'order'] + 1
            order = order.values[0]
            # handle a single case where the child comes before parent in the list
            df.loc[i, 'order'] = 2 if pd.isnull(order) else order

    def get_factors(self):
        df = self.merge_elements()
        df['order'] = None
        for i in df.index:
            self.order_element(df, i)
        new_job_id = [get_new_id(i) for i in df['job']]
        df['new_job_id'] = new_job_id
        df.sort_values(['new_job_id', 'order'], inplace=True)
        df.reset_index(inplace=True)
        df['index'] = df.index + 1
        cols = df.columns.values
        corder = [0,1,10,4,5,2,6,7,3,8,9]
        df = df[cols[corder]]
        df.loc[df['parent'].isnull(), 'parent'] = 0

        lst = []
        for n, i in df.iterrows():
            lst += [np.nan] if i.parent == 0 else [df.loc[df['element']==i.parent, 'index'].item()]
        df['new_parent'] = lst

        df.to_csv('merged_elements.csv', index=False)
        return(df)


class ContactTrans:
    models = ['Organisation', 'Contact', 'Name']
    d = dict(zip(models, [get_module(i, 'contact.models') for i in models]))

    def delete(self):
        for i in self.d.keys():
            delete_content(self.d[i])

    def reset(self):
        for i in self.models:
            table = 'contact_' + i.lower()
            reset_sequence(table)



    def contact(self, cdict):
        mcont = self.d['Contact']
        mname = self.d['Name']
        firstname, lastname = cdict['firstname'], cdict['lastname']
        try:
            idx = mname.objects.get(first=firstname, last=lastname).contact
            c = mcont.objects.get(id=idx)
        except:
            if lastname != 'Barry':
                c = mcont()
                c.save()
                mcont.objects.filter(id=c.id).update(timestamp=cdict['datetime'])
            else:
                c = mname.objects.get(last='Berehowyj').contact
            n = mname(contact=c, first=firstname, last=lastname)
            n.save()
            mname.objects.filter(first=firstname, last=lastname).update(timestamp=cdict['datetime'])

        return(c)
                

    def organisation(self, odict):
        """Add organisation if it doesn't exist."""
        m = self.d['Organisation']
        name = odict['name']
        abbr = odict['abbr']
        note = odict['note']
        try:
            o = m.objects.get(abbr=abbr)
        except:
            name = name if name else abbr
            o = m(name=name, abbr=abbr, note=note)
            o.save()
            m.objects.filter(abbr=abbr).update(timestamp=odict['datetime'])
        return(o)

   

class JobTrans(GetModel):
    models = ['Job', 'Title', 'Status', 'Location', 'Contact']
    #d = dict(zip(models, [get_module(i, 'job.models') for i in models]))
    #job_order = pd.read_csv('job_order.csv')
    #old_id = job_order['old_id']
    #ctrans = ContactTrans()
    app = 'job'

    def __init__(self):
        self.model = GetModel('job')
        wee = self.model.get('Job')
        print('weewee')
        exit()
        self.delete()
        self.reset()
        self.ctrans.delete()
        self.ctrans.reset()
        for i in self.old_id:
            print(i)
            o = OldModels().get_id(i)
            j = self.job(o)
            self.title(j, o)
            self.status(j, o)
            self.location(j, o)
            self.contact(j, o)
                
    def delete(self):
        for i in self.d.keys():
            delete_content(self.d[i])

    def reset(self):
        for i in self.models:
            table = 'job_' + i.lower()
            reset_sequence(table)

    def job(self, old_job):
        """"""
        m = self.d['Job']
        j = m(note=old_job.notes, directory=old_job.id)
        j.save()
        m.objects.filter(id=j.id).update(timestamp=old_job.datetime)
        return(j)

    def title(self, j, old_job):
        """"""
        m = self.d['Title']
        t = m(job=j, title=old_job.description)
        t.save()
        m.objects.filter(job_id=j.id).update(timestamp=old_job.datetime)

    def status(self, j, old_job):
        m = self.d['Status']
        s = m(job=j, status=True)
        s.save()
        m.objects.filter(job_id=j.id).update(timestamp=old_job.datetime)

    def location(self, j, old_job):
        if old_job.location:
            m = self.d['Location']
            l = m(job=j, location=old_job.location)
            l.save()
            m.objects.filter(job_id=j.id).update(timestamp=old_job.datetime)

    def contact(self, j, old_job):
        c = old_job.client
        o = c.organisation

        cdict = {
            'firstname': c.firstname,
            'lastname': c.lastname,
            'status': c.status,
            'note': c.notes,
            'datetime': old_job.datetime,
            'name_change': [('Barry', 'Berehowyj')],
        }

        cnct = self.ctrans.contact(cdict) 

        odict = {
            'name': o.name,
            'abbr': o.abbreviation,
            'note': o.notes,
            'datetime': old_job.datetime,
        }

        org = self.ctrans.organisation(odict) 

        m = self.d['Contact']
        job_contact = m(job=j, contact=cnct, organisation=org)
        job_contact.save()
        m.objects.filter(job=j).update(timestamp=old_job.datetime)

class ElementTrans:
    models = ['Element', 'Factor']
    d = dict(zip(models, [get_module(i, 'element.models') for i in models]))
    job_order = pd.read_csv('job_order.csv')
    old_id = job_order['old_id']
    old_models = OldModels()
 
    def __init__(self):
        self.delete()
        self.reset()

        df = self.subset_factors()
        for n, i in df.iterrows():
            p = df.loc[(df['new_job_id']==i.new_job_id) & (df['order']==i.order-1)]
            parent = None if p.empty else p.id.item()
            factor = self.d['Factor'](job_id=i.new_job_id, factor=i.label, parent_id=parent, note=i.note_factor)
            factor.save()
            
        df = self.subset_elements()
        for n, i in df.iterrows():
            f = self.d['Factor'].objects.get(job_id=i.new_job_id, factor=i.label)
            e = self.d['Element'](factor=f, value=i.value, note=i.note_element)
            e.save()

    def get_elements(self):
        df = self.old_models.get_factors()
        df = df.loc[df['note_factor']!='Dont know what this job is for'] 
        return(df)

    def subset_factors(self):
        df = self.get_elements()
        f = df[['new_job_id', 'label', 'order', 'note_factor']].drop_duplicates()
        f.reset_index(drop=True, inplace=True)
        f['id'] = f.index.values + 1
        return(f)

    def subset_elements(self):
        df = self.get_elements()
        df = df[['new_job_id', 'label', 'value', 'note_element']]
        return(df)

    def delete(self):
        for i in self.d.keys():
            delete_content(self.d[i])

    def reset(self):
        for i in self.models:
            table = 'element_' + i.lower()
            reset_sequence(table)


class ElementTrans2:
    models = ['Element', 'Factor']
    d = dict(zip(models, [get_module(i, 'element.models') for i in models]))
    job_order = pd.read_csv('job_order.csv')
    old_id = job_order['old_id']
    old_models = OldModels()
 
    def __init__(self):
        self.delete()
        self.reset()

        f = self.d['Factor'](group='wee')
        exit()

        df = self.subset_factors()
        print(df)
        exit()
        for n, i in df.iterrows():
            pass
            #p = df.loc[(df['new_job_id']==i.new_job_id) & (df['order']==i.order-1)]
            #parent = None if p.empty else p.id.item()
            f = self.d['Factor']

            #factor = self.d['Factor2'](group=str(i.new_job_id), factor=i.label, note=i.note_factor)
            factor = f(group='poo')
            #factor.save()
            
        exit()
        #df = self.subset_elements()
        #for n, i in df.iterrows():
        #    f = self.d['Factor'].objects.get(job_id=i.new_job_id, factor=i.label)
        #    e = self.d['Element'](factor=f, value=i.value, note=i.note_element)
        #    e.save()

    def get_elements(self):
        df = self.old_models.get_factors()
        df = df.loc[df['note_factor']!='Dont know what this job is for'] 
        return(df)

    def subset_factors(self):
        df = self.get_elements()
        f = df[['new_job_id', 'label', 'order', 'note_factor']].drop_duplicates()
        f.reset_index(drop=True, inplace=True)
        f['id'] = f.index.values + 1
        return(f)

    def subset_elements(self):
        df = self.get_elements()
        df = df[['new_job_id', 'label', 'value', 'note_element']]
        return(df)

    def delete(self):
        for i in self.d.keys():
            delete_content(self.d[i])

    def reset(self):
        for i in self.models:
            table = 'element_' + i.lower()
            reset_sequence(table)

  

JobTrans()
#ElementTrans()
#ElementTrans2()
con.close()


