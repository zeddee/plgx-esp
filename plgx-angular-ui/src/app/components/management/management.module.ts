import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ManagementComponent } from './management.component';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { ConfigureEmailComponent } from './configure-email/configure-email.component';
import { IntelKeysComponent } from './intel-keys/intel-keys.component';
import { GlobalModule } from '../../global/global.module';
import { ManagementRoutingModule} from '../management/management-routing';
import { ResolvedAlertsComponent } from './resolved-alerts/resolved-alerts.component';
import { ConfigurationSettingsComponent } from './configuration-settings/configuration-settings.component';
import { AntivirusEnginesComponent } from './antivirus-engines/antivirus-engines.component';
import { HostDisableComponent } from './host-disable/host-disable.component';
import { DataTablesModule } from 'angular-datatables';
import { NgJsonEditorModule } from 'ang-jsoneditor';
import { TagInputModule } from 'ngx-chips';

@NgModule({
  declarations: [
    ManagementComponent,
    ChangePasswordComponent,
    ConfigureEmailComponent,
    IntelKeysComponent,
    ResolvedAlertsComponent,
    ConfigurationSettingsComponent,
    AntivirusEnginesComponent,
    HostDisableComponent
  ],
  imports: [
     CommonModule,
     ManagementRoutingModule, 
     FormsModule,
     ReactiveFormsModule,
     CommonModule,
     GlobalModule,
     RouterModule,
     DataTablesModule,
     NgJsonEditorModule,
     TagInputModule
  ],
})
export class ManagementModule { }
