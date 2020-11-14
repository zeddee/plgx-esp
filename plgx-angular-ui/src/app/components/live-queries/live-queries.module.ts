import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LiveQueriesRoutingModule } from './live-queries-routing.module';
import { LiveQueriesComponent } from './live-queries.component';
import { GlobalModule } from '../../global/global.module';
import { AceEditorModule } from 'ng2-ace-editor';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AngularMultiSelectModule } from 'angular2-multiselect-dropdown';
import { NgxSpinnerModule } from "ngx-spinner";
import { LiveSearchPipe } from './livesearch.pipe';
import { DataTablesModule } from 'angular-datatables';


@NgModule({
  declarations: [LiveQueriesComponent,LiveSearchPipe],
  imports: [
    CommonModule,
    LiveQueriesRoutingModule,
    GlobalModule,
    AceEditorModule,
    FormsModule,
    ReactiveFormsModule,
    AngularMultiSelectModule,
    NgxSpinnerModule,
    DataTablesModule,
    // TableModule
    
  ]
})
export class LiveQueriesModule { }
