import { AfterViewInit,Component, OnInit,ViewChild ,} from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DataTableDirective } from 'angular-datatables';
import { Subject } from 'rxjs';
import {HttpClient, HttpResponse} from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import {JsonEditorComponent, JsonEditorOptions} from 'ang-jsoneditor';
import {CommonapiService} from '../../../dashboard/_services/commonapi.service';
import { Location } from '@angular/common';
import { saveAs } from 'file-saver';
import Swal from 'sweetalert2';
declare var $: any;
import 'datatables.net';
import {Datatablecolumndefs} from '../../../dashboard/_helpers/datatable-columndefs';

class DataTablesResponse {
  data: any[];
  draw: number;
  recordsFiltered: number;
  recordsTotal: number;
}
@Component({
  selector: 'app-alerts-under-rule',
  templateUrl: './alerts-under-rule.component.html',
  styleUrls: ['./alerts-under-rule.component.css']
})
export class AlertsUnderRuleComponent implements AfterViewInit,OnInit {
  @ViewChild(JsonEditorComponent, {static: true}) editor: JsonEditorComponent;
  public editorOptions: JsonEditorOptions;
id:any;
@ViewChild(DataTableDirective, {static: false})
dtElement: DataTableDirective;
dtTrigger: Subject<any> = new Subject();
alert_data:any;
alerted_data_json:any;
// dtOptions: DataTables.Settings = {};
dtOptions:any = {}
searchText:string;
errorMessage:any;
toggle: boolean = false;
masterSelected:boolean;
checklist:any;
checkedList:any;
rule_name:string;
aggregated_data:any={};
alert_selectedItem:any;
responsedata:any;
  constructor(
    private _Activatedroute: ActivatedRoute,
    private http: HttpClient,
    private commonapi: CommonapiService,
    private router: Router,
    private _location: Location,
    private columndefs: Datatablecolumndefs,
  ) { }

  ngOnInit() {
    $.fn.dataTable.ext.errMode = 'none';
    this._Activatedroute.paramMap.subscribe(params => {
      this.id = params.get('id');
    })
    this.rule_name=localStorage.getItem('rule_name')
    var that=this;
    this.dtOptions = {
      pagingType: 'full_numbers',
      pageLength: 10,
      serverSide: true,
      processing: false,
      searching: true,
      dom: '<"pull-right"B><"pull-right"f><"pull-left"l>tip',
      buttons: [
        {
          text: 'Export',
          action: function ( e, dt, node, config ) {
            that.exportAlerts(this.id);
          },
          className: 'export_button'
        }
      ],
      "language": {
        "search": "Search: "
      },
      ajax: (dataTablesParameters: any,callback) => {

        var body = dataTablesParameters;
        body['limit']=body['length'];
        if(body.search.value!= ""  &&  body.search.value.length>=1)
      {

        body['searchterm']=body.search.value;

      }
        if(body['searchterm']==undefined){
          body['searchterm']="";
        }
       body["rule_id"]=this.id
        this.http.post<DataTablesResponse>(environment.api_url + "/alerts", body, {
          headers: {
            'Content-Type': 'application/json',
            'x-access-token': localStorage.getItem('JWTkey')
          }
        }).subscribe(res => {
          this.responsedata = res;
          if(this.responsedata.status == "failure"){
            this.pagenotfound();
          }
          else{
          this.alert_data =res.data['results'];
        if(res.data['count'] > 0 && res.data['results'] != undefined)
        {
          this.checklist = [ ];
          this.masterSelected = false;
          for (const i in this.alert_data){
            let checkboxdata={}
            checkboxdata['id']=this.alert_data[i].id
            checkboxdata['isSelected']=false
              this.checklist.push(checkboxdata)
          }
          $('.dataTables_paginate').show();
          $('.dataTables_info').show();
          $('.dataTables_filter').show()
        }
        else{
          if(body.search.value=="" || body.search.value == undefined)
          {
            this.errorMessage="No Records Found";
          }
          else{
            this.errorMessage="No Matching Record Found";
          }
          $('.dataTables_paginate').hide();
          $('.dataTables_info').hide();

        }
          callback({
            recordsTotal: res.data['total_count'],
            recordsFiltered: res.data['count'],
            data: []
          });
        }
        });
      },
      ordering: false,
      columns: [{data: 'hostname'}]
    }
  }
  ngAfterViewInit(): void {
    this.dtTrigger.next();
  }
  ngOnDestroy(): void {
    this.dtTrigger.unsubscribe();
  }
    /*  Alerted Entry Json Editor Start*/
    showdata(any, title) {
      this.toggle = false;
      setTimeout(() => {
        this.editorOptions = new JsonEditorOptions();
        this.editorOptions.mode = 'view';
        this.alerted_data_json = any;
        this.toggle = true;
      }, 100);
    }

