<?php

/* Check Netinstall  */
$distribution = 'llx21';
$distribution_name ='focal';
$mirror_var="/var/lib/n4d/variables/LLIUREXMIRROR";
$filename="/etc/llxnetinstall/netinstall.json";
$type_install='';

//if (is_file($mirror_var)){
try{
    // $fp = file_get_contents($mirror_var);
    // $content = json_decode($fp,true);
    // if (array_key_exists('LLIUREXMIRROR',$content) && array_key_exists('value',$content['LLIUREXMIRROR']) && array_key_exists($distribution,$content['LLIUREXMIRROR']['value'])){
    //     $data_mirror = $content['LLIUREXMIRROR']['value'][$distribution];
    //     if (array_key_exists('status_mirror',$data_mirror) && array_key_exists('progress',$data_mirror) && strtolower($data_mirror['status_mirror']) == 'ok' && $data_mirror['progress'] == 100 ){
    //         $mirror_installed = true;
    //     }else{
    //         $mirror_installed = false;
    //     }
    // }else{
    //     $mirror_installed = false;
    // }
    $ret = exec('/usr/bin/lliurex-version -m');
    if (strtolower($ret) == "true"){
        $mirror_installed = true;
    }else{
        $mirror_installed = false;
    }
}catch(Exception $e){
    $mirror_installed = false;
}
//}

$json=array();
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


if (is_array($json) && array_key_exists("netinstall_boot",$json) && strtolower($json["netinstall_boot"]) == "true" && $mirror_installed==True){
   $MenuEntryList=array();
   $MenuEntry=new stdClass();
   $MenuEntry->id="netinstall";
   $MenuEntry->label="Instal·la LliureX en aquest ordinador";
   $MenuEntry->menuString="";
   $dirname = "/var/www/mirror/$distribution/dists/$distribution_name/main/";
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
