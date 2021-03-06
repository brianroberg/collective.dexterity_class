import datetime

from five import grok
from plone.directives import dexterity, form

from Acquisition import aq_inner
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from collective.z3cform.datetimewidget import DateFieldWidget

from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

from collective.dexteritytextindexer import searchable

from collective.dexterity_class import MessageFactory as _


@grok.provider(schema.interfaces.IContextSourceBinder)
def vocabProvider(context):
    """ pick up fruit list from parent """

    fruit_list = getattr(context.__parent__, 'available_fruits', [])
    return SimpleVocabulary.fromValues(fruit_list)

# Interface class; used to define content-type schema.

class IEverythingModel(form.Schema):
    """
    Everything type built via model.
    """
    
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/everything_model.xml to define the content type
    # and add directives here as necessary.
    
    form.model("models/everything_model.xml")

    fruit_choice = schema.Choice(title=_(u"Pick your fruit"), 
        source=vocabProvider)
    
    form.fieldset(
        "attachments", 
        label=_("Attachments"),
        fields=['file_upload', 'image_field'],
        )

    searchable('text_line')
    text_line = schema.TextLine(title=_(u"Text Line"), required=False)

    date_time_field = schema.Date(title=u'Date-Time Field', required=False)
    form.order_after(date_time_field='choice_field')
    
    form.mode(floater='hidden')
    floater = schema.Float(title=_(u"Floating Point Field"), default=0.0)

    relation_field = RelationChoice(title=_(u'My Related Page'),
      source=ObjPathSourceBinder(portal_type='Document'),
      default=None,
      required=False
    )

    dexterity.read_permission(relatedItems='cmf.ReviewPortalContent')
    dexterity.write_permission(relatedItems='cmf.ReviewPortalContent')
    relatedItems = RelationList(
        title=u"Related Items",
        default=[],
        value_type=RelationChoice(
              title=_(u"Related"),
              source=ObjPathSourceBinder(portal_type=('Document', 'File'))),
        required=False,
    )



@form.default_value(field=IEverythingModel['date_time_field'])
def default_date(data):
    return datetime.datetime.today()


@form.validator(field=IEverythingModel['text_line'])
def validateTitle(value):
    if value and value == value.upper():
        raise schema.interfaces.InvalidValue(_(u"Please don't shout"))


@form.error_message(error=schema.interfaces.InvalidValue, field=IEverythingModel['text_line'])
def tooLoud(value):
    # import pdb; pdb.set_trace()
    # Attempting to read value blows up!
    return _(u"Yuck! Too loud")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class EverythingModel(dexterity.Item):
    grok.implements(IEverythingModel)
    
    def getCountDown(self):
        return str(range(self.integer_field or 0, 0, -1))
        
    count_down = property(getCountDown, doc="Count Down from integer_field")


# View class
# The view will automatically use a similarly named template in
# everything_model_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(form.DisplayForm):
    grok.context(IEverythingModel)
    grok.require('zope2.View')
    
    def upperLine(self):
        return (getattr(aq_inner(self.context), 'text_line') or 'missing').upper()
    

class AsText(grok.View):
    grok.context(IEverythingModel)
    grok.require('zope2.View')

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        return getattr(aq_inner(self.context), 'text_line', 'missing')