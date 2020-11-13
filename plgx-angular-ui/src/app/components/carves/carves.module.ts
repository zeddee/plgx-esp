import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CarvesRoutingModule } from './carves-routing.module';
import { CarvesComponent } from './carves.component';
import { GlobalModule } from '../../global/global.module';
import { DataTablesModule } from 'angular-datatables';


@NgModule({
  declarations: [CarvesComponent],
  imports: [
    CommonModule,
    CarvesRoutingModule,
    GlobalModule,
    DataTablesModule
  ]
})
export class CarvesModule { }
