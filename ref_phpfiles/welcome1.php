<html>
<body>

<!-- Deal with account. -->
<!-- Must contain at least one number/letter. Only numbers, letters and '_' are valid. Length of account should be longer than 6 and shorter than 17. -->
<?php

$login = $_POST["login"];
if(strlen($login)==0){
    echo "Please do not leave the account empty!!<br>";
}
elseif(!preg_match("/[0-9]+/",$login)){
    echo "Your account must contain at least one number!!<br>";
}
elseif(!preg_match("/[a-zA-Z]+/",$login)){
    echo "Your account must contain at least one letter!!<br>";
}
elseif(preg_match("/^[0-9a-zA-Z_]{6,17}$/",$login)){
    echo "Account is valid!!<br>";
}
elseif(strlen($login)<6){
    echo "Account is too short or inlcudes invalid chars!!<br>";
}
elseif(strlen($login)>17){
    echo "Account is too long or includes invalid chars!!<br>";
}
else{
    echo "The account includes invaid chars!!<br>";
}
?>

<!-- Deal with password. -->
<!-- Must contain at least one number/letter. Only numbers, letters and '_' are valid. Length of password should be longer than 6 and shorter than 17. -->
<?php
$password = $_POST["password"];
if(strlen($password)==0){
    echo "Please do not leave the password empty!!<br>";
}
elseif(!preg_match("/[0-9]+/",$password)){
    echo "Your password must contain at least one number!!<br>";
}
elseif(!preg_match("/[a-zA-Z]+/",$password)){
    echo "Your password must contain at least one letter!!<br>";
}
elseif(preg_match("/^[0-9a-zA-Z_]{6,17}$/",$password)){
    echo "Password is valid!!<br>";
}
elseif(strlen($password)<6){
    echo "Password is too short or inlcudes invalid chars!!<br>";
}
elseif(strlen($password)>17){
    echo "Password is too long or includes invalid chars!!<br>";
}
else{
    echo "The password includes invaid chars!!<br>";
}
?>


<!-- Deal with Phone number. -->
<!-- Phone number format: XXXX-XXX-XXX. '', ' '(space) and '-' are valid notations to seperate the phone number. -->
<?php
$tel = $_POST["tel"];
if(preg_match("/^\d{4}[\s-]?\d{3}[\s-]?\d{3}$/",$tel)){
    echo "The phone number  ".$tel."  is valid!!<br>";
}
elseif(strlen($tel)==0){
    echo "You leave the phone number empty!!<br>";
}
else{
    echo "The phone number  ".$tel."  is invalid!!<br>";
}
?>

<!-- Deal with Email. -->
<?php
$email = $_POST["email"];
if(!filter_var($email, FILTER_VALIDATE_EMAIL) === false){
    echo $email."     is a valid email address!!<br>";
} 
elseif(strlen($email)==0){
    echo "You leave the email empty!!<br>";
}
else{
    echo $email."     is not a valid email address!!<br>";
}
?>

<!-- Deal with URL. -->
<?php
// FILTER_FLAG_SCHEME_REQUIRED - URL must be RFC compliant (like http://example)
// FILTER_FLAG_HOST_REQUIRED - URL must include host name (like http://www.example.com)
// FILTER_FLAG_PATH_REQUIRED - URL must have a path after the domain name (like www.example.com/example1/)
// FILTER_FLAG_QUERY_REQUIRED - URL must have a query string (like "example.php?name=Peter&age=37")
$URL = $_POST["url"];
if(!filter_var($URL, FILTER_VALIDATE_URL, FILTER_FLAG_HOST_REQUIRED) === false){
    echo $URL."     is a valid URL!!<br>";
}
elseif(strlen($URL)==0){
    echo "You leave the URL empty!!<br>";
}
else{
    echo $URL."     is not a valid URL!!<br>";
}
?>

<!-- Deal with Week. -->
<!-- Date format: Year-Week. '-W' is the only valid notations to seperate the date. -->
<!-- 999<Year<2100, 0<Week<53 -->
<?php
$week = $_POST["week"];
$format = 0;
$valid = 0;
if(preg_match("/^\d{3,4}-W\d{1,2}$/",$week)){
    $format = 1;
}
if($format){
    $array = preg_split("/-W/",$week);
    $year = intval($array[0]);
    $WEEK = intval($array[1]);
    if(is_int($year) and $year<2100 and $year>999){
        if(is_int($WEEK) and $WEEK>0 and $WEEK<=52){
            $valid = 1;
        }
    }
}
if(strlen($week)==0){
    echo "You leave the week empty!!<br>";
}
elseif($format and $valid){
    echo "Week is valid!!<br>";
}
else{
    echo "Week is invalid<br>";
}
?>
<!-- Deal with Month. -->
<!-- Month format: Year-Month. '-' is the only valid notations to seperate the date. -->
<!-- 999<Year<2100, 0<Month<13 -->

<?php
$month = $_POST["month"];
$format = 0;
$valid = 0;
if(preg_match("/^\d{3,4}-\d{1,2}$/",$month)){
    $format = 1;
}
if($format){
    $array = preg_split("/-/",$month);
    $year = intval($array[0]);
    $MONTH = intval($array[1]);
    if(is_int($year) and $year<2100 and $year>999){
        if(is_int($MONTH) and $MONTH>0 and $MONTH<=12){
            $valid = 1;
        }
    }
}
if(strlen($MONTH)==0){
    echo "You leave the month empty!!<br>";
}
elseif($format and $valid){
    echo "Month is valid!!<br>";
}
else{
    echo "Month is invalid<br>";
}
?>

