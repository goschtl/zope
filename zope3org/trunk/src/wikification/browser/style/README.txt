CSS Hacks 'n Filters
====================

[1] @import filter
    Primarily used to filter out NS4.x/all

    Example 1:

    @import url(main.css);

    Notes:
    Affected browsers ignore @import rules.

    References:
    <http://www.ericmeyeroncss.com/bonus/trick-hide.html>
    <http://www.w3.org/TR/CSS21/cascade.html#at-import>

[2] @import single quotes without url
    Primarily used to filter out IE4-5.x/Mac and IE4-5.0/Win

    Example 1:

    /* without whitespace */
    @import'main.css';

    Example 2:

    /* with whitespace */
    @import 'main.css';

    Example 3:

    /* with double quotes */
    @import "main.css";

    Notes:
    Affected browsers ignore @import rules without url.
    If used with double quotes without whitespace, Konq2.2-2.3/all will ignore it.
    If used without whitespace, IE5.0/Win will ignore it.

    References:
    <http://www.dithered.com/css_filters/css_only/import_single_quotes_no_space.html>
    <http://www.w3.org/TR/CSS21/cascade.html#at-import>
    <http://www.w3.org/TR/CSS21/syndata.html#strings>

[3] IE5 backslash hack v2
    Hide a block of rules from IE5.x/Mac. Everything between /*\*/ and /**/ will
    be ignored.

    Example:

    /*\*/
    div {
      color: green;
    }
    /**/

    Notes:
    In IE5.x/Mac the \ escapes the end-comment marker. This is a browser bug.
    Q: Should we use this hack even though we filter out IE5.x/Mac?
    A: Yes, if we know that something would break; and because it's easier
    to add support later (if we need to).

    References:
    <http://www.sam-i-am.com/work/sandbox/css/mac_ie5_hack.html>
    <http://www.w3.org/TR/CSS21/syndata.html#comments>
    <http://www.w3.org/TR/CSS21/syndata.html#escaped-characters>