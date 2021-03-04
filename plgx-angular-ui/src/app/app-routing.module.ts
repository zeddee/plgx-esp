import { NgModule } from '@angular/core';
import { Routes, RouterModule,  } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { GlobalComponent } from './global/global.component';
import {AuthGuard}  from './_helpers/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'authentication',
    pathMatch: 'full'
  },
  {
    path: 'authentication',
    loadChildren: () => import('./authentication/authentication.module').
      then(m => m.AuthenticationModule)
  },
  {
    path: '',
    component: GlobalComponent,
    canActivate: [AuthGuard],
    children: [{
      path: 'manage', loadChildren: () => import('./dashboard/dashboard.module').
        then(m => m.DashboardModule),
    },
    {
      path: 'hosts', loadChildren: () => import('./components/hosts/hosts.module').
        then(m => m.HostsModule),
    },
    {
      path: 'management', loadChildren: () => import('./components/management/management.module').
        then(m => m.ManagementModule),
    },
    {
      path: 'alerts', loadChildren: () => import('./components/alerts/alerts.module').
        then(m => m.AlertsModule),
    },
    {
      path: 'live-queries', loadChildren: () => import('./components/live-queries/live-queries.module').
        then(m => m.LiveQueriesModule),
    },
    {
      path: 'ioc', loadChildren: () => import('./components/ioc/ioc.module').
        then(m => m.IocModule),
    },
    {
      path: 'rules', loadChildren: () => import('./components/rule/rule.module').
        then(m => m.RuleModule),
    },
    {
      path: 'tag', loadChildren: () => import('./components/tag/tag.module').
        then(m => m.TagModule),
    },
    {
      path: 'carves', loadChildren: () => import('./components/carves/carves.module').
        then(m => m.CarvesModule),
    },
    {
      path: 'config', loadChildren: () => import('./components/config/config.module').
        then(m => m.ConfigModule),
    },
    {
      path: 'hunt', loadChildren: () => import('./components/hunt/hunt.module').
        then(m => m.HuntModule),
    },
    {
      path: 'options', loadChildren: () => import('./components/options/options.module').
        then(m => m.OptionsModule),
    },
    {
      path: 'packs', loadChildren: () => import('./components/packs/packs.module').
        then(m => m.PacksModule),
    },
    {
      path: 'queries', loadChildren: () => import('./components/queries/queries.module').
        then(m => m.QueriesModule),
    },
    {
      path: 'readme', loadChildren: () => import('./components/readme/readme.module').
        then(m => m.ReadmeModule),
    },
    {
      path: 'search', loadChildren: () => import('./components/search/search.module').
        then(m => m.SearchModule),
    },
    {
      path: 'yara', loadChildren: () => import('./components/yara/yara.module').
        then(m => m.YaraModule),
    },
    {
      path: 'pagenotfound', loadChildren: () => import('./components/pagenotfound/pagenotfound.module').
        then(m => m.PagenotfoundModule),
    },
    {
      path: '**',
      loadChildren: () => import('./components/pagenotfound/pagenotfound.module').
        then(m => m.PagenotfoundModule),
    },
      // {
      //   path: '',
      //   component: GlobalComponent,
      //   children: [
      //     { path: 'change-password', loadChildren: './components/management/management.module#ManagementModule' },
      //   ]
      // }

    ]
  },
  {
    path: '**',
    redirectTo: 'authentication',
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
