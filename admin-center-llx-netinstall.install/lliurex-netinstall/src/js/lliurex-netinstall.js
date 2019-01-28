function LlxNetinstall(){
   this.netinstall=false;
   this.unattended_netinstall=false;
   this.netinstall_stats=true;
   this.nongplapps=false;
}

LlxNetinstall.prototype._=function _(text){
  return ( i18n.gettext("lliurex-netinstall", text));
}

// Methods

LlxNetinstall.prototype.getNetinstallConfig=function getNetinstallConfig(){
   var self=this;
   
   credentials="";
   n4dclass="NetinstallManager";
   n4dmethod="getNetinstall";
   arglist=[];
    
   Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
      console.log('getNetinstall '+response);
      response.netinstall == 'true' ? self.netinstall=true : self.netinstall=false;
      response.unattended == 'true' ? self.unattended_netinstall=true : self.unattended_netinstall=false;
      response.stats == 'true' ? self.netinstall_stats=true : self.netinstall_stats=false;
      response.nongplapps == 'true' ? self.nongplapps=true : self.nongplapps=false;
      self.showUI();   
   },0);
}

LlxNetinstall.prototype.set_nongplapps=function set_nongplapps(status){
   var self=this;
   
   credentials=[sessionStorage.username, sessionStorage.password];
   n4dclass="NetinstallManager";
   n4dmethod="install_nongpl";
   if (status == true){
        arglist=['true'];
   }else{
        arglist=['false'];
   }
   Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
      console.log('SetNonGPL '+response);
   },0);
}

LlxNetinstall.prototype.mostrarAgreement = function(){
    var html =" <div class='form-group' id = 'lliurex_netinstall_agreement_box'>";
    if (!this.visibleLocals){
        html+=this._("lliurex_netinstall_nongpl_description");
    }
    html +="</div>";
    var dialog=bootbox.dialog({
        title: this._("lliurex_netinstall_agreement_title"),
        message:html,
        buttons:[
        {
            label:'ok',
            className: 'btn-info',
            callback: function(diag){
                //debugger;
                self.netInstall.nongplapps=true;
                $("#llx_netinstall_enable_nongpl_apps").prop('checked',true);
            }
        },
        {
            label:'cancel',
            className: 'btn-danger',
            callback: function(diag){
                //debugger;
                self.netInstall.nongplapps=false;
                $("#llx_netinstall_enable_nongpl_apps").prop('checked',false);
            }
        }
        ],
        onshown: function(){ 
            $.material.init('#lliurex_netinstall_agreement_box');
        },
    });
    dialog.modal("show");
}


