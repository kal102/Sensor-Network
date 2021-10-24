<!DOCTYPE html>
<html lang="pl">
	<head>
		<meta charset="utf-8"></meta>
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
		<title>Lokalizacja</title>
        <!-- Favicon-->
        <link rel="icon" type="image/x-icon" href="assets/favicon.ico" />
        <!-- CSS (includes Bootstrap)-->
        <link href="css/styles.css" rel="stylesheet" />
		<link href="css/map.css" rel="stylesheet" />
        <!-- Scripts-->
        <script src="//cdn.jsdelivr.net/npm/chart.js@2.9.4/dist/Chart.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/moment.js/2.13.0/moment.min.js"></script>
        <script src="//canvasjs.com/assets/script/canvasjs.min.js"></script>
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
	</head>
	<body>
        <!-- Responsive navbar-->
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="index.php">Sieć czujników</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
                <div class="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                        <li class="nav-item"><a class="nav-link" aria-current="page" href="index.php">Strona główna</a></li>
                        <li class="nav-item"><a class="nav-link" href="temperature.php">Temperatura</a></li>
                        <li class="nav-item"><a class="nav-link" href="pressure.php">Ciśnienie</a></li>
                        <li class="nav-item"><a class="nav-link" href="humidity.php">Wilgotność</a></li>
                        <li class="nav-item"><a class="nav-link active" href="location.php">Lokalizacja</a></li>
                        <li class="nav-item"><a class="nav-link" href="control.php">Sterowanie</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        <!-- Page content-->
        <div class="container">
            <div class="text-center mt-5" id="map">
                <script type="text/javascript" src=js/location.js></script>
                
                <!-- Async script executes immediately and must be after any DOM elements used in callback. -->
                <script
                    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDb8NANj49maSQj5GQGTut8XqJfoS083Hs&callback=initMap&libraries=&v=weekly"
                    async
                ></script>
            </div>
        </div>
        <!-- Bootstrap core JS-->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.bundle.min.js"></script>
        <!-- Core theme JS-->
        <script src="js/scripts.js"></script>		
	</body>
</html>
