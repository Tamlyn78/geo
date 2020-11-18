from django.db import models


class Contact(models.Model):
    """A list of contact unique identifiers."""
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-id', '-timestamp',)
        get_latest_by = 'timestamp'

    def __str__(self):
        return(str(self.id))


class Name(models.Model):
    """A list of contact names."""
    contact = models.ForeignKey(Contact, to_field='id', on_delete=models.CASCADE, related_name='contact_name')
    first = models.TextField(blank=True, null=True)
    middle = models.TextField(blank=True, null=True)
    last = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-last', '-first', '-timestamp',)
        get_latest_by = 'timestamp'

    def __str__(self):
        name = self.first if self.first else None
        name += ' ' + self.last if self.last else name
        return(name)


class Organisation(models.Model):
    name = models.TextField()
    abbr = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('abbr',)
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return(self.abbr)


