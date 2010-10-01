=====================
Das Theme f�r Zope.de
=====================

Dies ist das Theme f�r die Website zope.de des DZUG e.V.

Startseite
==========

Nach der Installation des Themes ist der neue View �Frontpage� verf�gbar, der im Wurzelverzeichnis von Plone �ber das Men� �Darstellung� aktiviert wird.

Dieser View bindet die Inhalte auf der Startseite automatisch ein. 

Banner
------

Der View �Frontpage� sucht im Ordner �frontpage-stuff� nach Bildern und Links und bindet sie oben rechts neben der Slideshow als Banner ein. Daf�r muss die Frontpage �ber das ZMI mit dem Interface �IFrontPage� versehen werden. 

Die Bilder und Links im Ordner �frontpage-stuff� m�ssen folgende Kurznamen haben und ver�ffentlicht sein:

* image1 (Oberes Bild)
* image2 (Unteres Bild)

* image1-link (Link f�r das obere Bild)
* image2-link (Link f�r das untere Bild)

Die Links k�nnen dabei sowohl zu Zielen innerhalb der Website, als auch zu anderen Websites f�hren.

Teaser
------

Die Textbl�cke unterhalb der Slideshow werden ebenfalls automatisch eingebunden. Die Inhalte daf�r werden aus Links bezogen, die sich im Ordner �frontpage-stuff� befinden. Es werden die Felder �Titel�, �Beschreibung� und �Url� ausgewertet. Die Urls f�hren in der Regel zu Zielen innerhalb der Website. Die Links m�ssen folgende Kurznamen haben und ver�ffentlicht sein:

* teaser-1
* teaser-2

Es k�nnen weitere Links im Format �teaser-n� eingef�gt werden, wenn dies redaktionell erforderlich wird.

Slideshow
---------

Die Slideshow wird mit collective.easyslider realisiert. Siehe dazu die Dokumentation von Easyslider.

Aktuelles
=========

F�r die �bersichtsseite �Aktuelles� gibt es einen neuen View mit dem Namen �pageportlets�. Der View erm�glicht die Einbindung von Portlets im Content-Bereich. Die Portlets werden �ber �@@manage-page-portlets� eingebunden. 