<!-- Deal with date. -->
<!-- Date format: Year-Month-Day. '/', ' ' and '-' are valid notations to seperate the date. -->
<!-- 999<Year<2100, 0<Month<13, 0<Day<32-->
<?php
$date = $_POST["date"];
$format = 0;
$valid = 0;
if(preg_match("/^\d{3,4}[\/\s-]+\d{1,2}[\/\s-]+\d{1,2}$/",$date)){
    $format = 1;
}
if($format){
    $array = preg_split("/[\/\s-]/",$date);
    $year = intval($array[0]);
    $month =  intval($array[1]);
    $day = intval($array[2]);
    if(is_int($year) and $year<2100 and $year>999){
        if(is_int($month) and $month<13 and $month>0){
            if(is_int($day) and $day<32 and $day>0){
                $valid = 1;
            }
        }
    }
}
if(strlen($date)==0){
    echo "You leave the date empty!!<br>";
}
elseif($format and $valid){
    echo "Date is valid!!<br>";
}
else{
    echo "Date is invalid<br>";
}
?>

<!-- Deal with time. -->
<!-- Time format: Hour:Minute. ' '(space) and ':' are valid notations to seperate the time. -->
<!-- 24>Hour>=0, 60>Minute>=0 -->
<?php
$time = $_POST["time"];
$format = 0;
$valid = 0;
if(preg_match("/^\d{1,2}[\s:]?\d{1,2}$/",$time)){
    $format = 1;
}
if($format){
    $array = preg_split("/[\/\s-]/",$time);
    $hour = intval($array[0]);
    $minute =  intval($array[1]);
    if(is_int($hour) and $hour<24 and $hour>=0){
        if(is_int($minute) and $minute<60 and $minute>=0){
            $valid = 1;
        }
    }
}
if(strlen($time)==0){
    echo "You leave the time empty!!<br>";
}
elseif($format and $valid){
    echo "Time is valid!!<br>";
}
else{
    echo "Time is invalid<br>";
}
?>

<!-- Deal with Datetime. -->

<?php
$datetime = $_POST["datetime"];
$format = 0;
$valid = 0;
echo "Datetime : ".$datetime."<br>";
?>

<!-- Deal with Datetime-local. -->

<?php
$datetime_local = $_POST["datetime_local"];
$format = 0;
$valid = 0;
if(preg_match("/^\d{3,4}[\/\s-]+\d{1,2}[\/\s-]+\d{1,2}T\d{1,2}[\s:]?\d{1,2}$/",$datetime_local)){
    $format = 1;
}
if($format){
    $array = preg_split("/[T:-\s\/]/",$datetime_local);
    $year = intval($array[0]);
    $month = intval($array[1]);
    $day = intval($array[2]);
    $hour = intval($array[3]);
    $minute = intval($array[4]);
    if(is_int($year) and $year<2100 and $year>999){
        if(is_int($month) and $month<13 and $month>0){
            if(is_int($day) and $day<32 and $day>0){
                if(is_int($hour) and $hour<24 and $hour>=0){
                    if(is_int($minute) and $minute<60 and $minute>=0){
                        $valid = 1;
                    }
                }
            }
        }
    }
}
if(strlen($datetime_local)==0){
    echo "You leave the datetime-local empty!!<br>";
}
elseif($format and $valid){
    echo "Datetime-local is valid!!<br>";
}
else{
    echo "Datetime-local is invalid!!<br>";
}
?>

<!-- Deal with number. -->
<?php
$number = $_POST["number"];
if(strlen($number)==0){
    echo "You leave the number empty!!<br>";
}
elseif(preg_match("/^-?\d{0,16}$/",$number)){
    //Integer
    echo "Number is valid!!<br>";
}
elseif(preg_match("/^-?\d{0,16}\.\d{0,8}$/",$number)){
    //Float
    echo "Number is valid!!<br>";
}
else{
    echo "Number is invalid!!<br>";
}
?>

<!-- Deal with range. -->
<?php
$range = $_POST["range"];
$format = 0;
$vlaid = 0;
if(preg_match("/^\d{1,4}$/",$range)){
    $format = 1;
}
if($format){
    $value = intval($range);
    if($value%50 ==0 and $value>=0 and $value <=1000){
        $valid = 1;
    }
}
if(strlen($range)==0){
    echo "You leave the range empty!!<br>";
}
else if($format and $valid){
    echo "Range is valid!!<br>";
}
else{
    echo "Range is invalid!!<br>";
}
?>

<!-- Deal with color. -->
<?php
$color = $_POST["color"];
if(strlen($color)==0){
    echo "You leave the color empty!!<br>";
}
elseif(preg_match("/^#[a-f0-9]{6}$/",$color)){
    echo "Color is valid!!<br>";
}
else{
    echo "Color is invalid!!<br>";
}
?>

<!-- Deal with search. -->
<?php
$search = $_POST["search"];
$format = 0;
$valid = 0;
echo "Search : ".$search."<br>";
?>


</body>
</html>

