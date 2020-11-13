import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { RuleComponent } from './rule.component';
import { AddRuleComponent } from './add-rule/add-rule.component';
import { EditRuleComponent } from './edit-rule/edit-rule.component';
import { AlertsUnderRuleComponent } from './alerts-under-rule/alerts-under-rule.component';


const routes: Routes = [
  {
    path: '',
    component: RuleComponent, 
  },
  {
    path: '',
    children: [{
      path: 'add-rule', component: AddRuleComponent,
    }]
  },
  {
    path: '',
    children: [{ 
      path: ':id/edit', component: EditRuleComponent,
    }]
  },
  {
    path: '',
    children: [{
      path: ':id/alert', component: AlertsUnderRuleComponent,
    }]
  }
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class RuleRoutingModule { }
