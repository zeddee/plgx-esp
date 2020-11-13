import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonVariableService } from '../../dashboard/_services/commonvariable.service';
import { Location } from '@angular/common';

@Component({
  selector: 'app-readme',
  templateUrl: './readme.component.html',
  styleUrls: ['./readme.component.css']
})
export class ReadmeComponent implements OnInit {

  cpt_down:any;
  route: string;
  currentURL='';
  Version=this.commonvariable.version_in_readme_content

  constructor(
    private _Activatedroute:ActivatedRoute,
    private router: Router,
    private commonvariable: CommonVariableService,
  ) { }

  ngOnInit() {
  }

  downloadFile(e,val){
    this.currentURL = window.location.href;
    let toArray = this.currentURL.split(':');
    this.cpt_down = toArray[0] + ":" + toArray[1] + ":9000/downloads/" + val;
    // this.cpt_down = "https://13.232.172.29:9000/downloads/" + val;
    console.log("url",this.cpt_down);
    window.open(this.cpt_down,'_blank');
  }

}
