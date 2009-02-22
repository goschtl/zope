##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""WSGI environment key names used by zope.pipeline applications.

This module contains an alias for each of the environment keys below.

'zope.pipeline.can_retry'
     Contains a boolean value specifying whether the error handling
     application should propagate Retry and ConflictError exceptions.
     It is created by the `retry` application and is later read by the
     `handle_error` application.

'zope.pipeline.request'
    Contains an object that provides the IRequest interface. The
    request is created and later closed by the `create_request`
    application. It is used by several applications, the
    `switch_pipeline` and `call` applications in particular.

'zope.pipeline.traversal_hooks'
    Contains a list of functions to call before each traversal step.
    The `set_site`, `event`, and `authenticate` applications add to
    this list and the `traverse` application calls the hooks.  The
    `retry` application clears this list.

    Each hook will be called with two parameters, request and ob. The
    hook function does not need to return anything.

    These hooks will be called before traversing an object for the
    first time. If the same object is traversed more than once, the
    hook will still only be called the first time.

'zope.pipeline.traversed'
    List of (name, obj) steps that have been traversed. Created by the
    `open_root` application, which adds the application root as the
    first element of this list. Used by at least the `traverse` and
    `call` applications.

'zope.pipeline.default_traversal_steps'
    Number of steps that were traversed implicitly. Default traversal
    adds implicit traversal steps to the end of the path; this is
    primarily used for default views of folders. Created by the
    `traverse` application and used by the `fix_relative_links`
    application.

'zope.pipeline.string_result_hooks'
    A list of functions to call if the response is set to a string
    result. Each function is passed two parameters, string_result and
    environ, and returns a new string result. The hooks are processed
    in order. The `fix_relative_links` application adds this hook and
    the response object attached to the request uses these hook. The
    `retry` application removes this hook.

    The hooks are not called if the response is set to something
    other than a string.

$Id$
"""
__docformat__ = 'restructuredtext'

CAN_RETRY_KEY = "zope.pipeline.can_retry"
REQUEST_KEY = "zope.pipeline.request"
TRAVERSAL_HOOKS_KEY = "zope.pipeline.traversal_hooks"
TRAVERSED_KEY = "zope.pipeline.traversed"
DEFAULT_TRAVERSAL_STEPS_KEY = "zope.pipeline.default_traversal_steps"
STRING_RESULT_HOOKS_KEY = "zope.pipeline.string_result_hooks"

RESETTABLE_KEYS = [
    name for (varname, name) in globals().items() if varname.endswith('_KEY')]
