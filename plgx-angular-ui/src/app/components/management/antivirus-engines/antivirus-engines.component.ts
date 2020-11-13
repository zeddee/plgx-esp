import { Component, OnInit } from '@angular/core';
import { CommonapiService } from '../../../dashboard/_services/commonapi.service';
import { CommonVariableService } from '../../../dashboard/_services/commonvariable.service';
import Swal from 'sweetalert2';
import { Location } from '@angular/common';
import { Title } from '@angular/platform-browser';


@Component({
  selector: 'app-antivirus-engines',
  templateUrl: './antivirus-engines.component.html',
  styleUrls: ['./antivirus-engines.component.css','./antivirus-engines.component.scss']
})
export class AntivirusEnginesComponent implements OnInit {
 av_engines_data={};
 apikey_data:any;
  constructor(
    private commonapi: CommonapiService,
    private commonvariable: CommonVariableService,
    private _location: Location,
    private titleService: Title,
  ) { }

  ngOnInit() {
    this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Antivirus-Engines");
    this.commonapi.getAntiVirusEngines().subscribe((res: any) => {
        $('.hide_av_engines_data').hide();
        if( res.data.min_match_count && res.data.av_engines){
          $('.show_av_engines_data').show();
        }else{
          $('.no_data').append('No data Present')
        }
      this.av_engines_data['min_match_count']=res.data.min_match_count
      this.av_engines_data['av_engines']=res.data.av_engines
    })
  }

  get_changed_data(data){
    this.av_engines_data['av_engines']=data
  }

  onSubmit(){
    this.commonapi.Apikey_data().subscribe(res => {
      this.apikey_data = res;
      console.log(this.apikey_data);
      if(this.apikey_data.data ==undefined){
        Swal.fire({
          text: "Virustotal key is not configured. Please configure it and retry",
          })
      }
      else{
        this.update()
      }

    })
  }

update(){
  if(this.av_engines_data['min_match_count'] <=0){
    Swal.fire({
      text: "Please provide minimum count greater than or equal to 1",
      })
  }else{
  Swal.fire({
    title: 'Are you sure want to update?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#518c24',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, Update!'
  }).then((result) => {
    if (result.value) {
  this.commonapi.postAntiVirusEngines(this.av_engines_data).subscribe((res: any) => {
    if(res.status=='success'){
      Swal.fire({
        icon: 'success',
        title:"Successfully updated",
        showConfirmButton: false,
        timer: 1500,
        })
    }else{
      Swal.fire({
        icon: 'warning',
        title: res.status,
        text: res.message,
        showConfirmButton: false,
        timer: 2000

      })
    }
  })
}
})
}
}

goBack(){
  this._location.back();
}
}
