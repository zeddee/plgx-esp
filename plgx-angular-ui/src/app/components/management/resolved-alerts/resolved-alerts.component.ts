import {AfterViewInit, Component, OnDestroy, OnInit, QueryList, ViewChild, ViewChildren} from '@angular/core';
import {DataTableDirective} from 'angular-datatables';
import {Subject} from 'rxjs';
import {HttpClient, HttpResponse} from '@angular/common/http';
import {CommonapiService} from '../../../dashboard/_services/commonapi.service';
import { CommonVariableService } from '../../../dashboard/_services/commonvariable.service';
import {JsonEditorComponent, JsonEditorOptions} from 'ang-jsoneditor';
import {Datatablecolumndefs} from '../../../dashboard/_helpers/datatable-columndefs';
import {environment} from '../../../../environments/environment';
import { Title } from '@angular/platform-browser';
import swal from 'sweetalert'
declare var $: any;
import 'datatables.net';


class DataTablesResponse {
  data: any[];
  draw: number;
  recordsFiltered: number;
  recordsTotal: number;
}
@Component({
  selector: 'app-resolved-alerts',
  templateUrl: './resolved-alerts.component.html',
  styleUrls: ['./resolved-alerts.component.css']
})
export class ResolvedAlertsComponent implements AfterViewInit, OnDestroy, OnInit {
  @ViewChild(JsonEditorComponent, {static: true}) editor: JsonEditorComponent;
  public editorOptions: JsonEditorOptions;
  alertSource: any;
  virusTotalCount: number;
  IBMForceTotalCount: number;
  AlientTotalVault: number;
  IOCTotalCount: number;
  RuleTotalCount: number;
  alertSourceData = {};
  alerted_data_json: any;
  alert_title: any;
  errorMessage= {  };
  all_options = {};
  title = 'Angular 7 CheckBox Select/ Unselect All';
  masterSelected = {};
  checklist = {};
  checkedList = {};
  dtTrigger: Subject<any>[] = [];
  @ViewChildren(DataTableDirective)
  dtElements: QueryList<DataTableDirective>;
  contentEditable = false;
  activeAlerts: any;
  fetched = {};
  aggregated_data:any={};
  alert_selectedItem:any;
  aggregate_tab=[];
  constructor(
    private commonapi: CommonapiService,
    private commonvariable: CommonVariableService,
    private http: HttpClient,
    private titleService: Title,
    private columndefs:Datatablecolumndefs,
  ) {

  }
  toggle: boolean = false;
  ngOnInit() {
    $.fn.dataTable.ext.errMode = 'none';
    this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Resolved Alerts");
    this.commonapi.alerts_source_count_api_resolved().subscribe((res: any) => {
      var alerttype = ['rule', 'virustotal','ioc', 'alienvault', 'ibmxforce']
      var sort_alert_type = []
      for (const name in alerttype) {
        for (const alert in res.data.alert_source) {

          if (alerttype[name] == res.data.alert_source[alert].name) {
            sort_alert_type.push(res.data.alert_source[alert]);
          }
        }
      }
      this.alertSource = sort_alert_type;
      var active_souce=this.alertSource[0].name;
      if (this.activeAlerts != null && this.activeAlerts != '' && this.activeAlerts != undefined &&  this.alertSource.find(x => x.name == this.activeAlerts)!=undefined) {
        active_souce = this.alertSource.find(x => x.name == this.activeAlerts).name;
      }
      if (this.alertSource.length > 0) {
        for (let i = 0; i < this.alertSource.length; i++) {

          if (this.alertSource[i].name == "virustotal") {
            this.virusTotalCount = this.alertSource[i].count;
          }
          if (this.alertSource[i].name == "ibmxforce") {
            this.IBMForceTotalCount = this.alertSource[i].count;
          }
          if (this.alertSource[i].name == "alienvault") {
            this.AlientTotalVault = this.alertSource[i].count;
          }
          if (this.alertSource[i].name == "ioc") {
            this.IOCTotalCount = this.alertSource[i].count;
          }
          if (this.alertSource[i].name == "rule") {
            this.RuleTotalCount = this.alertSource[i].count;
          }
        }
      }
      for (let i = 0; i < this.alertSource.length; i++) {
          this.getAlertData(this.alertSource[i].name);
      }
      setTimeout(() => {

        this.show_hide_div(active_souce);

      }, 300);
    })

  }