    /*  Alerted Entry Json Editor End*/

      /* Start Resolve alert*/
    resolveAlert(AlertId) {
      let resolve_alerts_data={}
      resolve_alerts_data["resolve"]=true
      resolve_alerts_data['alert_ids']=AlertId
      Swal.fire({
        title: 'Are you sure?',
        text: "Want to resolve the alert!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#518c24',
        cancelButtonColor: '#d33',
        confirmButtonText: "Yes,Resolve"
      }).then((result) => {
        if (result.value) {
          this.commonapi.AlertsResolve(resolve_alerts_data).subscribe(res => {
            if (res['status'] == "success") {
              Swal.fire({
                icon: 'success',
                title: 'Resolved',
                text: 'Alert has been successfully resolved',
                timer: 2000,
                showConfirmButton: false,
              })
            } else {
              Swal.fire({
                icon: "warning",
                text: res['message'],
              })
            }
            setTimeout(() => {
              this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
                // Destroy the table first
                dtInstance.destroy();
                // Call the dtTrigger to rerender again
                this.dtTrigger.next();
              });
        },1500);
          })

        }
      })
    }
    resolvedAllSelected() {
      let resolve_alerts_data={}
      resolve_alerts_data["resolve"]=true
      resolve_alerts_data['alert_ids']=this.checkedList
      if (this.checkedList.length == 0) {
      }
      else {
        Swal.fire({
          title: 'Are you sure?',
          text: "Want to resolve the alerts!",
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#518c24',
          cancelButtonColor: '#d33',
          confirmButtonText: "Yes,Resolve"
        }).then((result) => {
          if (result.value) {
              this.commonapi.AlertsResolve(resolve_alerts_data).subscribe(res => {
                if (res['status'] == "success") {
                  Swal.fire({
                    icon: 'success',
                    title: 'Resolved',
                    text: 'Alerts has been successfully resolved',
                    timer: 2000,
                    showConfirmButton: false,
                  })
                } else {
                  Swal.fire({
                    icon: "warning",
                    text: res['message'],
                  })
                }
            })
            setTimeout(() => {
              this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
                // Destroy the table first
                dtInstance.destroy();
                // Call the dtTrigger to rerender again
                this.dtTrigger.next();
              });
        },1500);
            }
          })
      }
      }
      /* END Resolve alert*/
      goBack() {
        this._location.back();
      }
      checkUncheckAll() {
        for (var i = 0; i < this.checklist.length; i++) {
          this.checklist[i].isSelected = this.masterSelected;
        }
        this.getCheckedItemList();
      }
      isAllSelected() {
        this.masterSelected = this.checklist.every(function(item:any) {
            return item.isSelected == true;
          })
        this.getCheckedItemList();
      }

      getCheckedItemList(){
        this.checkedList = [];
        for (var i = 0; i < this.checklist.length; i++) {
          if(this.checklist[i].isSelected)
          this.checkedList.push(this.checklist[i].id);
        }
      }

      // Start Aggregated alerts
