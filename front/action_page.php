<?php

// error_reporting(E_ALL);
// ini_set('display_errors', 1);


$IP = $_SERVER['REMOTE_ADDR'];

//print_r($_GET);
// Array ( [nome] => Carlos [sobrenome] => Smaniotto [idade] => 35 [sexo] => 0 [peso] => 90 [altura] => 1.75 [hipertensao] => on [diabete] => on [hortadia] => 3 [frutadia] => 3 [carnegordura] => on [atividadefisica] => on )

$pnome = trim($_GET["nome"]);
$sobrenome = trim($_GET["sobrenome"]);
$sexo = (int) $_GET["sexo"];
$idade = (int) $_GET["idade"];
$peso = (float)  $_GET["peso"];
$altura = (float) $_GET["altura"];

$carnegordura = (int) ($_GET["carnegordura"] == "on" ? 1 : 0);
$atividadefisica = (int) ($_GET["atividadefisica"] == "on" ? 1 : 0);
$hipertensao = (int) ($_GET["hipertensao"] == "on" ? 1 : 0);
$diabete = (int) ($_GET["diabete"] == "on" ? 1 : 0);
$frutadia = (int) $_GET["frutadia"];
$hortadia  = (int) $_GET["hortadia"];

/** Caluca o IMC
Abaixo de 17	Muito abaixo do peso
Entre 17 e 18,49	Abaixo do peso
Entre 18,5 e 24,99	Peso normal
Entre 25 e 29,99	Acima do peso
Entre 30 e 34,99	Obesidade I
Entre 35 e 39,99	Obesidade II (severa)
Acima de 40	Obesidade III (mórbida)
 */
$imc = round($peso / pow($altura,2),2);


/*
 * Fazendo Post Json para o Microservico de ML.
 */

// {"nome": "Carlos Smaniotto", "facebookID": 222, "IP": "177.125.129.63","weight": {"sexo":1,"horotadia":1,"frutadia":0,"carnegordura":1, "atividade":0,"hiptertensao":0,"diabetes":1}}

$nome = $pnome . ' ' . $sobrenome;
$facebookid = mt_rand();

$data = array(
    'nome'  => $nome,
    'facebookID' =>  $facebookid,
    'IP'  => $IP,
    'weight' =>  array  (
        'sexo' => $sexo,
        'idade' => $idade,
        'imc' => number_format($imc,2,'.',''),
        'hortadia' => $hortadia,
        'frutadia' => $frutadia,
        'carnegordura' => $carnegordura,
        'atividade' => $atividadefisica,
        'hiptertensao' => $hipertensao,
        'diabetes' => $diabete )
);



$uri = "http://ml-api.lifeordie.me:80/helth/api/v1.0/score_cholesterol";
//$uri = "http://127.0.0.1:8080/helth/api/v1.0/score_cholesterol";
$content = json_encode($data, JSON_PRETTY_PRINT);


$curl = curl_init($uri);

curl_setopt($curl, CURLOPT_HEADER, false);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_HTTPHEADER,
    array("Content-type: application/json"));
curl_setopt($curl, CURLOPT_POST, true);
curl_setopt($curl, CURLOPT_POSTFIELDS, $content);

$json_response = curl_exec($curl);
$status = curl_getinfo($curl, CURLINFO_HTTP_CODE);

if ( $status != 201 ) {
    die("Error: call to URL $uri failed with status $status, response $json_response, curl_error " . curl_error($curl) . ", curl_errno " . curl_errno($curl));
}


curl_close($curl);

$response = json_decode($json_response);
//echo json_encode($response, JSON_PRETTY_PRINT);
// { "Application": "ML-API", "IP": "127.0.0.1", "RequestData": "2017-06-25 13:54:23.592365", "RequestID": "b'Wktk87EtULzazJ7zhTaxzUW4Hfnk1l52bXSpr3lrdAw='", "atividade": 0, "carnegordura": 1, "diabetes": 0, "facebookID": 1921804768, "frutadia": 2, "hiptertensao": 1, "hortadia": 1, "idade": 35, "imc": "29.39", "nome": "Carlos Smanioto", "score": 0.34488067488067486454639265502919442951679229736328125, "sexo": 1 }

// Exibindo os perfils de saúde.
echo "<br>";
$score = (float) $response->score;

//echo "IMC: " . $imc;
//echo "<br>";
//echo "Caracas mano: " . $score;
echo  "<!DOCTYPE html>
       <html lang=\"en\">
       <head>
            <title>lifeordie.me</title>
            <meta charset=\"utf-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
            <link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css\">
            <script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js\"></script>
            <script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js\"></script>
            <link href=\"https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css\" rel=\"stylesheet\">
            <script src=\"https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js\"></script>
        </head>
        <body>


        <div class=\"row\">
            <div class=\"col-md-4\">
            </div>
            <div class=\"col-md-8\">
                <h1>Teu Resultado</h1>
            </div>
        </div>";




if ($score < 0.2) {
    echo "<div class=\"row\">
                <div class=\"col-md-6 brd\">
                    <div class=\"center-block\">
                            Você tem muita saúde para gastar heim " . $nome . "
                             <BR>
                             Teu score foi baixo:  " . $score . ".
                             <br>
                             Teu IMC: "  . $imc  ."
                             <br>
                             <img src=\"img/sheen.png\" alt=\"Charlie Sheen\" />
                    </div>
                 </div>";


    #echo  "<h1> Você tem muita saúde para gastar heim  ". $nome . "</h1>";
    #echo  "<br> Teu score foi baixo:  " . $score . " - <bold>isso signifca que tem poucas possibilidades de colesterol</bold> ";
    #echo  "<br> Teu IMC: " . $imc;
    #echo  "<br> Trofeu - Charlie Sheen ";
}

if ($score > 0.2 && $score < 0.45) {
    #echo "<html>";
    #echo  "<h1> Você esta na média! Sabe viver a vida :)   ". $nome . "</h1>";
    #echo  "<br> Teu score foi médio:  " . $score . " - <bold>isso signifca que dá para abusar, só um pouquinho..</bold> ";
    #echo  "<br> Teu IMC: " . $imc;
    #echo  "<br> Trofeu - Seu Madruga ";
    echo "<div class=\"row\">
                <div class=\"col-md-6 brd\">
                    <div class=\"center-block\">
                            Você tem saúde média ! Sabe viver a vida heim " . $nome . "
                             <BR>
                             Teu score foi medio:  " . $score . ".
                             <br>
                             Teu IMC: "  . $imc  ."
                             <br>
                             <img src=\"img/madruga.png\" alt=\"Seu Madruga\" />
                    </div>
                 </div>";



}


if ($score > 0.45 ) {
    #echo "<html>";
    #echo  "<h1> Você esta F*** e é bom se cuidar!  ". $nome . "</h1>";
    #echo  "<br> Teu score foi alto:  " . $score . " - <bold>isso signifca que você esta F*** e pode morrer logo...</bold> ";
    #echo  "<br> Teu IMC: " . $imc;
    #echo  "<br> Trofeu - Inri Cristo";
    echo "<div class=\"row\">
                <div class=\"col-md-6 brd\">
                    <div class=\"center-block\">
                            Você esta F**** e é bom se cuidar... " . $nome . "
                             <BR>
                             Teu score foi alto:  " . $score . ".
                             <br>
                             Teu IMC: "  . $imc  ."
                             <br>
                             <img src=\"img/inri.png\" alt=\"Inri Cristo\" />
                    </div>
                 </div>";



}

echo "</div>
     </body>
    </html> ";

?>