  get_options(source) {
    var that=this;
    return {
      pagingType: 'full_numbers',
      pageLength: 10,
      serverSide: true,
      processing: true,
      searching: true,
      destroy: true,
      "language": {
        "search": "Search: "
      },
      ajax: (dataTablesParameters: any, callback) => {
        var body = dataTablesParameters;
        body['limit'] = body['length'];
        body['source'] = source;
        var searching=false;
        if (body.search.value != "" && body.search.value.length >= 1) {
          body['searchterm'] = body.search.value;
          searching=true;
        }

        if (body['searchterm'] == undefined) {
            body['searchterm'] = "";
        }
        body['resolved'] = true;
        this.http.post<DataTablesResponse>(environment.api_url + "/alerts", body, {
          headers: {
            'Content-Type': 'application/json',
            'x-access-token': localStorage.getItem('JWTkey')
          }
        }).subscribe(res => {
          this.checklist[source] = [];
          if(res.data.hasOwnProperty("total_count")){
          if (source == "virustotal") {
            this.virusTotalCount = res.data['total_count'];
          }
          if (source == "ibmxforce") {
            this.IBMForceTotalCount = res.data['total_count'];
          }
          if (source == "alienvault") {
            this.AlientTotalVault = res.data['total_count'];
          }
          if (source == "ioc") {
            this.IOCTotalCount = res.data['total_count'];
          }
          if (source == "rule" ) {
            this.RuleTotalCount = res.data['total_count'];
          }
          }
          if (res.data['count'] > 0 && res.data['results'] != undefined) {
            this.alertSourceData[source] = res.data['results'];
            this.masterSelected[source] = false;
            for (const i in this.alertSourceData[source]) {
              let checkboxdata = {}
              checkboxdata['id'] = this.alertSourceData[source][i].id;
              checkboxdata['isSelected'] = false
              this.checklist[source].push(checkboxdata);
            }
            this.getCheckedItemList(source);

            // $("#DataTables_Table_0_info").
            $('#'+source+'_table_paginate').show();
            $('#'+source+'_table_info').show();


            this.errorMessage[source] = ''
          } else {

            if (!searching) {
              if((source == "virustotal" && this.virusTotalCount > 0 )
                 || (source == "ibmxforce" && this.IBMForceTotalCount > 0 )
                 || (source == "alienvault" && this.AlientTotalVault > 0 )
                 || (source == "ioc" && this.IOCTotalCount > 0 )
                 || (source == "rule" && this.RuleTotalCount > 0 )
                ){
                this.errorMessage[source] = "No alerts found for the selected duration";
              }
              else{
                this.errorMessage[source] = "No alerts found";
              }

              $('#'+source+'_table_paginate').hide();
              $('#'+source+'_table_info').hide();
            } else {
              this.errorMessage[source] = "No Data";
              $('#'+source+'_table_paginate').hide();
              $('#'+source+'_table_info').hide();
            }
          }
          callback({
            recordsTotal: res.data['total_count'],
            recordsFiltered: res.data['count'],
            data: []
          });
        });
      },
      ordering: false,
      columns: [{data: 'hostname'}]
    }
  }
getAlertData(source) {
    if(this.dtTrigger[source] == undefined) {
      this.dtTrigger[source] = new Subject<any>();
    }
    this.all_options[source] = this.get_options(source);
  }

  ngAfterViewInit(): void {
  }

  ngOnDestroy(): void {
  }

  /*  Alerted Entry Json Editor Start*/
  showdata(any, title) {
    this.alert_title = title;

    this.toggle = false;
    setTimeout(() => {
      this.editorOptions = new JsonEditorOptions();
      this.editorOptions.mode = 'view';
      this.alerted_data_json = any;
      this.toggle = true;
    }, 100);
  }

