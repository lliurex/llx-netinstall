<?php

/* Check Netinstall  */

$mirror_var="/var/lib/n4d/variables-dir/LLIUREXMIRROR";
if (is_file($mirror_var) ) $mirror_installed=True; else $mirror_installed=False;
$filename="/etc/ltsp/bootopts/netinstall.json";
$type_install='';

if (is_file($filename)){
    $content_json=file_get_contents($filename);
    $json=json_decode($content_json,true);
    if(isset($json->{'normal_install'})){
        if ($json["normal_install"] == "true"){
            $type_install='normal';
        }else{
            $type_install='light';
        }
    }
}


if (strtolower($json["netinstall_boot"])=="true"&&$mirror_installed==True){
   $MenuEntryList=array();
   $MenuEntry=new stdClass();
   $MenuEntry->id="netinstall";
   $MenuEntry->label="Instal·la LliureX en aquest ordinador";
   $MenuEntry->menuString="";
   $dirname = '/var/www/mirror/llx19/dists/bionic/main/';
   $dir=false;
   if (is_dir($dirname)){
        $dir=scandir($dirname);
   }
   if ($dir != false){    
        $put_amd64=false;
        foreach ($dir as $item){
	    if ($item == 'binary-amd64')
	        $put_amd64=true;
        }
  
        $str_pxelinux="";
        if (strtolower($json["netinstall_stats"])=="true"){
            $str_pxelinux="pxelinux-stats.cfg";
        }else{
            $str_pxelinux="pxelinux.cfg";
        }
   
        if ($put_amd64){
            $MenuEntry->menuString.="\n# Netinst: Install Menu
            LABEL Instal.la LliureX en aquest ordinador amd64
            MENU LABEL Instal.la LliureX en aquest ordinador amd64
            KERNEL pxe-ltsp/netinstall/ubuntu-installer/amd64/boot-screens/vesamenu.c32
            CONFIG pxe-ltsp/netinstall/ubuntu-installer/amd64/$str_pxelinux/default pxe-ltsp/netinstall/\n";
        }

        if ($put_amd64){
            array_push($MenuEntryList, $MenuEntry);
            $MenuEntryListObject=$MenuEntryList;
        }
    }
}

?>
