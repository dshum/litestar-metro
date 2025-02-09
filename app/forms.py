from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.fields.list import FieldList
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, PasswordField, BooleanField, FileField
from wtforms.form import Form
from wtforms.validators import InputRequired, DataRequired, NumberRange, Optional
from wtforms.widgets import NumberInput
from wtforms.widgets.core import CheckboxInput, ListWidget


class FileValidationException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message


class LoginForm(Form):
    username = StringField("Username", [InputRequired()])
    password = PasswordField("Password", [InputRequired()])


class WorldForm(Form):
    name = StringField("Name", [InputRequired()])
    order = IntegerField("Order", [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))


class LineForm(Form):
    name = StringField("Name", [InputRequired()])
    order = IntegerField("Order", [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))
    world_id = SelectField("World", [InputRequired()])


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
    name = StringField("Name", [InputRequired()])
    order = IntegerField("Order", [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))
    line_id = SelectField("Line", [InputRequired()])
    platform_length = IntegerField("Platform length", widget=NumberInput(min=0, step=1))
    platform_square = IntegerField("Platform area", widget=NumberInput(min=0, step=1))
    platform_number = IntegerField("Platform number", widget=NumberInput(min=0, step=1))
    entrance_number = IntegerField("Entrance number", widget=NumberInput(min=0, step=1))
    has_depot = BooleanField("Has depot", default=False)
    has_elevators = BooleanField("Has elevators", default=False)
    is_underground = BooleanField("Is underground", default=False)
    is_terminal = BooleanField("Is terminal", default=False)
    materials = StringFieldList(
        StringField("Material", [DataRequired()], description="Enter material"),
        label="Materials",
        description="Enter material",
    )


class StationTransfersForm(Form):
    transfers = MultiCheckboxField(
        "Transfers",
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False),
    )


class StationScreenshotForm(Form):
    image = FileField("Image", [InputRequired()])
    title = StringField("Title")
    order = IntegerField("Order", [Optional(), NumberRange(min=0)], widget=NumberInput(min=0, step=1))
