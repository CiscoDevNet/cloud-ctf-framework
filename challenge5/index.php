<?php
// DO NOT MODIFY THIS APPLICATION CODE
function shaself(){
    return md5_file(__FILE__);
}
header("shaself: ".shaself());
echo "<h2>My First Cloud LAMP</h2>";
//echo "You found the flag! flag{Surely_This_is_n0t_a_real_flag}";

require_once('../db_creds.php');

$maria = mysqli_connect($maria_host, $maria_user, $maria_pw, $maria_db);
if (!$maria)
{
    error_log("mysql err: ".mysqli_error($maria));
    die('Could not connect: Where is maria?');
}

else
{
    $selectdb = mysqli_select_db($maria, $maria_db);
    if (!$selectdb)
    {
        error_log("mysql err: ".mysqli_error($maria));
        die('Could not connect: Where did the database go?');
    }
    else
    {
        echo "<p>Connected to the database!</p>";
        $data = mysqli_query($maria, "SELECT visits FROM counter");
        if (!$data)
        {
            error_log("mysql err: ".mysqli_error($maria));
            die('Could not find my table?');
        }
        else
        {
            $add=mysqli_query($maria,"UPDATE counter SET visits = visits+1");
            if(!$add)
            {
                error_log("mysql err: ".mysqli_error($maria));
                die('Could not update table :( ');
            }
            else
            {
                $query = "SELECT visits FROM counter";
                $result = mysqli_query($maria, $query);
                $row = mysqli_fetch_array($result, MYSQLI_ASSOC);
                print "<p>Thanks for visiting the site. You are visitor number <strong>{$row['visits']}</strong></p>";
            }
        }
    }
}
mysqli_close($maria);