  /*  Alerted Entry Json Editor End*/
  checkUncheckAll(source) {
    for (var i = 0; i < this.checklist[source].length; i++) {
      this.checklist[source][i].isSelected = this.masterSelected[source];
    }
    this.getCheckedItemList(source);
  }


  isAllSelected(source) {
    this.masterSelected[source] = this.checklist[source].every(function (item: any) {
      return item.isSelected == true;
    })
    this.getCheckedItemList(source);
  }

  getCheckedItemList(source) {
    this.checkedList[source] = [];
    for (var i = 0; i < this.checklist[source].length; i++) {
      if (this.checklist[source][i].isSelected)
        this.checkedList[source].push(this.checklist[source][i].id);
    }
  }

  unresolveAlert(AlertId,source) {
    let unresolve_alets_data={}
    unresolve_alets_data["resolve"]=false
    unresolve_alets_data['alert_ids']=AlertId
    swal({
      title: 'Are you sure?',
      text: "Want to unresolve the alert!",
      icon: 'warning',
      buttons: ["Cancel","Yes,UnResolve"],
      dangerMode: true,
      closeOnClickOutside: false,
    }).then((willDelete) => {
      if (willDelete) {
        this.commonapi.AlertsResolve(unresolve_alets_data).subscribe(res => {
          if (res['status'] == "success") {
          swal({
            icon: 'success',
            title: 'UnResolved',
            text: 'Alert has been successfully UnResolved',
            buttons: [false],
            timer: 2000
          })
        }else {
          swal({
            icon: "warning",
            text: res['message'],
            buttons: [true],
          })
        }
          setTimeout(() => {
            this.dtTrigger[source].next();
          }, 1000);
        })
      }
    })
  }

  unresolvedAllSelected(source){
   let unresolve_alets_data={}
   unresolve_alets_data["resolve"]=false
   unresolve_alets_data['alert_ids']=this.checkedList[source]
    if(this.checkedList[source].length==0){
    } else{
      swal({
        title: 'Are you sure?',
              text: "Want to unresolve the alerts!",
              icon: 'warning',
              buttons: ["Cancel", "Yes,UnResolve"],
              dangerMode: true,
              closeOnClickOutside: false,
        }).then((willDelete) => {
        if (willDelete) {
          this.commonapi.AlertsResolve(unresolve_alets_data).subscribe(res => {
            if (res['status'] == "success") {
              swal({
                icon: 'success',
                title: 'UnResolved',
                text: 'Alerts has been successfully UnResolved',
                buttons: [false],
                timer: 2000
              })
            } else {
              swal({
                icon: "warning",
                text: res['message'],
                buttons: [true],
              })
            }
        })
      setTimeout(() => {
        this.dtTrigger[source].next();
      }, 1000);

        }
        })
  }
  }

  toggleDisplay(source) {
    this.fetched[source] = true;
    this.dtTrigger[source].next();
    }
    show_hide_div(name: any) {
      $('.nav-link-active').removeClass("active");
      $('#' + name).addClass("active");
      $('.alert_source_div').hide();
      $('#div_' + name).show();
      $('.no_data').hide();
      if (this.fetched[name] != true) {
        this.toggleDisplay(name);
      }
    }
    // Start Aggregated alerts
get_alerts_aggregated_data(id){
  this.aggregated_data={}
  this.aggregate_tab = [];
  this.commonapi.get_alerts_aggregated_data(id).subscribe((res: any) => {
   for(const i in res.data){
     if (!this.aggregated_data.hasOwnProperty(res.data[i].name)){
      this.aggregated_data[res.data[i].name]=[]
      this.aggregate_tab.push(res.data[i].name)
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
            // var counter = 0;
            // keys.forEach(function (key) {
            //   counter++;
            //   columns.push({
            //     data: key,
            //     title: key
            //   });
            // });
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
            "language": {
              "search": "Search: "
            },
            "initComplete": function (settings, json) {
              div_table.wrap("<div style='overflow:auto; width:100%;position:relative;'></div>");
            },
            "columnDefs":column_defs,
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


}
