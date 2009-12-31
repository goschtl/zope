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

from grokcore.view import path, name

from megrok.icon.interfaces import (
    IIconsRegistry, IIconsRegistryStorage, ITemporaryIconsRegistry)

from megrok.icon.registry import IconsRegistry, CHECKER

from megrok.icon.registries_map import _icons_registries_map
from megrok.icon.registries_map import (
    getIconsRegistriesMap, setIconsRegistriesMap, queryIconsRegistry)

from megrok.icon.directive import icon
from megrok.icon.utils import (
    get_icon_url, get_component_icon_url, populate_icons_registry)
