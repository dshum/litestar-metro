from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.fields.list import FieldList
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, PasswordField, BooleanField, FileField
from wtforms.form import Form
from wtforms.validators import InputRequired, DataRequired, NumberRange, Optional
from wtforms.widgets import NumberInput
from wtforms.widgets.core import CheckboxInput, ListWidget

from app.configs import _


class FileValidationException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message


class LoginForm(Form):
    username = StringField(_("Username"), [InputRequired()])
    password = PasswordField(_("Password"), [InputRequired()])


class WorldForm(Form):
    name = StringField(_("Name"), [InputRequired()])
    order = IntegerField(_("Order"), [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))


class LineForm(Form):
    name = StringField(_("Name"), [InputRequired()])
    order = IntegerField(_("Order"), [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))
    world_id = SelectField(_("World"), [InputRequired()])


class StringFieldList(FieldList):
    ...


class MultiCheckboxField(SelectMultipleField):
    def process_formdata(self, valuelist):
        if valuelist:
            if isinstance(valuelist[0], list):
                self.data = valuelist[0]
            else:
                self.data = valuelist
        else:
            self.data = []


class StationForm(Form):
    name = StringField(_("Name"), [InputRequired()])
    order = IntegerField(_("Order"), [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))
    line_id = SelectField(_("Line"), [InputRequired()])
    platform_length = IntegerField(_("Platform length"), widget=NumberInput(min=0, step=1))
    platform_square = IntegerField(_("Platform area"), widget=NumberInput(min=0, step=1))
    platform_number = IntegerField(_("Platform number"), widget=NumberInput(min=0, step=1))
    entrance_number = IntegerField(_("Entrance number"), widget=NumberInput(min=0, step=1))
    has_depot = BooleanField(_("Has depot"), default=False)
    has_elevators = BooleanField(_("Has elevators"), default=False)
    is_underground = BooleanField(_("Is underground"), default=False)
    is_terminal = BooleanField(_("Is terminal"), default=False)
    materials = StringFieldList(
        StringField(_("Material"), [DataRequired()], description="Enter material"),
        label=_("Materials"),
        description=_("Enter material"),
    )


class StationTransfersForm(Form):
    transfers = MultiCheckboxField(
        _("Transfers"),
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False),
    )


class StationScreenshotForm(Form):
    image = FileField(_("Image"), [InputRequired()])
    title = StringField(_("Title"))
    order = IntegerField(_("Order"), [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))
