import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurationSettingsComponent } from './configuration-settings.component';

describe('ConfigurationSettingsComponent', () => {
  let component: ConfigurationSettingsComponent;
  let fixture: ComponentFixture<ConfigurationSettingsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ConfigurationSettingsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
