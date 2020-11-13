import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { AuthenticationService } from '../../dashboard/_services/authentication.service';
import { User } from '../../dashboard/_models/user';
import { ToastrService } from 'ngx-toastr';
import {Renderer2} from '@angular/core';
import { filter } from 'rxjs/operators';
import { CommonVariableService } from '../../dashboard/_services/commonvariable.service';
@Component({
    selector: 'app-admin-aside',
    templateUrl: './admin-aside.component.html',
    styleUrls: ['./admin-aside.component.css']
})
export class AdminAsideComponent implements OnInit {
    currentUser: User;
    default_menu_name:any;
    id_for_links:any;
    Version=this.commonvariable.Version
    constructor(
        private router: Router,
        private authenticationService: AuthenticationService,
        private toastr:ToastrService,
        private titleService: Title,
        private renderer: Renderer2,
        private commonvariable: CommonVariableService,
    ) {
        this.authenticationService.currentUser.subscribe(x => this.currentUser = x);
        this.router.events.pipe(
            filter(event => event instanceof NavigationEnd)
          ).subscribe((event: NavigationEnd) => {
            if(event.url.includes('live-queries')){
                this.id_for_links = 'live-queries';
            }
          });

    }
    ngOnInit(){

        this.default_menu_name = localStorage.getItem('menu_name');
        var str = window.location.href;
        var page_name = str.substr(str.lastIndexOf('/') + 1);
        console.log(page_name)
        if(page_name == "manage"){
            this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Dashboard");
        }
        else if(page_name == "openc2"){
            this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Response Action" );
        }
        else{
            this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+ page_name );
        }
        if(this.default_menu_name !== null){
            document.getElementById(this.default_menu_name).classList.add('kt-menu__item--active');
        }else if(this.default_menu_name == null){
            document.getElementById('Dashboard').classList.add('kt-menu__item--active');
        }
        this.renderExternalScript('../../../assets/demo/default/base/scripts.bundle.js').onload = () => {
    // console.log('Google API Script loaded');
    // do something with this library
  }
    }

    action(event): void {
        event.stopPropagation();
    }


    // this function removed all localStorage key value data and redirect to login page
    logout() {
        this.toastr.success('You have successfully logged out.');
        localStorage.removeItem('currentUser');
        localStorage.removeItem('JWTkey');
        localStorage.removeItem('menu_name');
        this.router.navigate(['/']);
    }
    OnNavChange(event, id, active, rel) {
        this.id_for_links=id;
        localStorage.setItem("menu_name",id);
        this.router.events.pipe(
            filter(event => event instanceof NavigationEnd)
          ).subscribe((event: NavigationEnd) => {
            if(event.url.includes('live-queries')){
                this.id_for_links = 'live-queries';
            }
          });
          if(id === 'live-queries'){
              console.log(id)
              id = 'Live Queries';
          }else if(id === 'Action'){
            id = 'Response Action';
          }

        // document.getElementById(default_menu_name).classList.add(active);
        this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+ id.replace('-', ' ') );
        var elems = document.querySelectorAll("." + active);
        [].forEach.call(elems, function (el) { el.classList.remove(active); });
        event.target.parentElement.parentElement.classList.remove(rel);
        document.getElementById(id).classList.add(active);

        //collapse Management sub page while click other page
        var div = document.getElementById("test");
    	  div.classList.remove("show");

    }

    collapsemanagementmenu(){
      var div = document.getElementById("test");
      div.classList.remove("show");
    }


    public setTitle( newTitle: string) {

      }
      renderExternalScript(src: string): HTMLScriptElement {
        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = src;
        script.async = true;
        script.defer = true;
        this.renderer.appendChild(document.body, script);
        return script;
      }

}
var KTAppOptions = {
    "colors": {
        "state": {
            "brand": "#5d78ff",
            "metal": "#c4c5d6",
            "light": "#ffffff",
            "accent": "#00c5dc",
            "primary": "#5867dd",
            "success": "#34bfa3",
            "info": "#36a3f7",
            "warning": "#ffb822",
            "danger": "#fd3995",
            "focus": "#9816f4"
        },
        "base": {
            "label": [
                "#c5cbe3",
                "#a1a8c3",
                "#3d4465",
                "#3e4466"
            ],
            "shape": [
                "#f0f3ff",
                "#d9dffa",
                "#afb4d4",
                "#646c9a"
            ]
        }
    }
};
