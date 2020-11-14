import { AfterViewInit,OnDestroy,Component, OnInit,ViewChild } from '@angular/core';
import { CommonapiService } from '../../dashboard/_services/commonapi.service';
import swal from 'sweetalert';
import { Location } from '@angular/common';
import { saveAs } from 'file-saver';
// declare var $ :any;
import 'datatables.net';
import { DataTableDirective } from 'angular-datatables';
import { Subject } from 'rxjs';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { environment } from '../../../environments/environment'

// import {PopoverModule} from "ngx-smart-popover";
class DataTablesResponse {
  data: any[];
  draw: number;
  recordsFiltered: number;
  recordsTotal: number;
}

class carves_data {
  hostname: string;
  Session: string;
  created_at: string;
  File:any;
  Blocks_Acquired:any
  Status:any;
  Carve_Size:any;
  Delete:string;
}



@Component({
  selector: 'app-carves',
  templateUrl: './carves.component.html',
  styleUrls: ['./carves.component.css']
})
export class CarvesComponent implements AfterViewInit, OnInit {
  @ViewChild(DataTableDirective, {static: false})
  dtElement: DataTableDirective;
  dtTrigger: Subject<any> = new Subject();
  carves_val:any;
  carves_data:any;
  carves_delete:any;
  DownloadCarvesid:any;
  carves_download:any;
  errorMessage:any;
  byte_value: number;
  Progress_value:number = 0;
  dtOptions: DataTables.Settings = {};
   constructor(
    private commonapi:CommonapiService,
    private _location: Location,
    private http: HttpClient,
  ) { }

  ngOnInit() {
    $('.carves_result').hide()
    // this.getFromAlertData();
    // this.commonapi.carves_api().subscribe(res => {
    //   this.carves_val = res ;
    //   this.carves_data = this.carves_val.data.results;
    //   console.log(this.carves_val);
    // });
    this.dtOptions = {
      pagingType: 'full_numbers',
      pageLength: 10,
      serverSide: true,
      processing: false,
      searching: false,
      ajax: (dataTablesParameters: any,callback) => {
      var body = dataTablesParameters;
      body['limit']=body['length'];
      if(body.search.value!= ""  &&  body.search.value.length>=1)
    {

      body['searchterm']=body.search.value;

    }

      console.log(body,"bodymm",body['searchterm'])


      if(body['searchterm']==undefined){
        body['searchterm']="";
      }
        this.http.post<DataTablesResponse>(environment.api_url+"/carves", body, { headers: { 'Content-Type': 'application/json','x-access-token': localStorage.getItem('JWTkey')}}).subscribe(res =>{

          this.carves_val = res ;
            this.carves_data = this.carves_val.data.results;

          console.log(this.carves_val)
          // this.temp_var=true;
        if(this.carves_data.length >0 &&  this.carves_data!=undefined)
        {
        this.carves_data = this.carves_val.data['results'];
          // $("#DataTables_Table_0_info").
          $('.dataTables_paginate').show();
          $('.dataTables_info').show();
          $('.dataTables_filter').show()
          $('.carves_result').show()
        }
        else{
          if(body.search.value=="" || body.search.value == undefined)
          {
            this.errorMessage="No Carves created. You may create new Carves";
          }
          else{
            this.errorMessage="No Matching Record Found";
          }

          $('.dataTables_paginate').hide();
          $('.dataTables_info').hide();
          $('.carves_result').hide()
        }
          callback({
            recordsTotal: this.carves_val.data.total_count,
            recordsFiltered: this.carves_val.data.count,
            data: []
          });
        });
      },
      ordering: false,
      columns: [{ data: 'hostname' },{ data: 'session' },{ data: 'carves_size' },{ data: 'files' },{ data: 'blocks_aquire' },{ data: 'status' },{ data: 'created_at' },{data:'delete'}],
    }


    // $('.popover-dismiss').popover({
    //   trigger: 'focus'
    // })
  }

  downloadCarve(event,carve_file_name){

    console.log(event.target);
    var DownloadCarvesid = event.target.id;
    var DownloadCarvesname = event.target.name;

  //   this.commonapi.carves_download_api(DownloadCarvesid).subscribe(blob => {
  //     saveAs(blob, carve_file_name+".tar");
  //       })

  this.commonapi.carves_download_api(DownloadCarvesid).subscribe((event)=> {
    if(event['loaded'] && event['total']){
      this.Progress_value = Math.round(event['loaded']/event['total']*100);
    }
    if(event['body'])
    {
      saveAs(event['body'], carve_file_name+".tar");
      swal("File Download Completed", {
        icon: "success",
        buttons: [false],
        timer: 2000
      });
    }
  })
  }


  /*
    This function convert bytes into carvesize format
    */

  getCarvesize(bytes){
   let sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      if (bytes == 0)
        return '0 Byte';
    this.byte_value = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, this.byte_value)) + ' ' + sizes[this.byte_value];

}
  deleteCarve(event){
        swal({
        icon: 'warning',
        title: "Are you sure?",
        text: "You won't be able to revert this!",
        buttons: ["Cancel", true],
        dangerMode: true,
      }).then((willDelete) => {
        if (willDelete) {
        var idAttr = event.target.id;
        this.commonapi.carves_delete_api(idAttr).subscribe(res => {
          this.carves_delete = res;
          swal("Carve file has been deleted successfully!", {
            icon: "success",
            buttons: [false],
            timer: 2000
          });
          setTimeout(() => {
            this.ngOnInit();
            this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
              // Destroy the table first
              dtInstance.destroy();
              // Call the dtTrigger to rerender again
              this.dtTrigger.next();
            });
          },2100);

        })
      }
})

  }
  ngAfterViewInit(): void {
    this.dtTrigger.next();
  }
  goBack(){
    this._location.back();
  }


}
