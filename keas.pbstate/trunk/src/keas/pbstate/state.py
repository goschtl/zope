

class StateTuple(tuple):
    """Contains the persistent state of a ProtobufState object.

    Contains data (a byte string) and targets (a map of refid to object).
    This state class has an attribute, 'serial_format', that provides
    a hint on how the state ought to be serialized.
    """
    serial_format = 'protobuf'
