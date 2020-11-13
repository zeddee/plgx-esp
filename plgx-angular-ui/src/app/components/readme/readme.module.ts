import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ReadmeRoutingModule } from './readme-routing.module';
import { ReadmeComponent } from './readme.component';
import { GlobalModule } from '../../global/global.module';


@NgModule({
  declarations: [ReadmeComponent],
  imports: [
    CommonModule,
    ReadmeRoutingModule,
    GlobalModule
  ]
})
export class ReadmeModule { }
