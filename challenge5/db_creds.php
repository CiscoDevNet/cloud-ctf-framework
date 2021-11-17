<?php
$maria_user = 'chal5user';
$maria_pw = 'cH41l3ng3_5';
$maria_db = 'chal5db';
$maria_host = '';
if(file_exists('/var/www/.maria')){
    try{
        $maria_env = parse_ini_file('/var/www/.maria');
        if($maria_env){
            if(array_key_exists('maria_host', $maria_env)){
                $maria_host = $maria_env['maria_host'];
            }
            if(array_key_exists('maria_user', $maria_env)){
                $maria_user = $maria_env['maria_user'];
            }
            if(array_key_exists('maria_pw', $maria_env)){
                $maria_pw = $maria_env['maria_pw'];
            }
            if(array_key_exists('maria_db', $maria_env)){
                $maria_db = $maria_env['maria_db'];
            }
        }
    }catch(\Exception $e){
        error_log("Caught Exception: $e");
        die('Could not get db info, what did you break?' );
    }
}
