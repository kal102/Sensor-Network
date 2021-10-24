<!DOCTYPE html>
<html lang="pl">
	<head>
		<meta charset="utf-8"></meta>
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
		<title>Ciśnienie</title>
        <!-- Favicon-->
        <link rel="icon" type="image/x-icon" href="assets/favicon.ico" />
        <!-- CSS (includes Bootstrap)-->
        <link href="css/styles.css" rel="stylesheet" />
		<link href="css/table.css" rel="stylesheet" />
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
                        <li class="nav-item"><a class="nav-link active" href="pressure.php">Ciśnienie</a></li>
                        <li class="nav-item"><a class="nav-link" href="humidity.php">Wilgotność</a></li>
                        <li class="nav-item"><a class="nav-link" href="location.php">Lokalizacja</a></li>
                        <li class="nav-item"><a class="nav-link" href="control.php">Sterowanie</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        <!-- Page content-->
        <div class="container">
            <div class="text-center mt-5" id="chart_table">
				<table style="width:100%; border-collapse:collapse;">
					<tr>
						<td>
							<div id="chartContainer" style="height: 500px; max-width: 960px; margin: 0px auto;"></div>
						</td>
					</tr>
				</table>
				<br>
				<center>
					<label for="min_date">Od:</label>
					<input type="date" id="min_date">
					<input type="time" id="min_time">
					<label for="max_date">Do:</label>
					<input type="date" id="max_date">
					<input type="time" id="max_time">
					<br>
					<label style="color:red;display:none;" id="date_error_label"></label>
				</center>
				<div id="latest-results">
					<table id="table">
						<thead>
							<tr>
								<th>Nazwa urządzenia</th>
								<th>Najnowsza wartość</th>
                                <th>Data pomiaru</th>
							</tr>
						</thead>
						<tbody>
						</tbody>
					</table>
				</div>
				<script type="text/javascript" dataType="pressure" src=js/data.js></script>
			</div>
		</div>
        <!-- Bootstrap core JS-->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.bundle.min.js"></script>
        <!-- Core theme JS-->
        <script src="js/scripts.js"></script>		
	</body>
</html>
