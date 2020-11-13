import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CarvesComponent } from './carves.component';

describe('CarvesComponent', () => {
  let component: CarvesComponent;
  let fixture: ComponentFixture<CarvesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CarvesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CarvesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