get_alerts_aggregated_data(id){
  this.aggregated_data={}
  this.commonapi.get_alerts_aggregated_data(id).subscribe((res: any) => {
   for(const i in res.data){
     if (!this.aggregated_data.hasOwnProperty(res.data[i].name)){
      this.aggregated_data[res.data[i].name]=[]
       }
       this.aggregated_data[res.data[i].name].push(res.data[i].columns)
    }
    if(res.data.length!=0){
      this.alerts_aggregated_data(res.data[0].name)
    }else{
      $("#alerts_aggretated_table").html('No results found');
    }
  })
}
alerts_aggregated_data(key){
  this.alert_selectedItem =key
  // $('#alerts_aggretated_table').empty();
  document.getElementById("alerts_aggretated_table").innerHTML = '';
  var id="alerts_aggretated_table";
  var div_table = $("<table></table>")
      .attr("id", key + "_table")
      .attr("style", "margin-left:auto;width:100%;overflow-x: scroll")
      .attr("width", "100%;")
      .addClass("table table-striped- table-bordered  table-checkable");
        $("#"+id).append(div_table);
      let values=this.aggregated_data[key]
      var columns = [];
  var keys =  Object.keys(values[0]);

  var _result = this.columndefs.columnDefs(keys);
  var column_defs = _result.column_defs;
  columns = _result.column;
            $(document).ready(function() {
              div_table.DataTable({
              dom: "Bfrtip",
              bLengthChange:true,
              data: values,
              sPaginationType:"full_numbers",
              "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
              columns: columns,
              paging:true,
              buttons: [ {extend: 'csv',filename: function () { return key;}}],
                "columnDefs":column_defs,
                "language": {
              "search": "Search: "
            },
            "initComplete": function (settings, json) {
              div_table.wrap("<div style='overflow:auto; width:100%;position:relative;'></div>");
            },
            rowCallback: function(row, data, index){
              $('td', row).css('background-color', 'white');
            }
            });
          })

}

  // End Aggregated alerts
  close_data(){
    document.getElementById("alerts_aggretated_table").innerHTML = '';
      }
  get_csv_data(id){
    var payloadDict={"source":'rule',"rule_id":id}
      this.commonapi.rule_alerts_export(payloadDict).subscribe(blob => {
      saveAs(blob,"alert"+"_"+"rule"+'.csv');
    })
  }


/*  Export csv file for all the alert type*/
exportAlerts(id){
var payloadDict = {"source":'rule',"rule_id":id}
var alert_name = JSON.stringify(payloadDict);
var token_val = localStorage.getItem('JWTkey');
var today = new Date();
var currentDate = today.getDate()+"-"+(today.getMonth()+1)+"-"+today.getFullYear();
$.ajax({
    "url": environment.api_url+"/alerts/alert_source/export",
    "type": 'POST',
    "data": alert_name,
    headers: {
        "content-type":"application/json",
        "x-access-token": token_val
      },
    "success": function(res, status, xhr) {
      if(res.status == 'failure'){
        var csvData = new Blob([res.message], {
            type: 'text/csv;charset=utf-8;'
        });
        var csvURL = window.URL.createObjectURL(csvData);
        var tempLink = document.createElement('a');
        tempLink.href = csvURL;
        tempLink.setAttribute('download', 'alert'+'_'+payloadDict.source+ '_' + currentDate + '.csv');
        tempLink.click();
      }
      else{
        var csvData = new Blob([res], {
            type: 'text/csv;charset=utf-8;'
        });
        var csvURL = window.URL.createObjectURL(csvData);
        var tempLink = document.createElement('a');
        tempLink.href = csvURL;
        tempLink.setAttribute('download', 'alert'+'_'+payloadDict.source+ '_' + currentDate + '.csv');
        tempLink.click();
    }
      }

});
return false;
}
pagenotfound() {
    this.router.navigate(['/pagenotfound']);
}
}
