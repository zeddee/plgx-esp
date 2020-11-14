import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CarvesComponent } from './carves.component';


const routes: Routes = [
  {
    path: '',
    component: CarvesComponent, 
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CarvesRoutingModule { }
