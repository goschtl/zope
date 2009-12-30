# -*- coding: utf-8 -*-

import logging

# Configuring level and formatter
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

# Creating logger
log = logging.getLogger('iconregistry')
log.addHandler(ch)

from megrok.icon.interfaces import IIcon, IIconRegistry, IIconRegistryStorage
from megrok.icon.registry import Icon, IconRegistry
