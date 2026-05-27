"""Module providing the In() sur-Class"""

from .generic import GenericType
from .error import STypeError, SAttributeError
from .toolbox import validation_parameters


class In(GenericType):
    """
    A kind of "one of"
    """

    @validation_parameters
    def __init__(self, models: list[GenericType | None], **kwargs):
        """
        available arguments

        """
        self._models = models
        GenericType.__init__(self, **kwargs)

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = GenericType.get_schema(self)
        a["sub_scheme"] = []
        for schema in self._models:
            a["sub_scheme"].append(schema.get_schema())
        return a

    def check_type(self, value):

        for model in self._models:

            # Look for the good type
            try:
                if value is not None:
                    model.check_type(value)
                    return
            except Exception:  # pylint: disable=broad-exception-caught
                continue

        raise STypeError(
            '{0}: Match no model (value="{value}", models="{models}")',
            self.path_name(),
            value=value,
            models=self._models,
        )

    def check_value(self) -> None:
        """
        Check of the value is compliant to contraints
        or throw an error
        """

        # Cannot read
        if self.exists_or_can_read() is False:
            raise SAttributeError("{0}: Locked", self.path_name())

        value = self.get_value()
        for model in self._models:
            try:
                model.check_type(value)
            except Exception:  # pylint: disable=broad-exception-caught
                continue
            model.check_constraints(value)