LlxNetinstall.prototype.showUI=function showUI(){
   var self=this;
   var content="";

   var netinstallchecked="";
   var netinstallunattended="";
   var netinstallunattendeddisabled="";
   var netinstall_stats="";
   var netinstall_enable_nongpl="";
   
   if (self.nongplapps === true){
        netinstall_enable_nongpl="checked";
   }
   //self.set_nongplapps(self.nongplapps);
   if (self.netinstall_stats===true){
      netinstall_stats="checked";
   }

   if (self.netinstall===true){
      netinstallchecked="checked";
   }else{
      netinstallunattendeddisabled="disabled";
   }
   
   if (self.unattended_netinstall===true) {
      netinstallunattended="checked";
      netinstalldataunattended="";
   } else netinstalldataunattended="true";
   
   content+=Utils.formFactory.createCheckbox({"id":"llx_netinstall_setnetinstall",
                                                "label":self._("lliurex_netinstall_enable_netinstall"),
                                                "default":netinstallchecked,
                                                "disabled": "",
                                                "help":self._("lliurex_netinstall_enable_netinstall")});
   
   content+=Utils.formFactory.createCheckbox({"id":"llx_netinstall_setnetinstall_unattended",
                                                "label":self._("lliurex_netinstall_enable_unattended"),
                                                "default":netinstallunattended,
                                                "disabled": netinstallunattendeddisabled,
                                                "help":self._("lliurex_netinstall_enable_unattended")});

    content+=Utils.formFactory.createCheckbox({"id":"llx_netinstall_enable_nongpl_apps",
                                                "label":self._("lliurex_netinstall_enable_nongpl_apps"),
                                                "default": netinstall_enable_nongpl,
                                                "disabled": "",
                                                "help":self._("lliurex_netinstall_enable_nongpl_apps")});
 
      content+=Utils.formFactory.createText({"id":"llx_netinstall_setnetinstall_user",
                                        "label": self._("lliurex_netinstall_username"),
                                        "help":self._("lliurex_netinstall_username"),
                                        "disabled": netinstalldataunattended,
                                        "value":""});
        
   content+=Utils.formFactory.createText({"id":"llx_netinstall_setnetinstall_pass",
                                        "label": self._("lliurex_netinstall_pass"),
                                        "disabled": netinstalldataunattended,
                                        "help":self._("lliurex_netinstall_pass"),
                                        "value":""});
   
   content+=Utils.formFactory.createText({"id":"llx_netinstall_setnetinstall_pass_root",
                                        "label": self._("lliurex_netinstall_rootpass"),
                                        "disabled": netinstalldataunattended,
                                        "help":self._("lliurex_netinstall_rootpass"),
                                        "value":""});

   content+=Utils.formFactory.createCheckbox({"id":"llx_netinstall_do_stats",
                                              "label":self._("lliurex_netinstall_enable_stats"),
                                              "default":netinstall_stats,
                                              "disabled": "",
                                              "help":self._("lliurex_netinstall_enable_stats")},false);

   
   $("#llx_netinstall_config").append(content);
   
   
   $.material.init();
   
   
   
   // Event binding
   $("#llx_netinstall_apply_config").show();
   
   $("#llx_netinstall_enable_nongpl_apps").on("click", function(){
            if ($('#llx_netinstall_enable_nongpl_apps').prop('checked') == true){
                //show message
                self.mostrarAgreement();
            }else{
                self.nongplapps=false;
            }
        //console.log('setting nongplapps '+self.nongplapps)
        //self.set_nongplapps(self.nongplapps);
        }
    );
   
   $("#llx_netinstall_do_stats").off("click");
   $("#llx_netinstall_do_stats").on("click", function(){
            self.netinstall_stats=!self.netinstall_stats;
        }
    );

   $("#llx_netinstall_setnetinstall").off("click");
   $("#llx_netinstall_setnetinstall").on("click", function(){
      self.netinstall=!self.netinstall;
      if(self.netinstall) {
         $("#llx_netinstall_setnetinstall_unattended").removeAttr("disabled");
      }
      else {
         if (self.unattended_netinstall) $("#llx_netinstall_setnetinstall_unattended").click();
         $("#llx_netinstall_setnetinstall_unattended").attr("disabled", "disabled");
         
         $("#llx_netinstall_setnetinstall_user").attr("disabled", "disabled");
         $("#llx_netinstall_setnetinstall_pass").attr("disabled", "disabled");
         $("#llx_netinstall_setnetinstall_pass_root").attr("disabled", "disabled");
      }
      
      $.material.init();
   
      });
   
   $("#llx_netinstall_setnetinstall_unattended").off("click");
   $("#llx_netinstall_setnetinstall_unattended").on("click", function(){
      
      self.unattended_netinstall=!self.unattended_netinstall;
      
      //console.log(self.unattended_netinstall);
      if(self.unattended_netinstall) {
         $("#llx_netinstall_setnetinstall_user").removeAttr("disabled");
         $("#llx_netinstall_setnetinstall_pass").removeAttr("disabled");
         $("#llx_netinstall_setnetinstall_pass_root").removeAttr("disabled");
      }
      else {
         $("#llx_netinstall_setnetinstall_user").attr("disabled", "disabled");
         $("#llx_netinstall_setnetinstall_pass").attr("disabled", "disabled");
         $("#llx_netinstall_setnetinstall_pass_root").attr("disabled", "disabled");
      }
      
      $.material.init();
   
      });
     
   // 
   $("#llx_netinstall_apply_config").off("click");
   $("#llx_netinstall_apply_config").on("click", function(){
      //alert(self.netinstall);
      //alert(self.unattended_netinstall);
      
      var  username=($("#llx_netinstall_setnetinstall_user").val());
      var  password=($("#llx_netinstall_setnetinstall_pass").val());
      var  rootpassword=($("#llx_netinstall_setnetinstall_pass_root").val());

      if (self.unattended_netinstall){
        if (! username || !password || !rootpassword){
            msg=self._("llx_netinstall_no_user");
            Utils.msg(msg, MSG_ERROR);
            return false;
        }
      }

      var credentials=[sessionStorage.username, sessionStorage.password];
      var n4dclass="NetinstallManager";
      var n4dmethod="setNetinstall";

      var arglist=[self.netinstall.toString(), self.unattended_netinstall.toString(), self.netinstall_stats.toString(), self.nongplapps.toString()];
      console.log('Setting netinstall '+arglist);
      var test=arglist;
      self.set_nongplapps(self.nongplapps);
      
      
      Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
         
         // caldria comprovar si retorna ok...
         try{
         if (response!==null && (response.status)=="true"){
         
            var credentials=[sessionStorage.username, sessionStorage.password];
            var n4dclass="NetinstallManager";
            var n4dmethod="setNetinstallUnattended";
            var arglist=[self.unattended_netinstall, username, password,rootpassword];
               
               
               Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
                  if (response!==null && (response.status)=="true"){
                     msg=self._("llx_netinstall_success");
                     Utils.msg(msg, MSG_SUCCESS);}
                  else {
                     msg=self._("llx_netinstall_error")+response.msg;
                     Utils.msg(msg, MSG_ERROR);
                  }
               });
         } else {
            msg=self._("llx_netinstall_error")+response.msg;
            Utils.msg(msg, MSG_ERROR);
         }
         
         
         
      
      }catch(exception){
           msg=self._("llx_netinstall_error")+exception;
           Utils.msg(msg, MSG_ERROR);
         }
         
         
      });
      
      });
   
};

LlxNetinstall.prototype.showMirrorUnavailable=function showMirrorUnavailable(){
       var self=this;
       
       msg="<h4>"+self._("llx_netinstall_mirror_unavailable")+"</h4>";
       $("#llx_netinstall_config").append(msg);
}

LlxNetinstall.prototype.checkMirrorAvailable=function checkMirrorAvailable(){
 
   var self=this;
   var credentials="";
   var n4dclass="MirrorManager";
   var n4dmethod="is_mirror_available";
   var arglist="";
      
   Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
     if(response.status){
        self.getNetinstallConfig();
     } else {
        self.showMirrorUnavailable();
     }
   });
}


var netInstall=new LlxNetinstall();
//$("body").css("background","#ffffff");
//alert(document.getElementsByTagName("body"));
$(document).on("moduleLoaded", function(e, args){
    var moduleName="lliurex-netinstall";
    //console.log(args["moduleName"]);
    if(args.moduleName===moduleName){
      // First of all check if mirror is available
      netInstall.checkMirrorAvailable();
    }
});





