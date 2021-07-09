{% args name, ip %}
<html>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Urządzenie {{name}}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css" />
</head>

<body>
    <section class="hero is-primary is-fullheight">

        <div class="hero-head">
            <nav class="navbar">
                <div class="container">

                    <div id="navbarMenuHeroA" class="navbar-menu">
                        <div class="navbar-end">
                            <a href="/" class="navbar-item">
                                Strona główna
                            </a>
                            <a href="configuration" class="navbar-item">
                                Konfiguracja
                            </a>
                            <a href="commands" class="navbar-item">
                                Komendy
                            </a>
                            <a href="log" class="navbar-item">
                                Log
                            </a>
                            <a href="http://micropython.org/webrepl/?#{{ip}}:8266" class="navbar-item">
                                REPL
                            </a>
                        </div>
                    </div>
                </div>
            </nav>
        </div>

        <div class="hero-body">
            <div class="container has-text-centered">
                <h1 class="title">Strona urządzenia {{name}}</h1>
            </div>
        </div>
    </section>
</body>

</html>
