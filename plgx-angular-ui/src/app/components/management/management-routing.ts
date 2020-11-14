import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { ConfigureEmailComponent } from './configure-email/configure-email.component';
import { IntelKeysComponent } from './intel-keys/intel-keys.component';
import { ManagementComponent } from './management.component';
import { ResolvedAlertsComponent } from './resolved-alerts/resolved-alerts.component';
import { ConfigurationSettingsComponent } from './configuration-settings/configuration-settings.component';
import { AntivirusEnginesComponent } from './antivirus-engines/antivirus-engines.component';
import { HostDisableComponent } from './host-disable/host-disable.component';


const routes: Routes = [
    {
        path: '',
        children: [
            // { path: '', redirectTo: 'login', pathMatch: 'full' },
            {
                path: 'change-password',
                component: ChangePasswordComponent
            },
            {
                path: 'configure-email',
                component: ConfigureEmailComponent
            },
            {
                path: 'intel-keys',
                component: IntelKeysComponent
            },
            {
                path: 'resolved-alerts',
                component: ResolvedAlertsComponent
            },
            {
                path: 'configuration-settings',
                component: ConfigurationSettingsComponent
            },

            {
                path: 'antivirus-engines',
                component: AntivirusEnginesComponent
            },
            {
                path: 'removed-hosts',
                component: HostDisableComponent,           
              }
        ]
    }


]

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class ManagementRoutingModule { }
