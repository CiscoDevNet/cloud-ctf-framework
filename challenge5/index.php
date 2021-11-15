<?php
require_once('../db_creds.php');
$mysql = mysqli_connect($mysql_host, $mysql_user, $mysql_pw, $mysql_db);
if (!$mysql)
{
die('Could not connect: ' . mysqli_error($mysql));
}
else
{
$selectdb = mysqli_select_db($mysql, $mysql_db);
if (!$selectdb)
{
die('Could not connect: ' . mysqli_error($mysql));
}
else
{
echo "Connected to the database!";
$data = mysqli_query($mysql, "SELECT visits FROM counter");
if (!$data)
{
die('Could not connect: ' . mysqli_error($mysql));
}
else
{
$add=mysqli_query($mysql,"UPDATE counter SET visits = visits+1");
if(!$add)
{
die('Could not connect: ' . mysqli_error($mysql));
}
else
{
print "<table><tr><th>Visits</th></tr>";
while($value=mysqli_fetch_array($mysql,$data))
{
print "<tr><td>".$value['visits']."</td></tr>";
}
print "</table>";
}
}
}
}
mysqli_close($mysql);
?>