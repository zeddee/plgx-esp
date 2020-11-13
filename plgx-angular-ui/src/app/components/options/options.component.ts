import { Component, ViewChild } from '@angular/core';
import { JsonEditorComponent, JsonEditorOptions } from 'ang-jsoneditor';
import { CommonapiService } from '../../dashboard/_services/commonapi.service';
import { Location } from '@angular/common';
// import { timer } from 'rxjs'
import swal from 'sweetalert';

@Component({
selector: 'app-options',
templateUrl: './options.component.html',
styleUrls: ['./options.component.css']
})

export class OptionsComponent {
  @ViewChild(JsonEditorComponent, { static: true }) editor: JsonEditorComponent;
  public editorOptions: JsonEditorOptions;
  options = new JsonEditorOptions();
  submitted = false;
  Updated = false;
  // public options:any;
  public options_data: any;
  public data = {};
  updateQueryObj = [];
  public result: any;
  error: any;
  public json_data: any = {};

  constructor(
    private commonapi: CommonapiService,
    private _location: Location
  ) {
    this.options.mode = 'code';
    this.options.modes = ['code','text', 'tree', 'view'];
    this.options.onChange = () => this.json_data['option'] = this.editor.get()
  }
  
  toggle: boolean = false;

  ngOnInit() {
    this.toggle = false;
    setTimeout(() => {
      this.commonapi.options_api().subscribe((res: any) => {
        this.options_data = res;
        this.editorOptions = new JsonEditorOptions();
        this.editorOptions.mode = 'code';
        this.editorOptions.modes = ['code','text', 'tree', 'view'];
        this.editorOptions.statusBar = false;

        this.data = this.options_data.data;
        this.json_data['option'] = this.data;
        this.toggle = true;
      });
    }, 100);
  }

  public setTreeMode() {
    this.editor.setMode('tree');
  }

  onSubmit() {
    this.commonapi.options_upload(this.json_data).subscribe(res => {
      this.result = res;
      if (this.result && this.result.status === 'failure') {
        swal({
          icon: 'warning',
          title: "Failure",
          text: this.result.message,
        })
      } else {
        swal({
          icon: 'success',
          title: 'Success',
          text: this.result.message,
          buttons: [false],
          timer: 2000
        })
        this.error = null;
        this.Updated = true;
      }
      setTimeout(() => {
        this.ngOnInit()
        // location.reload();
      }, 2000);
    },
    error => {
      console.log(error);
    })
  }
  goBack() {
    this._location.back();
  }
}
