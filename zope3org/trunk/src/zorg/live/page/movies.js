// JavaScript Document

// Kommunikation flash <-> HTML

		var myFilm;

		function thisMovie(myFilm)
			{
			if (navigator.appName.indexOf ("Microsoft") != -1)
				{
				return window[myFilm]
				}
			else
				{
				return document[myFilm]
				}
			}


		function movieIsLoaded (theMovie)
			{
			if (typeof(theMovie) != "undefined")
				{
				return theMovie.PercentLoaded() == 100;
				}
			else
				{
				return false;
				}
			}



		//Funktion fuer film starten

		function playFlash(myFilm)
			{
			if (movieIsLoaded(thisMovie(myFilm)))
			    {
				thisMovie(myFilm).Play();
				}
			}


		//Funktion fuer film anhalten

		function pauseFlash(myFilm)
			{
			if (movieIsLoaded(thisMovie(myFilm)))
				{
				thisMovie(myFilm).StopPlay();
				}
			}


		//Funktion fuer film zurücksetzen
			
		function startFlash(myFilm)
			{
			if (movieIsLoaded(thisMovie(myFilm)))
				{
				thisMovie(myFilm).GotoFrame(0);
				}
			}
		


		function movie_DoFSCommand (command, args)
			{
			}
