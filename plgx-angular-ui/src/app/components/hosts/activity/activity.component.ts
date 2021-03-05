import { AfterViewInit, Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Subject } from 'rxjs';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { CommonapiService } from '../../../dashboard/_services/commonapi.service';
import { CommonVariableService } from '../../../dashboard/_services/commonvariable.service';
// import { DataTablesModule } from 'angular-datatables';
import { DataTableDirective } from 'angular-datatables';
import { environment } from '../../../../environments/environment';
import { Location } from '@angular/common';
import { saveAs } from 'file-saver';
import { Title } from '@angular/platform-browser';
class DataTablesResponse {
  data: any[];
  draw: number;
  recordsFiltered: number;
  recordsTotal: number;
}
@Component({
  selector: 'app-activity',
  templateUrl: './activity.component.html',
  styleUrls: ['./activity.component.css']
})
export class ActivityComponent implements AfterViewInit, OnDestroy, OnInit {
  myjson: any = JSON;
  id: any;
  sub: any;
  activitydata: any;
  nodes: any;
  activitynode: any;
  nodesdata: any;
  searchText: any;
  activitycount: any;
  errorMessage:any;
  activitydatanode: any;
  defaultData: boolean;
  queryname: any;
  selectedItem: any;
  host_identifier: any;
  recentactivitydata: any;
  export_csv_data: any = {}
  query_name: any;
  click_queryname:any;
  activitysearch:any;
  @ViewChild(DataTableDirective, { static: false })
  dtElement: DataTableDirective;
  dtOptions: any = {};
  dtTrigger: Subject<any> = new Subject();
  constructor(
    private _Activatedroute: ActivatedRoute,
    private commonapi: CommonapiService,
    private commonvariable: CommonVariableService,
    private http: HttpClient,
    private _location: Location,
    private titleService: Title,
    private router: Router,

  ) { }

  ngOnInit(): void {

    this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Hosts");

    // localStorage.removeItem('activity_nodekey');
    this.sub = this._Activatedroute.paramMap.subscribe(params => {
      this.getFromActivityData();
      this.id = params.get('id');
     this.commonapi.host_name_api(this.id).subscribe(res => {
        this.activitydata = res;
        if(this.activitydata.status == "failure"){
          this.pagenotfound();
        }
        else{
        this.host_identifier = this.activitydata.data.host_identifier
        if (this.activitydata.data.id == this.id) {
          this.nodes = this.activitydata.data.node_info.computer_name;
        }
      }
      });

      this.commonapi.recent_activity_count_api(this.id).subscribe(res => {
        this.nodesdata = res;
        this.activitynode = this.nodesdata.data;
        this.click_queryname=this.activitynode[0].name
        this.query_name=this.activitynode[0].name;
        this.activitycount = Object.keys(this.activitynode).length;
        this.searchText;
        this.defaultData=true;
        this.getFromActivityData();
        this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
          dtInstance.destroy();
          this.dtTrigger.next();
        });


      });

    });
  }

  pagenotfound() {
      this.router.navigate(['/pagenotfound']);
  }

  getFromActivityData() {
    this.dtOptions = {
      pagingType: 'full_numbers',
      pageLength: 10,
      scrollX: false,
      scrollY: 480,
      serverSide: true,
      processing: true,
      searching: true,
      "language": {
        "search": "Search: "
      },
      ajax: (dataTablesParameters: any, callback) => {
        let node_id = this.id;
        var body = dataTablesParameters;
        body['limit'] = body['length'];
        body['node_id'] = node_id;
        if (!this.query_name && !this.queryname){
          return;
        }
        if (this.defaultData) {
          body['query_name'] = this.query_name;
          this.selectedItem = this.query_name;
          this.queryname = this.query_name;

        } else {
          body['query_name'] = this.queryname;
        }
        if(body.search.value!= ""  &&  body.search.value.length>=1)
        {
          body['searchterm']=body.search.value;
        }
        if(body['searchterm']==undefined){
          body['searchterm']="";
        }

        this.http.post<DataTablesResponse>(environment.api_url + "/hosts/recent_activity", body, {headers: { 'Content-Type': 'application/json','x-access-token': localStorage.getItem('JWTkey')}}).subscribe(res => {
          this.recentactivitydata = res;
          this.activitydatanode = this.recentactivitydata.data.results;
          for(const id in this.activitynode){
            if(this.activitynode[id].name==this.queryname){
              this.activitynode[id].count=res.data['total_count']
            }
          }
          for (var v = 0; v < this.activitydatanode.length; v++) {
            if (this.activitydatanode[v].columns != '') {
              this.activitydatanode[v].columns = this.activitydatanode[v].columns;
            }
          }
          if(this.activitydatanode.length >0 &&  this.activitydatanode!=undefined)
            {
              $('.dataTables_paginate').show();
              $('.dataTables_info').show();
            }
            else{
              this.activitydatanode=null;
              if(body.search.value=="" || body.search.value == undefined)
              {
                this.errorMessage="No Data Found";
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
        });
      },
      ordering: false,
      columns: [{ data: 'columns' }]
    };
  }
  action(event): void {
    event.stopPropagation();
  }
  ngAfterViewInit(): void {
    this.dtTrigger.next();
  }

  ngOnDestroy(): void {
    this.dtTrigger.unsubscribe();
  }

  getByActivityId(event, newValue, qryname, node_id): void {
   if(this.click_queryname==qryname){

   }else{
    this.selectedItem = newValue;
    this.queryname = qryname;
    this.defaultData = false;
    this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
      dtInstance.destroy();
      this.dtTrigger.next();
    });
    this.click_queryname=qryname;
  }
  }
  get_csv_data(host_identifier, queryname) {
    this.export_csv_data["host_identifier"] = host_identifier;
    this.export_csv_data["query_name"] = queryname;
    this.commonapi.recent_activity_search_csv_export(this.export_csv_data).subscribe(blob => {
      saveAs(blob, queryname+"_"+host_identifier+'.csv');

    })
  }
  goBack() {
    this._location.back();
  }
}
