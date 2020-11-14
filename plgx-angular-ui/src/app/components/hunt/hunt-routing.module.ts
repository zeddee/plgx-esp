import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HuntComponent } from './hunt.component';


const routes: Routes = [
  {
    path: '',
    component: HuntComponent, 
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class HuntRoutingModule { }
