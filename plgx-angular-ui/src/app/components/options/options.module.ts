import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { OptionsRoutingModule } from './options-routing.module';
import { OptionsComponent } from './options.component';
import { GlobalModule } from '../../global/global.module';
import { NgJsonEditorModule } from 'ang-jsoneditor';


@NgModule({
  declarations: [OptionsComponent],
  imports: [
    CommonModule,
    OptionsRoutingModule,
    GlobalModule,
    NgJsonEditorModule
  ]
})
export class OptionsModule { }
